from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user
from app.services.subscription_service import list_subscriptions

router = APIRouter()

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
