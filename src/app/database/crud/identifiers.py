from app.database.db import database
from app.database.structures import identifiers

from app.api.models.identifiers import IdentifierSchema

async def create(payload: IdentifierSchema):
    query = identifiers.insert().values(
        identifier=payload.identifier,
        verification_token_id=payload.verification_token_id,
        disabled=payload.disabled
    ).returning(identifiers.c.identifier)
    return await database.execute(query=query)

async def get(identifier: str):
    query = identifiers.select().where(identifier == identifiers.c.identifier)
    return await database.fetch_one(query=query)

async def get_from_token_id(verification_token_id: int):
    query = identifiers.select().where(verification_token_id == identifiers.c.verification_token_id)
    return await database.fetch_all(query=query)

async def get_all():
    query = identifiers.select()
    return await database.fetch_all(query=query)

async def update(identifier: str, payload: IdentifierSchema):
    query = (
        identifiers
        .update()
        .where(identifier == identifiers.c.identifier)
        .values(
            identifier = payload.identifier, 
            verification_token_id = payload.name,
            disabled = payload.disabled
        )
        .returning(identifier.c.identifier)
    )
    return await database.execute(query=query)

async def delete(identifier: str):
    query = identifiers.delete().where(identifier == identifiers.c.identifier)
    return await database.execute(query=query)

async def delete_from_token_id(verification_token_id: int):
    query = identifiers.delete().where(verification_token_id == identifiers.c.verification_token_id)
    return await database.execute(query=query)