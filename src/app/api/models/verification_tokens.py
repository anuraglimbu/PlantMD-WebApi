from datetime import datetime
from typing import Union
from pydantic import BaseModel, Field

class VerificationTokenSchema(BaseModel):
    token: str
    name: str
    disabled: bool

class VerificationTokenDB(VerificationTokenSchema):
    id: int
    user_id: Union[int, None]
    created_date: datetime