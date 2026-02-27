from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime


class Sport(Document):
    """
    Modèle de document pour les sports
    """
    title: str = Field(..., description="Titre du sport")
    description: Optional[str] = Field(None, description="Description du sport")
    
    # Catégories
    category: str = Field(..., description="Catégorie du sport")
    subcategory: Optional[str] = Field(None, description="Sous-catégorie")
    
    # Médias
    image: Optional[str] = Field(None, description="URL de l'image principale")
    thumbnail: Optional[str] = Field(None, description="URL de la miniature")
    video_url: Optional[str] = Field(None, description="URL de la vidéo")
    
    # Métadonnées
    duration: Optional[int] = Field(None, description="Durée en secondes")
    date: Optional[datetime] = Field(None, description="Date de diffusion")
    presenter: Optional[str] = Field(None, description="Présentateur")
    
    # Statistiques
    views: int = Field(default=0, description="Nombre de vues")
    likes: int = Field(default=0, description="Nombre de likes")
    
    # Tags et métadonnées
    tags: List[str] = Field(default_factory=list, description="Liste des tags")
    featured: bool = Field(default=False, description="Sport en vedette")
    is_new: bool = Field(default=False, description="Nouveau sport")
    is_active: bool = Field(default=True, description="Sport actif")
    
    # Champs spécifiques aux sports
    sport_type: Optional[str] = Field(None, description="Type de sport (Football, Basket, etc.)")
    teams: List[str] = Field(default_factory=list, description="Liste des équipes participantes")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "sports"
        indexes = [
            "category",
            "subcategory",
            "featured",
            "is_new",
            "is_active",
            "date",
            "views",
            "created_at"
        ]
