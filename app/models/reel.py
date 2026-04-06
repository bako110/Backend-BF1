from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional, List


class Reel(Document):
    video_url: Optional[str] = Field(None, description="URL de la vidéo")
    title: str = Field(..., description="Titre de la vidéo")
    description: Optional[str] = Field(None, description="Description de la vidéo")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")
    duration: Optional[float] = Field(None, description="Durée de la vidéo en secondes")
    thumbnail_url: Optional[str] = Field(None, description="URL de la miniature")
    tags: List[str] = Field(default_factory=list, description="Tags pour la découverte")

    # Métriques de base
    likes: int = Field(default=0, description="Nombre de likes")
    comments: int = Field(default=0, description="Nombre de commentaires")
    shares: int = Field(default=0, description="Nombre de partages")
    views: int = Field(default=0, description="Nombre de vues uniques 24h")
    saves: int = Field(default=0, description="Nombre de sauvegardes/favoris")

    # Métriques de rétention (clé pour garder l'utilisateur)
    watch_time_total: float = Field(default=0.0, description="Temps de visionnage cumulé en secondes")
    watch_completions: int = Field(default=0, description="Nombre de visionnages jusqu'au bout")

    # Métriques récentes pour le trending (fenêtre glissante 48h)
    recent_likes: int = Field(default=0, description="Likes des dernières 48h")
    recent_views: int = Field(default=0, description="Vues des dernières 48h")
    recent_shares: int = Field(default=0, description="Partages des dernières 48h")
    trending_score: float = Field(default=0.0, description="Score trending calculé")
    trending_updated_at: Optional[datetime] = Field(None, description="Dernière mise à jour trending")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "reels"
        indexes = [
            "created_at",
            "trending_score",
            [("trending_score", -1), ("created_at", -1)],
        ]
