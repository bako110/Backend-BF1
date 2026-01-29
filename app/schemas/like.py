from pydantic import BaseModel, Field, validator
from typing import Literal, Optional
from datetime import datetime
from bson import ObjectId

class LikeBase(BaseModel):
    content_id: str = Field(..., description="ID du contenu (movie ou show)")
    content_type: Literal["movie", "show"] = Field(..., description="Type de contenu")

class LikeCreate(LikeBase):
    pass

class LikeOut(LikeBase):
    id: str
    user_id: str
    username: Optional[str] = None
    created_at: datetime

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
