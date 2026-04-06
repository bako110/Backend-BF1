from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from bson import ObjectId


class ReelBase(BaseModel):
    video_url: Optional[str] = Field(None, description="URL de la vidéo")
    title: str = Field(..., min_length=1, max_length=200, description="Titre de la vidéo")
    description: Optional[str] = Field(None, description="Description de la vidéo")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")

    likes: int = Field(default=0, ge=0, description="Nombre de likes")
    comments: int = Field(default=0, ge=0, description="Nombre de commentaires")
    shares: int = Field(default=0, ge=0, description="Nombre de partages")

    @validator("video_url", pre=True)
    def validate_video_url(cls, v):
        if v == "" or v is None:
            return None
        if isinstance(v, str) and (v.startswith("http://") or v.startswith("https://")):
            return v
        return None
    
    @validator("description", pre=True)
    def validate_description(cls, v):
        if v == "":
            return None
        return v


class ReelCreate(BaseModel):
    video_url: Optional[str] = Field(None, description="URL de la vidéo")
    title: str = Field(..., min_length=1, max_length=200, description="Titre de la vidéo")
    description: Optional[str] = Field(None, description="Description de la vidéo")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")
    duration: Optional[float] = Field(None, description="Durée en secondes")
    thumbnail_url: Optional[str] = Field(None, description="URL de la miniature")
    tags: Optional[list] = Field(default_factory=list, description="Tags")

    class Config:
        extra = "ignore"

    @validator("video_url", pre=True)
    def validate_video_url(cls, v):
        if v == "" or v is None:
            return None
        if isinstance(v, str) and (v.startswith("http://") or v.startswith("https://")):
            return v
        return None

    @validator("description", pre=True)
    def validate_description(cls, v):
        if v == "":
            return None
        return v


class ReelUpdate(BaseModel):
    video_url: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    allow_comments: Optional[bool] = None

    likes: Optional[int] = Field(None, ge=0)
    comments: Optional[int] = Field(None, ge=0)
    shares: Optional[int] = Field(None, ge=0)

    class Config:
        extra = "ignore"  # Ignorer les champs supplémentaires
    
    @validator("description", pre=True)
    def validate_description(cls, v):
        if v == "":
            return None
        return v


class ReelOut(ReelBase):
    id: str
    views: int = 0
    saves: int = 0
    watch_completions: int = 0
    trending_score: float = 0.0
    duration: Optional[float] = None
    thumbnail_url: Optional[str] = None
    tags: list = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
