from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional, List
from datetime import datetime


class User(Document):
    email: Optional[EmailStr] = Field(None, description="Adresse email")
    phone: Optional[str] = Field(None, description="Numéro de téléphone")
    username: str = Field(..., description="Nom d'utilisateur")
    hashed_password: str = Field(..., description="Mot de passe hashé")
    is_active: bool = Field(True, description="Compte actif ?")
    is_premium: bool = Field(False, description="Abonné premium ?")
    is_admin: bool = Field(False, description="Administrateur ?")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = [
            "email",
            "username",
            "phone",
            "is_premium",
            "created_at"
        ]
