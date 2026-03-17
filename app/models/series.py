from beanie import Document
from pydantic import Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class Series(Document):
    title: str = Field(..., description="Titre de la série")
    description: Optional[str] = Field(None, description="Description de la série")
    genre: List[str] = Field(default_factory=list, description="Genres de la série")
    release_year: Optional[int] = Field(None, description="Année de sortie")
    country: str = Field(default="Sénégal", description="Pays de production")
    language: str = Field(default="Français", description="Langue principale")
    status: str = Field(default="ongoing", description="Statut: ongoing, completed, cancelled, hiatus")
    rating: str = Field(default="G", description="Classification: G, PG, PG-13, R, NC-17")
    image_url: Optional[str] = Field(None, description="URL de l'affiche")
    banner_url: Optional[str] = Field(None, description="URL de la bannière")
    trailer_url: Optional[str] = Field(None, description="URL de la bande-annonce")
    is_premium: bool = Field(default=False, description="Contenu premium")
    required_subscription_category: Optional[str] = Field(None, description="Catégorie d'abonnement requise: basic, standard, premium (None = gratuit)")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")
    cast: List[str] = Field(default_factory=list, description="Liste des acteurs")
    crew: List[str] = Field(default_factory=list, description="Équipe de production")
    production_company: Optional[str] = Field(None, description="Société de production")
    network: str = Field(default="BF1", description="Chaîne de diffusion")
    episode_duration: int = Field(default=45, description="Durée moyenne d'un épisode (minutes)")
    total_seasons: int = Field(default=0, description="Nombre total de saisons")
    total_episodes: int = Field(default=0, description="Nombre total d'épisodes")
    views_count: int = Field(default=0, description="Nombre de vues")
    likes_count: int = Field(default=0, description="Nombre de likes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    class Settings:
        name = "series"
        indexes = [
            "title",
            "genre",
            "status",
            "is_premium",
            "release_year",
            "created_at"
        ]

class Season(Document):
    series_id: str = Field(..., description="ID de la série")
    season_number: int = Field(..., description="Numéro de la saison")
    title: Optional[str] = Field(None, description="Titre de la saison")
    description: Optional[str] = Field(None, description="Description de la saison")
    release_date: Optional[datetime] = Field(None, description="Date de sortie")
    poster_url: Optional[str] = Field(None, description="URL du poster")
    trailer_url: Optional[str] = Field(None, description="URL de la bande-annonce")
    status: str = Field(default="upcoming", description="Statut: upcoming, airing, completed")
    episode_count: int = Field(default=0, description="Nombre d'épisodes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    class Settings:
        name = "seasons"
        indexes = [
            "series_id",
            "season_number",
            "status",
            "created_at"
        ]

class Episode(Document):
    series_id: str = Field(..., description="ID de la série")
    season_id: str = Field(..., description="ID de la saison")
    episode_number: int = Field(..., description="Numéro de l'épisode")
    title: str = Field(..., description="Titre de l'épisode")
    description: Optional[str] = Field(None, description="Description de l'épisode")
    duration: Optional[int] = Field(None, description="Durée en minutes")
    video_url: Optional[str] = Field(None, description="URL de la vidéo")
    thumbnail_url: Optional[str] = Field(None, description="URL de la miniature") 
    release_date: Optional[datetime] = Field(None, description="Date de sortie")
    status: str = Field(default="upcoming", description="Statut: upcoming, available, unavailable")
    is_premium: bool = Field(default=False, description="Épisode premium")
    views_count: int = Field(default=0, description="Nombre de vues")
    likes_count: int = Field(default=0, description="Nombre de likes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    class Settings:
        name = "episodes"
        indexes = [
            "series_id",
            "season_id", 
            "episode_number",
            "status",
            "is_premium",
            "created_at"
        ]