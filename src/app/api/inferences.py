import os
import datetime
from dotenv import load_dotenv
import json
import aiofiles

from fastapi import APIRouter, File, UploadFile, Path, Depends, HTTPException, status
from prediction_model import model

from app.api.models.identifiers import IdentifierInDB
from app.auth.base import get_current_active_device

from app.api.models.inferences import InferenceSchema, InferenceResult, Inferences
from app.api.models.prediction_results import PredictionResultSchema
from app.database.crud import inferences, prediction_results

load_dotenv()
router = APIRouter()

all_treatments = json.load(open(os.getenv("TREATMENTS_JSON_FILE")))

SUPPORTED_FORMATS = [
    "application/octet-stream",
    "image/jpg",
    "image/jpeg",
    "image/png",
    #"image/heic"
]

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 50  # 50 megabytes

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER")
MODEL_CONFIG_PATH = os.getenv("MODEL_CONFIG_LOCATION")
MODEL_PATH = os.path.join(os.getenv("MODEL_LOCATION"), "model.onnx")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=InferenceResult)
async def create_inference(file: UploadFile = File(..., description="The image file to be predicted"), current_user: IdentifierInDB = Depends(get_current_active_device)):
    if not file:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Must provide a file")
    
    if file.content_type not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="This file format "+ file.content_type +" is not supported")
    
    filename = file.filename.split(".")
    extension = filename.pop()
    randomName =  str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '') + "-"  + ".".replace(' ','_')
    originalFileName = randomName + "." + extension
    resultFileName = randomName + "-result"
    
    imagePath = os.path.join(IMAGE_FOLDER, originalFileName)

    if not os.path.exists(IMAGE_FOLDER):
        os.mkdir(IMAGE_FOLDER)

    async with aiofiles.open(imagePath, "wb") as f:
        while chunk := await file.read(DEFAULT_CHUNK_SIZE):
            await f.write(chunk)

    classes, confidences = model.main(imagePath, MODEL_PATH, MODEL_CONFIG_PATH, IMAGE_FOLDER, resultFileName)
    resultFileName += ".png"

    treatments = {}
    for disease in set(classes):
        treatments.update({disease : all_treatments[disease]})

    inference = InferenceSchema(
        identifier = current_user.identifier,
        original_filename = originalFileName,
        result_filename = resultFileName
    )
    inference_id = await inferences.create(inference)
    if not inference_id:
        os.remove(os.path.join(IMAGE_FOLDER, originalFileName))
        os.remove(os.path.join(IMAGE_FOLDER, resultFileName))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save inference data")
    
    for prediction_class, confidence in zip(classes, confidences):
        prediction_result = PredictionResultSchema(
            inference_id = inference_id,
            prediction_class = prediction_class,
            confidence = confidence
        )
        prediction_result_id = await prediction_results.create(prediction_result)
        if not prediction_result_id:
            os.remove(os.path.join(IMAGE_FOLDER, originalFileName))
            os.remove(os.path.join(IMAGE_FOLDER, resultFileName))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save inference prediction results")

    response = InferenceResult(
        # type = file.content_type,
        # name = randomName,
        # extension = extension,
        original_file = originalFileName,
        classes = classes,
        confidences = confidences,
        treatments = treatments,
        result_file = resultFileName
    )
    return response


@router.get("/", status_code=status.HTTP_200_OK, response_model=Inferences)
async def read_all_inferences(current_device = Depends(get_current_active_device)):
    db_inferences = await inferences.get_all()
    return Inferences(inferences=db_inferences)


@router.get("/identifier/{identifier}", status_code=status.HTTP_200_OK, response_model=Inferences)
async def read_all_inferences_from_identifier(identifier: str = Path(..., title="Identifier of device whose inferences to retrieve"), current_device = Depends(get_current_active_device)):
    db_inferences = await inferences.get_from_identifier(identifier)
    return Inferences(inferences=db_inferences)


@router.get("/id/{inference_id}", status_code=status.HTTP_200_OK, response_model=InferenceResult)
async def read_inference_from_id(inference_id: int = Path(..., title="Id of the inference you are trying to retrieve details of"), current_device = Depends(get_current_active_device)):
    inference_result = await inferences.get(inference_id)

    if not inference_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inference not found")

    inference_prediction_results = await prediction_results.get(inference_result.id)

    classes = []
    confidences = []

    for prediction in inference_prediction_results:
        classes.append(prediction.prediction_class)
        confidences.append(prediction.confidence)

    treatments = {}
    for disease in set(classes):
        treatments.update({disease : all_treatments[disease]})

    return InferenceResult(
        original_file = inference_result.original_filename,
        classes = classes,
        confidences = confidences,
        treatments = treatments,
        result_file = inference_result.result_filename
    )


@router.delete("/identifier/{identifier}", status_code=status.HTTP_200_OK, response_model=Inferences)
async def delete_all_inferences_using_identifier(identifier: str = Path(..., title="Identifier of device whose inferences to delete"), current_device = Depends(get_current_active_device)):
    db_inferences = await inferences.get_from_identifier(identifier)
    
    for inference_result in db_inferences:
        os.remove(os.path.join(IMAGE_FOLDER, inference_result.original_filename))
        os.remove(os.path.join(IMAGE_FOLDER, inference_result.result_filename))
        await prediction_results.delete_from_inference_id(inference_id=inference_result.id)

    await inferences.delete_from_identifier(identifier=identifier)

    return Inferences(inferences=db_inferences)


@router.delete("/id/{inference_id}/", status_code=status.HTTP_200_OK, response_model=InferenceResult)
async def delete_inference_from_id(inference_id: int = Path(..., title="Id of inference to delete"), current_device = Depends(get_current_active_device)):
    inference_result = await inferences.get(inference_id)
    if not inference_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inference not found")
    
    inference_prediction_results = await prediction_results.get(inference_result.id)

    classes = []
    confidences = []

    for prediction in inference_prediction_results:
        classes.append(prediction.prediction_class)
        confidences.append(prediction.confidence)

    treatments = {}
    for disease in set(classes):
        treatments.update({disease : all_treatments[disease]})

    await inferences.delete(inference_id)
    await prediction_results.delete_from_inference_id(inference_id)

    os.remove(os.path.join(IMAGE_FOLDER, inference_result.original_filename))
    os.remove(os.path.join(IMAGE_FOLDER, inference_result.result_filename))

    return InferenceResult(
        original_file = inference_result.original_filename,
        classes = classes,
        confidences = confidences,
        treatments = treatments,
        result_file = inference_result.result_filename
    )