from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


# Modèle de données pour MongoDB
class BreakingNews(Document):
    title: str = Field(..., description="Titre de l'actualité")
    category: str = Field(..., description="Catégorie de l'actualité (Économie, Politique, etc.)")
    description: Optional[str] = Field(None, description="Contenu de l'actualité")
    image: Optional[str] = Field(None, description="URL de l'image")
    author: str = Field(..., description="Auteur de l'article")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")
    views: int = Field(default=0, description="Nombre de vues")
    likes: int = Field(default=0, description="Nombre de likes")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "breaking_news"
        indexes = [
            "category",
            "author",
            [("created_at", -1)],
            [("category", 1), ("created_at", -1)],
            [("title", "text"), ("description", "text")],
        ]
