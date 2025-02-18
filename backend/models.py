from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, Field, field_serializer
from datetime import datetime
from typing import Annotated, Any, Optional

def ensure_str(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        return v
    raise ValueError(f"Cannot convert {v} to an id")

Id = Annotated[str, BeforeValidator(ensure_str)]

class QuestionModel(BaseModel):
    id: Optional[Id] = Field(default=None, alias="_id")
    title: str
    body: str
    category: Optional[str] = "general"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime, _info):
        return created_at.timestamp()
    
    class Config:
        populate_by_name = True

class ResponseModel(BaseModel):
    id: Optional[Id] = Field(default=None, alias="_id")
    question_id: Id
    text: str
    author: Optional[str] = "anonymous"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime, _info):
        return created_at.timestamp()

    class Config:
        populate_by_name = True
