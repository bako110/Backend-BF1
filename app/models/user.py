from beanie import Document, Indexed
from pydantic import Field, EmailStr
from typing import Optional, List
from datetime import datetime
from pymongo import IndexModel


class User(Document):
    email: Optional[EmailStr] = Field(None, description="Adresse email")
    phone: Optional[str] = Field(None, description="Numéro de téléphone")
    username: str = Field(..., description="Nom d'utilisateur")
    hashed_password: str = Field(..., description="Mot de passe hashé")
    is_active: bool = Field(True, description="Compte actif ?")
    is_premium: bool = Field(False, description="Abonné premium ?")
    subscription_category: Optional[str] = Field(None, description="Catégorie d'abonnement active: basic, standard ou premium")
    is_admin: bool = Field(False, description="Administrateur ?")
    
    # Informations de localisation pour adapter les prix
    location_country_code: Optional[str] = Field(None, description="Code pays de l'utilisateur (ex: BF)")
    location_is_in_country: Optional[bool] = Field(None, description="Utilisateur au Burkina Faso ?")
    location_latitude: Optional[float] = Field(None, description="Latitude")
    location_longitude: Optional[float] = Field(None, description="Longitude")
    location_updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour de localisation")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    reset_token: Optional[str] = Field(None, description="Token de réinitialisation du mot de passe")
    reset_token_expires: Optional[datetime] = Field(None, description="Expiration du token de réinitialisation")

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", 1)], unique=True, sparse=True, name="email_1_unique"),
            IndexModel([("username", 1)], unique=True, name="username_1_unique"),
            "phone",  # Index simple sans contrainte unique pour éviter les problèmes avec null
            "is_premium",
            "location_is_in_country",
            "created_at"
        ]
