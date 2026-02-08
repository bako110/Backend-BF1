from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class SubscriptionBase(BaseModel):
	user_id: str = Field(..., description="ID de l'utilisateur")
	start_date: Optional[datetime] = Field(None, description="Date de début")
	end_date: Optional[datetime] = Field(None, description="Date de fin")
	is_active: bool = Field(True, description="Actif")
	payment_method: Optional[str] = Field(None, max_length=50, description="Méthode de paiement")
	transaction_id: Optional[str] = Field(None, max_length=100, description="ID transaction")
	offer: Optional[str] = Field(None, max_length=50, description="Offre")
	is_in_country: Optional[bool] = Field(None, description="Utilisateur au Burkina Faso")
	price_multiplier: Optional[float] = Field(1.0, description="Multiplicateur de prix appliqué")
	final_price: Optional[int] = Field(None, description="Prix final payé en FCFA")

class SubscriptionCreate(SubscriptionBase):
	pass

class SubscriptionOut(SubscriptionBase):
	id: str

	@validator("id", pre=True, always=True)
	def str_id(cls, v):
		if isinstance(v, ObjectId):
			return str(v)
		return v

	class Config:
		from_attributes = True
