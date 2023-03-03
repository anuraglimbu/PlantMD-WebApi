from datetime import datetime, timedelta
from typing import Union
from secrets import token_hex

from fastapi import HTTPException, status
from jose import jwt

from app.api.models.identifiers import IdentifierInDB, Identifier
from app.auth.models import VerificationToken

from app.database.crud import verification_tokens, identifiers

async def get_token(verification_token: str):
    token = await verification_tokens.get_from_token(verification_token)
    if token:
        return VerificationToken(**token)

async def verify_token(verification_token: str):
    token_data = await get_token(verification_token)
    if not token_data:
        return False
    if token_data.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Disabled verification token")
    return True

async def get_device(identifier: str):
    identifier_dict = await identifiers.get(identifier=identifier)
    if identifier_dict:
        return IdentifierInDB(**identifier_dict)
    
async def create_device(verification_token_id: int, hex_value: int):
    generated_identifier = ""
    while True:
        generated_identifier = token_hex(hex_value)
        temp_identifier = await identifiers.get(generated_identifier)
        if not temp_identifier:
            break
    payload = Identifier(
        identifier = generated_identifier,
        verification_token_id = verification_token_id,
        disabled = False
    )
    return await identifiers.create(payload)

def create_access_token_utility(secret_key: str, algorithm: str, data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt