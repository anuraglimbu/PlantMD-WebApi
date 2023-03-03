from datetime import datetime
from typing import Union

from pydantic import BaseModel, Field

class AccessToken(BaseModel):
    access_token: str
    token_type: str
    identifier: str

class TokenData(BaseModel):
    identifier: Union[str, None] = None

class RequestTokenForm(BaseModel):
    verification_token: str = Field(..., min_length=24, max_length=100)
    identifier: Union[str, None] = Field(default=None, min_length=8, max_length=100)

class VerificationToken(BaseModel):
    id: int
    token: str
    name: str
    user_id: Union[int, None]
    disabled: bool
    created_date: datetime