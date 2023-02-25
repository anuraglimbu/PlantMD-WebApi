from fastapi import FastAPI

from app.api import base, inference
from app.database.db import engine, database, metadata

metadata.create_all(engine)

app = FastAPI(
    title="PlantMD API",
    description="API to interact with the underlying prediction model of PlantMD",
    version="v0.1"
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

app.include_router(inference.router, prefix="/inference", tags=["Inference"])