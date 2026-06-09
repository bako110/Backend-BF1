from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class Missed(Document):
    title: str = Field(..., description="Titre du contenu manqué")
    description: Optional[str] = Field(None, description="Description du contenu")
    
    # Médias
    thumbnail: Optional[str] = Field(None, description="URL de la miniature")
    image_url: Optional[str] = Field(None, description="URL de l'image")
    video_url: Optional[str] = Field(None, description="URL de la vidéo")
    
    # Métadonnées
    duration: Optional[int] = Field(None, description="Durée en minutes")
    category: Optional[str] = Field(None, description="Catégorie du contenu")
    tags: List[str] = Field(default_factory=list, description="Liste des tags")
    
    # Statistiques
    views: int = Field(default=0, description="Nombre de vues")
    likes: int = Field(default=0, description="Nombre de likes")
    
    # Statut et accès
    is_active: bool = Field(default=True, description="Contenu actif")
    is_premium: bool = Field(default=False, description="Contenu premium")
    required_subscription_category: Optional[str] = Field(None, description="Catégorie d'abonnement requise")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")
    
    # Dates
    published_at: Optional[datetime] = Field(None, description="Date de publication")
    aired_at: Optional[datetime] = Field(None, description="Date de diffusion originale")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "missed"
        indexes = [
            "category",
            "is_active",
            "is_premium",
            "aired_at",
            "published_at",
            "views",
            "created_at"
        ]
