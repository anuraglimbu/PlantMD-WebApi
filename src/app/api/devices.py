from fastapi import APIRouter, Depends

from app.api.models.identifiers import IdentifierInDB
from app.auth.base import get_current_active_device

router = APIRouter()

@router.get("/me/", response_model=IdentifierInDB)
async def read_devices_me(current_device: IdentifierInDB = Depends(get_current_active_device)):
    return current_device

@router.get("/me/items/")
async def read_own_items(current_user: IdentifierInDB = Depends(get_current_active_device)):
    return [{"item_id": "Foo", "owner": current_user.identifier}]