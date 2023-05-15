from app.database.db import database
from app.database.structures import prediction_results

from app.api.models.prediction_results import PredictionResultSchema

async def create(payload: PredictionResultSchema):
    query = prediction_results.insert().values(
        inference_id = payload.inference_id,
        prediction_class = payload.prediction_class,
        confidence = payload.confidence
    ).returning(prediction_results.c.id)
    return await database.execute(query=query)

async def get(inference_id: int):
    query = prediction_results.select().where(inference_id == prediction_results.c.inference_id)
    return await database.fetch_all(query=query)

async def get_all():
    query = prediction_results.select()
    return await database.fetch_all(query=query)

async def update(prediction_result_id: int, payload: PredictionResultSchema):
    query = (
        prediction_results
        .update()
        .where(prediction_result_id == prediction_results.c.id)
        .values(
            inference_id = payload.inference_id,
            prediction_class = payload.prediction_class,
            confidence = payload.confidence
        )
        .returning(prediction_results.c.id)
    )
    return await database.execute(query=query)

async def delete(prediction_result_id: int):
    query = prediction_results.delete().where(prediction_result_id == prediction_results.c.id)
    return await database.execute(query=query)

async def delete_from_inference_id(inference_id: int):
    query = prediction_results.delete().where(inference_id == prediction_results.c.inference_id)
    return await database.execute(query=query)