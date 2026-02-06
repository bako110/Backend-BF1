from beanie import Document
from pydantic import HttpUrl, Field
from datetime import datetime
from typing import Optional


class Interview(Document):
    title: str = Field(..., description="Titre de l'interview")
    guest_name: str = Field(..., description="Nom de l'invité")
    guest_role: str = Field(..., description="Rôle ou fonction de l'invité")

    image: Optional[HttpUrl] = Field(None, description="Image de l'interview")
    description: str = Field(..., description="Description ou contenu de l'interview")

    duration_minutes: int = Field(..., description="Durée en minutes")
    views: int = Field(default=0, description="Nombre de vues")
    rating: float = Field(default=0, ge=0, le=5, description="Note de l'interview (0 à 5)")

    published_at: Optional[datetime] = Field(None, description="Date de publication")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "interviews"
