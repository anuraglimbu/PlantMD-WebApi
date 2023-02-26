import os
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, status, Path
from fastapi.responses import FileResponse

load_dotenv()
router = APIRouter()

@router.get("/{image_name}", status_code=status.HTTP_200_OK)
async def get_image(image_name: str = Path(..., title="Name of image file to retrieve")):
    if not image_name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Must pass the name")

    path = os.path.join(os.getenv("IMAGE_FOLDER"), image_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File Not Found")
    return FileResponse(path)
    