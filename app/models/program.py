from beanie import Document
from pydantic import Field, HttpUrl
from datetime import datetime
from typing import Optional, List


class LiveChannel(Document):
    """Chaîne TV pour organiser les programmes"""
    name: str = Field(..., description="Nom de la chaîne")
    logo_url: Optional[HttpUrl] = Field(None, description="Logo de la chaîne")
    description: Optional[str] = Field(None, description="Description")
    order: int = Field(default=0, description="Ordre d'affichage")
    is_active: bool = Field(default=True, description="Chaîne active")
    is_news_channel: bool = Field(default=False, description="Chaîne d'info continue")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    
    class Settings:
        name = "live_channels"
        indexes = [
            "is_active",
            "order",
        ]


class Program(Document):
    """Programme TV (EPG) - Guide électronique des programmes"""
    title: str = Field(..., description="Titre du programme")
    description: Optional[str] = Field(None, description="Description")
    
    # Horaires
    start_time: datetime = Field(..., description="Date/heure de début")
    end_time: datetime = Field(..., description="Date/heure de fin")
    
    # Catégorisation
    type: str = Field(..., description="Type: Actualités, Sport, Culture, Politique, etc.")
    category: Optional[str] = Field(None, description="Catégorie secondaire")
    
    # Médias
    image_url: Optional[HttpUrl] = Field(None, description="Image/vignette")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="Miniature")
    
    # Présentation
    host: Optional[str] = Field(None, description="Présentateur/Animateur")
    guests: List[str] = Field(default_factory=list, description="Invités")
    
    # Statut
    is_live: bool = Field(default=False, description="En direct maintenant")
    has_replay: bool = Field(default=False, description="Replay disponible")
    replay_url: Optional[str] = Field(None, description="URL du replay")
    
    # Liens
    channel_id: Optional[str] = Field(None, description="ID de la chaîne")
    show_id: Optional[str] = Field(None, description="ID de l'émission liée")
    
    # Métadonnées
    duration_minutes: Optional[int] = Field(None, description="Durée en minutes")
    rating: Optional[str] = Field(None, description="Classification: PG-13, etc.")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    
    class Settings:
        name = "programs"
        indexes = [
            "start_time",
            "end_time",
            [("start_time", 1), ("end_time", 1)],
            "type",
            "category",
            "is_live",
            "channel_id",
            "show_id",
            [("start_time", -1)],
        ]


class ProgramReminder(Document):
    """Rappel de programme pour un utilisateur"""
    user_id: str = Field(..., description="ID utilisateur")
    program_id: str = Field(..., description="ID du programme")
    
    # Configuration du rappel
    minutes_before: int = Field(default=15, description="Minutes avant le début")
    reminder_type: str = Field(default="push", description="Type: push, inapp, email, sms")
    
    # Statut
    status: str = Field(default="scheduled", description="scheduled, sent, cancelled, failed")
    scheduled_for: datetime = Field(..., description="Date/heure d'envoi du rappel")
    sent_at: Optional[datetime] = Field(None, description="Date/heure d'envoi effectif")
    
    # Données denormalisées pour affichage
    program_title: Optional[str] = Field(None, description="Titre du programme")
    program_start_time: Optional[datetime] = Field(None, description="Début du programme")
    channel_name: Optional[str] = Field(None, description="Nom de la chaîne")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    
    class Settings:
        name = "program_reminders"
        indexes = [
            "user_id",
            "program_id",
            "status",
            [("user_id", 1), ("program_id", 1)],  # Unique: un rappel par user/program
            [("user_id", 1), ("scheduled_for", 1)],
            [("status", 1), ("scheduled_for", 1)],  # Pour le job d'envoi
        ]
