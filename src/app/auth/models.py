from datetime import datetime
from typing import Union, Optional

from pydantic import BaseModel
from fastapi.param_functions import Form

class AccessToken(BaseModel):
    access_token: str
    token_type: str
    identifier: str

class TokenData(BaseModel):
    identifier: Union[str, None] = None

class RequestTokenForm:
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        username: Optional[str] = Form(default=None),
        password: str = Form(),
        scope: str = Form(default=""),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split()

class VerificationToken(BaseModel):
    id: int
    token: str
    name: str
    user_id: Union[int, None]
    disabled: bool
    created_date: datetime