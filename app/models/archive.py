from beanie import Document
from pydantic import HttpUrl, Field
from datetime import datetime
from typing import Optional


class Archive(Document):
    title: str = Field(..., description="Titre de l'archive")
    guest_name: str = Field(..., description="Nom de l'invité")
    guest_role: str = Field(..., description="Rôle ou fonction de l'invité")
    
    image: Optional[HttpUrl] = Field(None, description="Image de l'archive")
    thumbnail: Optional[HttpUrl] = Field(None, description="Miniature de l'archive")
    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")
    
    description: str = Field(..., description="Description ou contenu de l'archive")
    duration_minutes: int = Field(..., description="Durée en minutes")
    
    # Informations de paiement
    is_premium: bool = Field(default=True, description="Contenu premium (payant)")
    price: float = Field(default=0.0, description="Prix de l'archive (si achat individuel)")
    
    # Statistiques
    views: int = Field(default=0, description="Nombre de vues")
    rating: float = Field(default=0, ge=0, le=5, description="Note de l'archive (0 à 5)")
    
    # Catégories et tags
    category: Optional[str] = Field(None, description="Catégorie de l'archive")
    tags: list[str] = Field(default_factory=list, description="Tags de l'archive")
    
    # Dates
    archived_date: datetime = Field(..., description="Date d'archivage")
    original_publish_date: Optional[datetime] = Field(None, description="Date de publication originale")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")
    
    # Statut
    is_active: bool = Field(default=True, description="Archive active")

    class Settings:
        name = "archives"
