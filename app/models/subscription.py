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
    is_in_country: Optional[bool] = Field(None, description="Utilisateur au Burkina Faso lors de la souscription")
    price_multiplier: Optional[float] = Field(1.0, description="Multiplicateur de prix appliqué (1 = Burkina, 3 = International)")
    final_price: Optional[int] = Field(None, description="Prix final payé en FCFA")

    class Settings:
        name = "subscriptions"
        indexes = [
            "user_id",
            "is_active",
            "end_date",
            [("user_id", 1), ("is_active", -1)]
        ]
