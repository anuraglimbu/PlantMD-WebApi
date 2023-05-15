from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import base, images, inferences, token, devices
from app.database.db import engine, database
from app.database.structures import metadata

metadata.create_all(engine)

app = FastAPI(
    title="PlantMD API",
    description="API to interact with the underlying prediction model of PlantMD",
    version="v0.5.0"
)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


'''
    Establishing connection to the database when the server starts and disconnecting on shutdown
'''
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

'''
    Adding api routes
'''
app.include_router(base.router, tags=["Base"])

app.include_router(token.router, tags=["Authenticate"])

app.include_router(devices.router, prefix="/devices", tags=["Devices"])

app.include_router(inferences.router, prefix="/inferences", tags=["Inferences"])

app.include_router(images.router, prefix="/images", tags=["Images"])