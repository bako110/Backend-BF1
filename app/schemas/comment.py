from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

class CommentBase(BaseModel):
    content_id: str = Field(..., description="ID du contenu (movie ou show)")
    content_type: Literal["movie", "show"] = Field(..., description="Type de contenu")
    text: str = Field(..., min_length=1, max_length=1000, description="Texte du commentaire")

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Nouveau texte")

class CommentOut(CommentBase):
    id: str
    user_id: str
    username: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
