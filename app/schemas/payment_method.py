"""Schémas Pydantic pour les méthodes de paiement"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PaymentMethodBase(BaseModel):
    """Schéma de base pour les méthodes de paiement"""
    code: str = Field(..., description="Code unique")
    name: str = Field(..., description="Nom affiché")
    description: Optional[str] = Field(None, description="Description")
    icon_url: Optional[str] = Field(None, description="URL de l'icône")
    is_active: bool = Field(default=True, description="Méthode active")
    order: int = Field(default=0, description="Ordre d'affichage")
    min_amount: Optional[float] = Field(None, description="Montant minimum")
    max_amount: Optional[float] = Field(None, description="Montant maximum")


class PaymentMethodCreate(PaymentMethodBase):
    """Schéma pour créer une méthode de paiement"""
    pass


class PaymentMethodUpdate(BaseModel):
    """Schéma pour mettre à jour une méthode de paiement"""
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: Optional[bool] = None
    order: Optional[int] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


class PaymentMethodOut(PaymentMethodBase):
    """Schéma de sortie pour les méthodes de paiement"""
    id: str = Field(..., alias="id")
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_serializer('id')
    def serialize_id(self, value):
        """Convertir ObjectId en string"""
        if isinstance(value, ObjectId):
            return str(value)
        return value
    
    class Config:
        populate_by_name = True
        from_attributes = True
