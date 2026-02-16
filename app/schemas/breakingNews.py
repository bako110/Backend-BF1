from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional
from bson import ObjectId


class BreakingNewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre de l'actualité")
    category: str = Field(..., min_length=1, max_length=80, description="Catégorie de l'actualité")
    description: str = Field(..., min_length=1, max_length=5000, description="Contenu de l'actualité")
    image: Optional[HttpUrl] = Field(None, description="URL de l'image")
    author: str = Field(..., min_length=1, max_length=120, description="Auteur de l'article")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")

    @validator("image", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class BreakingNewsCreate(BreakingNewsBase):
    pass


class BreakingNewsUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=80)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    image: Optional[HttpUrl] = None
    author: Optional[str] = Field(None, min_length=1, max_length=120)
    allow_comments: Optional[bool] = None


class BreakingNewsOut(BreakingNewsBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
