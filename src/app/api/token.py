from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.auth.base import create_access_token, authenticate_device, ACCESS_TOKEN_EXPIRE_MINUTES

from app.auth.models import RequestTokenForm, AccessToken

router = APIRouter()

@router.post("/token", response_model=AccessToken)
async def request_for_access_token(payload: RequestTokenForm):
    device = await authenticate_device(payload.identifier, payload.verification_token)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect verification_token or identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": device.identifier}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "identifier": device.identifier}