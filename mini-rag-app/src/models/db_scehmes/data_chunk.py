from pydantic import BaseModel, Field, Validator
from typing import Optional
from bson.objectid import ObjectId


class DataChunk(BaseModel):

    def __init__(self):
        super().__init__()

    _id: Optional[ObjectId]
    chunk_text: str = Field(..., min_length=1)
    chunk_meatadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId


    class Config:
        arbitrary_types_allowed = True