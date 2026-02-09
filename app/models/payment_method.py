"""Modèle pour les méthodes de paiement"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class PaymentMethod(Document):
    """Méthode de paiement disponible"""
    
    code: str = Field(..., description="Code unique (ex: orange, mtn, intouch)")
    name: str = Field(..., description="Nom affiché (ex: Orange Money)")
    description: Optional[str] = Field(None, description="Description de la méthode")
    icon_url: Optional[str] = Field(None, description="URL de l'icône")
    is_active: bool = Field(default=True, description="Méthode active")
    order: int = Field(default=0, description="Ordre d'affichage")
    
    # Configuration
    min_amount: Optional[float] = Field(None, description="Montant minimum")
    max_amount: Optional[float] = Field(None, description="Montant maximum")
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "payment_methods"
        indexes = [
            "code",
            "is_active",
            "order"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "orange",
                "name": "Orange Money",
                "description": "Paiement via Orange Money",
                "is_active": True,
                "order": 1,
                "min_amount": 100,
                "max_amount": 1000000
            }
        }
