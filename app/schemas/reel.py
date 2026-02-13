from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional
from bson import ObjectId


class ReelBase(BaseModel):
    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")
    title: str = Field(..., min_length=1, max_length=200, description="Titre de la vidéo")
    description: str = Field(..., min_length=1, max_length=5000, description="Description de la vidéo")

    likes: int = Field(default=0, ge=0, description="Nombre de likes")
    comments: int = Field(default=0, ge=0, description="Nombre de commentaires")
    shares: int = Field(default=0, ge=0, description="Nombre de partages")

    @validator("video_url", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class ReelCreate(BaseModel):
    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")
    title: str = Field(..., min_length=1, max_length=200, description="Titre de la vidéo")
    description: str = Field(..., min_length=1, max_length=5000, description="Description de la vidéo")

    @validator("video_url", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class ReelUpdate(BaseModel):
    video_url: Optional[HttpUrl] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)

    likes: Optional[int] = Field(None, ge=0)
    comments: Optional[int] = Field(None, ge=0)
    shares: Optional[int] = Field(None, ge=0)


class ReelOut(ReelBase):
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
