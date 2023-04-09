from app.database.db import database
from app.database.structures import verification_tokens

from app.api.models.verification_tokens import VerificationTokenSchema, VerificationTokenDB

async def create(payload: VerificationTokenSchema):
    query = verification_tokens.insert().values(
        token = payload.token, 
        name = payload.name, 
        disabled = payload.disabled
    )
    return await database.execute(query=query)

async def get(id: int):
    query = verification_tokens.select().where(id == verification_tokens.c.id)
    return await database.fetch_one(query=query)

async def get_from_token(token: str):
    query = verification_tokens.select().where(token == verification_tokens.c.token)
    return await database.fetch_one(query=query)

async def get_all():
    query = verification_tokens.select()
    return await database.fetch_all(query=query)

async def update(id: int, payload: VerificationTokenDB):
    query = (
        verification_tokens
        .update()
        .where(id == verification_tokens.c.id)
        .values(
            token = payload.token, 
            name = payload.name,
            user_id = payload.user_id,
            disabled = payload.disabled
        )
        .returning(verification_tokens.c.token)
    )
    return await database.execute(query=query)

async def delete(id: int):
    query = verification_tokens.delete().where(id == verification_tokens.c.id)
    return await database.execute(query=query)

async def delete_from_token(token: str):
    query = verification_tokens.delete().where(token == verification_tokens.c.token)
    return await database.execute(query=query)