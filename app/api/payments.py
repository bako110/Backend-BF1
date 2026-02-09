from fastapi import APIRouter, status, Depends, HTTPException
from app.utils.auth import get_current_user, get_admin_user
from app.services import payment_method_service
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodOut
from pydantic import BaseModel, Field
from typing import Optional, List

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
	"""Lister les méthodes de paiement disponibles (pour les utilisateurs)"""
	methods = await payment_method_service.list_payment_methods(active_only=True)
	return {
		"methods": [
			{
				"id": str(method.id),
				"name": method.name,
				"available": method.is_active,
				"code": method.code,
				"description": method.description,
				"icon_url": method.icon_url,
				"min_amount": method.min_amount,
				"max_amount": method.max_amount
			}
			for method in methods
		]
	}

# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/methods", tags=["Admin - Payments"])
async def list_all_payment_methods(
	skip: int = 0,
	limit: int = 50,
	current_user=Depends(get_admin_user)
):
	"""Lister toutes les méthodes de paiement (admin only)"""
	methods = await payment_method_service.list_payment_methods(skip=skip, limit=limit)
	# Convertir les ObjectId en string manuellement
	return [
		{
			"id": str(method.id),
			"code": method.code,
			"name": method.name,
			"description": method.description,
			"icon_url": method.icon_url,
			"is_active": method.is_active,
			"order": method.order,
			"min_amount": method.min_amount,
			"max_amount": method.max_amount,
			"created_at": method.created_at,
			"updated_at": method.updated_at
		}
		for method in methods
	]

@router.post("/admin/methods", status_code=status.HTTP_201_CREATED, tags=["Admin - Payments"])
async def create_payment_method(
	data: PaymentMethodCreate,
	current_user=Depends(get_admin_user)
):
	"""Créer une nouvelle méthode de paiement (admin only)"""
	method = await payment_method_service.create_payment_method(data)
	return {
		"id": str(method.id),
		"code": method.code,
		"name": method.name,
		"description": method.description,
		"icon_url": method.icon_url,
		"is_active": method.is_active,
		"order": method.order,
		"min_amount": method.min_amount,
		"max_amount": method.max_amount,
		"created_at": method.created_at,
		"updated_at": method.updated_at
	}

@router.get("/admin/methods/{method_id}", tags=["Admin - Payments"])
async def get_payment_method(
	method_id: str,
	current_user=Depends(get_admin_user)
):
	"""Récupérer une méthode de paiement par ID (admin only)"""
	method = await payment_method_service.get_payment_method(method_id)
	if not method:
		raise HTTPException(status_code=404, detail="Méthode de paiement non trouvée")
	return {
		"id": str(method.id),
		"code": method.code,
		"name": method.name,
		"description": method.description,
		"icon_url": method.icon_url,
		"is_active": method.is_active,
		"order": method.order,
		"min_amount": method.min_amount,
		"max_amount": method.max_amount,
		"created_at": method.created_at,
		"updated_at": method.updated_at
	}

@router.put("/admin/methods/{method_id}", tags=["Admin - Payments"])
async def update_payment_method(
	method_id: str,
	data: PaymentMethodUpdate,
	current_user=Depends(get_admin_user)
):
	"""Mettre à jour une méthode de paiement (admin only)"""
	method = await payment_method_service.update_payment_method(method_id, data)
	if not method:
		raise HTTPException(status_code=404, detail="Méthode de paiement non trouvée")
	return {
		"id": str(method.id),
		"code": method.code,
		"name": method.name,
		"description": method.description,
		"icon_url": method.icon_url,
		"is_active": method.is_active,
		"order": method.order,
		"min_amount": method.min_amount,
		"max_amount": method.max_amount,
		"created_at": method.created_at,
		"updated_at": method.updated_at
	}

@router.delete("/admin/methods/{method_id}", tags=["Admin - Payments"])
async def delete_payment_method(
	method_id: str,
	current_user=Depends(get_admin_user)
):
	"""Supprimer une méthode de paiement (admin only)"""
	deleted = await payment_method_service.delete_payment_method(method_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="Méthode de paiement non trouvée")
	return {"ok": True, "message": "Méthode de paiement supprimée"}

@router.patch("/admin/methods/{method_id}/toggle", tags=["Admin - Payments"])
async def toggle_payment_method(
	method_id: str,
	current_user=Depends(get_admin_user)
):
	"""Activer/désactiver une méthode de paiement (admin only)"""
	method = await payment_method_service.toggle_payment_method(method_id)
	if not method:
		raise HTTPException(status_code=404, detail="Méthode de paiement non trouvée")
	return {
		"id": str(method.id),
		"code": method.code,
		"name": method.name,
		"description": method.description,
		"icon_url": method.icon_url,
		"is_active": method.is_active,
		"order": method.order,
		"min_amount": method.min_amount,
		"max_amount": method.max_amount,
		"created_at": method.created_at,
		"updated_at": method.updated_at
	}
