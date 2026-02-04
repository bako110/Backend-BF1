from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class SubscriptionPlan(Document):
    code: str = Field(..., description="Code unique du plan (ex: monthly, quarterly, yearly)")
    name: str = Field(..., description="Nom affiché")
    duration_months: int = Field(..., ge=1, le=60, description="Durée en mois")
    price_cents: int = Field(..., ge=0, description="Prix en centimes")
    currency: str = Field("XOF", min_length=3, max_length=3, description="Devise ISO")
    is_active: bool = Field(True, description="Plan disponible à la vente")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)

    class Settings:
        name = "subscription_plans"
        indexes = [
            "code",
            "is_active",
            [("is_active", -1), ("duration_months", 1)]
        ]
