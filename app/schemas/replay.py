from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional
from bson import ObjectId


class ReplayBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre du replay")
    category: str = Field(..., min_length=1, max_length=80, description="Catégorie du replay")
    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")
    thumbnail: Optional[HttpUrl] = Field(None, description="Miniature du replay")
    description: str = Field(..., min_length=1, max_length=5000, description="Description du replay")
    duration_minutes: int = Field(..., ge=1, le=600, description="Durée en minutes")
    program_title: Optional[str] = Field(None, min_length=1, max_length=200, description="Émission d'origine")
    host: Optional[str] = Field(None, min_length=1, max_length=120, description="Animateur / présentateur")
    aired_at: datetime = Field(..., description="Date de diffusion originale")

    @validator("video_url", "thumbnail", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class ReplayCreate(ReplayBase):
    pass


class ReplayUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=80)
    video_url: Optional[HttpUrl] = None
    thumbnail: Optional[HttpUrl] = None
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    duration_minutes: Optional[int] = Field(None, ge=1, le=600)
    program_title: Optional[str] = Field(None, min_length=1, max_length=200)
    host: Optional[str] = Field(None, min_length=1, max_length=120)
    aired_at: Optional[datetime] = None


class ReplayOut(ReplayBase):
    id: str
    views: int = Field(0, ge=0, description="Nombre de vues")
    rating: float = Field(0, ge=0, le=5, description="Note du replay (0 à 5)")
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
