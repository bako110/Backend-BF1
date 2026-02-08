from beanie import Document
from pydantic import Field, HttpUrl
from typing import Optional, List
from datetime import datetime

class AppInfo(Document):
    """Informations sur l'application"""
    version: str = Field(..., description="Version de l'application")
    build_number: str = Field(..., description="Numéro de build")
    release_date: datetime = Field(..., description="Date de sortie")
    
    # Informations générales
    app_name: str = Field("BF1 TV", description="Nom de l'application")
    description: str = Field(..., description="Description de l'application")
    
    # Liens
    website: Optional[HttpUrl] = Field(None, description="Site web")
    privacy_policy_url: Optional[HttpUrl] = Field(None, description="Politique de confidentialité")
    terms_url: Optional[HttpUrl] = Field(None, description="Conditions d'utilisation")
    
    # Réseaux sociaux
    facebook_url: Optional[HttpUrl] = Field(None, description="Page Facebook")
    twitter_url: Optional[HttpUrl] = Field(None, description="Compte Twitter")
    instagram_url: Optional[HttpUrl] = Field(None, description="Compte Instagram")
    youtube_url: Optional[HttpUrl] = Field(None, description="Chaîne YouTube")
    
    # Contact
    support_email: Optional[str] = Field(None, description="Email de support")
    contact_phone: Optional[str] = Field(None, description="Téléphone de contact")
    
    # Fonctionnalités
    features: List[str] = Field(default_factory=list, description="Liste des fonctionnalités")
    changelog: List[dict] = Field(default_factory=list, description="Historique des changements")
    
    # Métadonnées
    is_active: bool = Field(True, description="Version active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "app_info"
        indexes = [
            "version",
            "is_active",
        ]


class TeamMember(Document):
    """Membres de l'équipe BF1"""
    name: str = Field(..., description="Nom du membre")
    role: str = Field(..., description="Rôle/Poste")
    bio: Optional[str] = Field(None, description="Biographie")
    photo_url: Optional[HttpUrl] = Field(None, description="Photo de profil")
    
    # Réseaux sociaux
    email: Optional[str] = Field(None, description="Email")
    linkedin_url: Optional[HttpUrl] = Field(None, description="LinkedIn")
    twitter_url: Optional[HttpUrl] = Field(None, description="Twitter")
    
    # Ordre et visibilité
    order: int = Field(0, description="Ordre d'affichage")
    is_active: bool = Field(True, description="Membre actif")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "team_members"
        indexes = [
            "is_active",
            "order",
        ]
