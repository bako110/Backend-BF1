from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre")
    content: str = Field(..., min_length=1, description="Contenu")
    image_url: Optional[str] = Field(None, description="URL de l'image")
    author: Optional[str] = Field(None, max_length=100, description="Auteur")

class NewsCreate(NewsBase):
    edition: Optional[str] = Field(None, max_length=50, description="Édition")
    is_live: bool = Field(False, description="En direct")
    live_url: Optional[str] = Field(None, description="URL du live")

class NewsUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    image_url: Optional[str] = None
    author: Optional[str] = None
    edition: Optional[str] = None
    is_live: Optional[bool] = None
    live_url: Optional[str] = None

class NewsOut(NewsBase):
    id: str
    edition: Optional[str] = None
    is_live: bool = False
    live_url: Optional[str] = None
    published_at: datetime

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
