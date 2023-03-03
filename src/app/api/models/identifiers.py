from datetime import datetime
from pydantic import BaseModel, Field

class Identifier(BaseModel):
    identifier: str
    verification_token_id: int
    disabled: bool

class IdentifierInDB(Identifier):
    created_date: datetime