from beanie import Document
from pydantic import Field
from typing import List, Optional
from datetime import datetime

class Movie(Document):
    title: str = Field(..., description="Titre du film")
    description: Optional[str] = Field(None, description="Description du film")
    genre: List[str] = Field(default_factory=list, description="Genres du film")
    release_date: Optional[datetime] = Field(None, description="Date de sortie")
    duration: Optional[int] = Field(None, description="Durée en minutes")
    image_url: Optional[str] = Field(None, description="URL de l'affiche")
    is_premium: bool = Field(False, description="Film premium ?")
    video_url: Optional[str] = Field(None, description="URL de streaming")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")
    # Les commentaires et likes sont gérés dans des collections séparées (Comment, Like)
    republished: bool = Field(False, description="Film republié ?")
    republished_at: Optional[datetime] = Field(None, description="Date de republication")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour")

    class Settings:
        name = "movies"
        indexes = [
            "genre",
            "is_premium",
            "release_date",
            "created_at"
        ]
