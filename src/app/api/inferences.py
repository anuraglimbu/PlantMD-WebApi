import os
import datetime
from dotenv import load_dotenv
import aiofiles

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from prediction_model import model

from app.api.models.identifiers import IdentifierInDB
from app.auth.base import get_current_active_device

load_dotenv()
router = APIRouter()

SUPPORTED_FORMATS = [
    "image/jpeg",
    "image/png",
    #"image/heic"
]

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 50  # 50 megabytes

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER")
MODEL_CONFIG_PATH = os.getenv("MODEL_CONFIG_LOCATION")
MODEL_PATH = os.path.join(os.getenv("MODEL_LOCATION"), "model.onnx")

@router.post("/")
async def create_inference(file: UploadFile = File(..., description="The image file to be predicted"), current_user: IdentifierInDB = Depends(get_current_active_device)):
    if not file:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Must provide a file")
    
    if file.content_type not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="This file format is not supported")
    
    filename = file.filename.split(".")
    extension = filename.pop()
    randomName =  str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '') + "-"  + ".".join(filename).replace(' ','_')
    originalFileName = randomName + "." + extension
    resultFileName = randomName + "-result"

    imagePath = os.path.join(IMAGE_FOLDER, originalFileName)

    async with aiofiles.open(imagePath, "wb") as f:
     while chunk := await file.read(DEFAULT_CHUNK_SIZE):
         await f.write(chunk)

    model.main(imagePath, MODEL_PATH, MODEL_CONFIG_PATH, IMAGE_FOLDER, resultFileName)

    response_object = {
        "type": file.content_type,
        "name" : randomName,
        "extension" : extension,
        "originalFile": originalFileName,
        "resultFile": resultFileName  + ".png"
    }
    return response_object