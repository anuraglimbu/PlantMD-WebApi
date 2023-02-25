from fastapi import FastAPI

from app.api import base

app = FastAPI(
    title="PlantMD API",
    description="API to interact with the underlying prediction model of PlantMD",
    version="v0.1"
)

app.include_router(base.router)