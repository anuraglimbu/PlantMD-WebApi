from datetime import datetime
from pydantic import BaseModel, Field

class InferenceSchema(BaseModel):
    identifier: str
    verification_token_id: int
    disabled: bool

class InferenceInDB(InferenceSchema):
    created_date: datetime