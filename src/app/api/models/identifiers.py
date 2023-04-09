from datetime import datetime
from pydantic import BaseModel, Field

class IdentifierSchema(BaseModel):
    identifier: str
    verification_token_id: int
    disabled: bool

class IdentifierInDB(IdentifierSchema):
    created_date: datetime