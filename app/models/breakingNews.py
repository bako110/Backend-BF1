from beanie import Document
from pydantic import HttpUrl, Field
from datetime import datetime
from typing import Optional


# Modèle de données pour MongoDB
class BreakingNews(Document):
    title: str = Field(..., description="Titre de l'actualité")
    category: str = Field(..., description="Catégorie de l'actualité (Économie, Politique, etc.)")
    description: str = Field(..., description="Contenu de l'actualité")
    image: Optional[HttpUrl] = Field(None, description="URL de l'image")
    author: str = Field(..., description="Auteur de l'article")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "breaking_news"  # Nom de la collection MongoDB
