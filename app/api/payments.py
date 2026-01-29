from fastapi import APIRouter, status, Depends
from app.utils.auth import get_current_user
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()

class PaymentRequest(BaseModel):
	amount: float = Field(..., gt=0, description="Montant du paiement")
	method: str = Field(..., description="Méthode: orange, mtn, intouch, etc.")
	offer: Optional[str] = Field(None, description="Code promo ou offre")

@router.post("/process", status_code=status.HTTP_201_CREATED)
async def process_payment(payment: PaymentRequest, current_user=Depends(get_current_user)):
	"""Traiter un paiement (Orange Money, MTN, InTouch, etc.)"""
	# TODO: Intégrer l'API de paiement réelle
	return {
		"success": True,
		"message": "Paiement en cours de traitement",
		"transaction_id": f"MOCK-{current_user.id}-123456",
		"amount": payment.amount,
		"method": payment.method
	}

@router.get("/methods")
async def get_payment_methods():
	"""Lister les méthodes de paiement disponibles"""
	return {
		"methods": [
			{"id": "orange", "name": "Orange Money", "available": True},
			{"id": "mtn", "name": "MTN Mobile Money", "available": True},
			{"id": "intouch", "name": "InTouch", "available": True},
			{"id": "card", "name": "Carte bancaire", "available": False}
		]
	}
