from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class UserSettings(Document):
    """Paramètres utilisateur pour l'application"""
    user_id: str = Field(..., description="ID de l'utilisateur")
    
    # Notifications
    push_notifications: bool = Field(True, description="Activer les notifications push")
    email_notifications: bool = Field(True, description="Activer les notifications par email")
    live_notifications: bool = Field(True, description="Notifications pour les lives")
    news_notifications: bool = Field(True, description="Notifications pour les actualités")
    
    # Préférences de lecture
    auto_play: bool = Field(True, description="Lecture automatique des vidéos")
    video_quality: str = Field("auto", description="Qualité vidéo: auto, low, medium, high")
    subtitles_enabled: bool = Field(False, description="Activer les sous-titres par défaut")
    
    # Confidentialité
    profile_visibility: str = Field("public", description="Visibilité du profil: public, friends, private")
    show_watch_history: bool = Field(True, description="Afficher l'historique de visionnage")
    
    # Langue et région
    language: str = Field("fr", description="Langue de l'application")
    region: str = Field("BF", description="Région/Pays")
    
    # Thème
    theme: str = Field("dark", description="Thème: dark, light, auto")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "user_settings"
        indexes = [
            "user_id",
        ]
