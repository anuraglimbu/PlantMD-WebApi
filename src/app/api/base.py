from fastapi import APIRouter, Depends

from app.auth.base import get_current_active_device

router=APIRouter()

@router.get("/")
def root():
    return {
        "location":"root",
        "docs":"/docs",
        "redoc":"/redoc",
        "ping":"/ping"
    }

@router.get("/ping")
def ping(current_device = Depends(get_current_active_device)):
    return {
        "status": "online",
        "device_id": current_device.identifier
    }