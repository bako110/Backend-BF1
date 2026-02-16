from beanie import Document
from pydantic import HttpUrl, Field
from datetime import datetime
from typing import Optional


class Reel(Document):
    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")
    title: str = Field(..., description="Titre de la vidéo")
    description: str = Field(..., description="Description de la vidéo")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")

    likes: int = Field(default=0, description="Nombre de likes")
    comments: int = Field(default=0, description="Nombre de commentaires")
    shares: int = Field(default=0, description="Nombre de partages")
    views: int = Field(default=0, description="Nombre de vues")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "reels"
