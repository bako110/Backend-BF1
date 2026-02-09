from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class ArchivePurchase(Document):
    """Modèle pour les achats individuels d'archives"""
    
    user_id: str = Field(..., description="ID de l'utilisateur")
    archive_id: str = Field(..., description="ID de l'archive achetée")
    
    # Informations de paiement
    amount_paid: float = Field(..., description="Montant payé")
    currency: str = Field(default="EUR", description="Devise")
    payment_method: str = Field(..., description="Méthode de paiement")
    transaction_id: Optional[str] = Field(None, description="ID de transaction externe")
    
    # Statut
    status: str = Field(default="completed", description="Statut de l'achat (completed, refunded, failed)")
    
    # Dates
    purchased_at: datetime = Field(default_factory=datetime.utcnow, description="Date d'achat")
    expires_at: Optional[datetime] = Field(None, description="Date d'expiration (si applicable)")
    
    # Métadonnées
    ip_address: Optional[str] = Field(None, description="Adresse IP de l'achat")
    user_agent: Optional[str] = Field(None, description="User agent")
    
    class Settings:
        name = "archive_purchases"
        indexes = [
            "user_id",
            "archive_id",
            [("user_id", 1), ("archive_id", 1)],  # Index composé
        ]
