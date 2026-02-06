from beanie import Document
from pydantic import HttpUrl, Field
from datetime import datetime
from typing import Optional


class PopularPrograms(Document):
    title: str = Field(..., description="Titre du programme")
    schedule: str = Field(..., description="Horaire du programme")
    image: Optional[HttpUrl] = Field(None, description="Image de présentation")
    description: str = Field(..., description="Description du programme")
    episodes: int = Field(..., description="Nombre d'épisodes disponibles")
    rating: float = Field(default=0, ge=0, le=5, description="Note moyenne du programme")
    category: str = Field(..., description="Catégorie du programme (Culture, Sport, Débat, etc.)")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "popular_programs"
