import os
from dotenv import load_dotenv

from datetime import timedelta
from typing import Union

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

from app.api.models.identifiers import IdentifierInDB
from app.auth.models import TokenData
from app.auth.utils import create_access_token_utility, get_token, verify_token, get_device, create_device

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = SECRET_KEY = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
IDENTIFIER_HEX_VALUE = int(os.getenv("IDENTIFIER_HEX_VALUE"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    
async def get_current_device(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        identifier: str = payload.get("sub")
        if identifier is None:
            raise credentials_exception
        token_data = TokenData(identifier=identifier)
    except JWTError:
        raise credentials_exception
    device = await get_device(identifier=token_data.identifier)
    if device is None:
        raise credentials_exception
    return device

async def get_current_active_device(current_device: IdentifierInDB = Depends(get_current_device) ):
    if current_device.disabled:
        raise HTTPException(status_code=400, detail="Disabled device")
    return current_device

async def authenticate_device(identifier: Union[str, None], verification_token: str):
    if not (await verify_token(verification_token)):
        return False
    token = await get_token(verification_token)
    if (identifier is None) or identifier == "":
        identifier = await create_device(verification_token_id=token.id, hex_value=IDENTIFIER_HEX_VALUE)
    device = await get_device(identifier)
    if not device:
        return False
    if not device.verification_token_id == token.id:
        return False
    return device

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    return create_access_token_utility(SECRET_KEY, algorithm=ALGORITHM, data=data, expires_delta=expires_delta)
