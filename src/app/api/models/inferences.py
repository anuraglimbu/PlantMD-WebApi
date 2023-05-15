from datetime import datetime
from typing import Union
from pydantic import BaseModel

class InferenceSchema(BaseModel):
    identifier: str
    original_filename: str
    result_filename: str
    

class InferenceInDB(InferenceSchema):
    id: int
    created_date: datetime

class InferenceResult(BaseModel):
    # type: str
    # name : str
    # extension : str
    original_file : str
    classes : list
    confidences : list
    treatments : dict
    result_file : str

class Inferences(BaseModel):
    inferences: list