from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre du film")
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    genre: List[str] = Field(default_factory=list, description="Genres")
    release_date: Optional[datetime] = Field(None, description="Date de sortie")
    duration: Optional[int] = Field(None, ge=0, le=500, description="Durée en minutes")
    image_url: Optional[str] = Field(None, description="URL de l'affiche")
    is_premium: bool = Field(False, description="Film premium")
    video_url: Optional[str] = Field(None, description="URL de streaming")

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    genre: Optional[List[str]] = None
    release_date: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=0, le=500)
    image_url: Optional[str] = None
    is_premium: Optional[bool] = None
    video_url: Optional[str] = None

class MovieOut(MovieBase):
    id: str
    likes_count: int = Field(0, description="Nombre de likes")
    comments_count: int = Field(0, description="Nombre de commentaires")
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
