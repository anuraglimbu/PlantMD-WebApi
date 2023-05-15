from app.database.db import database
from app.database.structures import inferences

from app.api.models.inferences import InferenceSchema

async def create(payload: InferenceSchema):
    query = inferences.insert().values(
        identifier = payload.identifier,
        original_filename = payload.original_filename,
        result_filename = payload.result_filename
    ).returning(inferences.c.id)
    return await database.execute(query=query)

async def get(inference_id: int):
    query = inferences.select().where(inference_id == inferences.c.id)
    return await database.fetch_one(query=query)

async def get_from_identifier(identifier: str):
    query = inferences.select().where(identifier == inferences.c.identifier)
    return await database.fetch_all(query=query)

async def get_all():
    query = inferences.select()
    return await database.fetch_all(query=query)

async def update(inference_id: int, payload: InferenceSchema):
    query = (
        inferences
        .update()
        .where(inference_id == inferences.c.id)
        .values(
            identifier = payload.identifier,
            original_filename = payload.original_filename,
            result_filename = payload.result_filename
        )
        .returning(inferences.c.id)
    )
    return await database.execute(query=query)

async def delete(inference_id: int):
    query = inferences.delete().where(inference_id == inferences.c.id)
    return await database.execute(query=query)

async def delete_from_identifier(identifier: str):
    query = inferences.delete().where(identifier == inferences.c.identifier)
    return await database.execute(query=query)