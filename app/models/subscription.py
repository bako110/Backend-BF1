from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Subscription(Document):
    user_id: str = Field(..., description="ID de l'utilisateur abonné")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = Field(None, description="Date de fin d'abonnement")
    is_active: bool = Field(True, description="Abonnement actif ?")
    payment_method: Optional[str] = Field(None, description="Moyen de paiement")
    transaction_id: Optional[str] = Field(None, description="ID de transaction")
    offer: Optional[str] = Field(None, description="Type d'offre ou promotion")

    class Settings:
        name = "subscriptions"
        indexes = [
            "user_id",
            "is_active",
            "end_date",
            [("user_id", 1), ("is_active", -1)]
        ]
