from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def inference():
    return {"location":"inference"}