from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_current_user, get_optional_user, get_admin_user
from app.services.subscription_service import list_subscriptions

router = APIRouter()

@router.get("/")
async def get_premium_content(current_user=Depends(get_optional_user)):
	"""Lister le contenu premium disponible"""
	return {
		"items": [],
		"total": 0,
		"message": "Pas de contenu premium pour le moment"
	}

@router.get("/offer")
async def get_premium_offer():
	"""Obtenir l'offre premium actuelle"""
	return {
		"name": "Abonnement Premium",
		"price": 5000,
		"currency": "XOF",
		"duration": 30,
		"description": "Accès complet à tous les contenus premium"
	}

@router.get("/me")
async def get_user_premium_status(current_user=Depends(get_current_user)):
	"""Vérifier si l'utilisateur a un accès premium actif"""
	subs = await list_subscriptions(str(current_user.id))
	active_subs = [s for s in subs if s.is_active]
	
	if not active_subs:
		return {"has_premium": False, "message": "Aucun abonnement actif"}
	
	return {
		"has_premium": True,
		"subscription": active_subs[0],
		"message": "Accès premium actif"
	}

@router.get("/stats")
async def get_premium_stats(current_user=Depends(get_admin_user)):
	"""Statistiques premium (admin seulement)"""
	return {
		"total_subscribers": 0,
		"active_subscriptions": 0,
		"revenue": 0,
		"currency": "XOF"
	}

@router.patch("/{content_id}/toggle")
async def toggle_premium_content(content_id: str, current_user=Depends(get_admin_user)):
	"""Basculer le statut premium d'un contenu"""
	return {"ok": True, "content_id": content_id, "message": "Statut premium mis à jour"}

@router.get("/check")
async def check_premium_access(current_user=Depends(get_current_user)):
	"""Vérifier si l'utilisateur a un accès premium actif"""
	subs = await list_subscriptions(str(current_user.id))
	active_subs = [s for s in subs if s.is_active]
	
	if not active_subs:
		return {"has_premium": False, "message": "Aucun abonnement actif"}
	
	return {
		"has_premium": True,
		"subscription": active_subs[0],
		"message": "Accès premium actif"
	}

@router.get("/benefits")
async def get_premium_benefits():
	"""Lister les avantages de l'abonnement premium"""
	return {
		"benefits": [
			"Accès à tous les films premium",
			"Visionnage sans publicité",
			"Qualité HD/4K",
			"Téléchargement hors ligne",
			"Accès anticipé aux nouvelles émissions"
		],
		"pricing": {
			"monthly": {"amount": 5000, "currency": "XOF"},
			"yearly": {"amount": 50000, "currency": "XOF", "discount": "2 mois gratuits"}
		}
	}
