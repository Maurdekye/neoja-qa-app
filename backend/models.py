from pydantic import BaseModel, BeforeValidator, Field
from datetime import datetime
from typing import Annotated, Optional

def ensure_str(v):
    if v is None:
        return None
    if not isinstance(v, str):
        return str(v)
    return v

Id = Annotated[str, BeforeValidator(ensure_str)]

class QuestionModel(BaseModel):
    id: Optional[Id] = Field(default=None, alias="_id")
    title: str
    body: str
    category: Optional[str] = "general"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class ResponseModel(BaseModel):
    id: Optional[Id] = Field(default=None, alias="_id")
    question_id: Id
    text: str
    author: Optional[str] = "anonymous"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
