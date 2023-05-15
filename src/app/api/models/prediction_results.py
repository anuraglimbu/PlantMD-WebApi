from datetime import datetime
from typing import Union
from pydantic import BaseModel

class PredictionResultSchema(BaseModel):
    inference_id: int
    prediction_class: str
    confidence: float

class PredictionResultInDB(PredictionResultSchema):
    id: int