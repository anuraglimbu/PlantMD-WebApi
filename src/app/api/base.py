from fastapi import APIRouter

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
def pong():
    return {"status":"online"}