from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, Field, field_serializer
from datetime import datetime, timezone
from typing import Annotated, Any, Optional

def ensure_str(v: Any) -> Optional[str]:
    """
    Ensures that the input value is converted to a string if possible.
    Args:
        v (Any): The input value to be converted.
    Returns:
        Optional[str]: The string representation of the input value if it can be converted,
                       otherwise None if the input value is None.
    Raises:
        ValueError: If the input value cannot be converted to a string.
    """
    
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime, _info):
        return created_at.timestamp()

    class Config:
        populate_by_name = True
