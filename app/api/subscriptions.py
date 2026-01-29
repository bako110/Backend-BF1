from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.subscription import SubscriptionCreate, SubscriptionOut
from app.services.subscription_service import create_subscription, get_subscription, list_subscriptions, cancel_subscription
from typing import List

router = APIRouter()

@router.post("/")
async def add_subscription(sub: SubscriptionCreate, current_user=Depends(get_current_user)):
    """Créer un abonnement"""
    return await create_subscription(sub)

@router.get("/me")
async def get_my_subscriptions(current_user=Depends(get_current_user)):
    """Récupérer mes abonnements"""
    return await list_subscriptions(str(current_user.id))

@router.get("/user/{user_id}")
async def get_user_subs(user_id: str, current_user=Depends(get_admin_user)):
    """Récupérer les abonnements d'un utilisateur (admin)"""
    return await list_subscriptions(user_id)

@router.get("/{sub_id}")
async def get_one_sub(sub_id: str, current_user=Depends(get_current_user)):
    """Récupérer un abonnement par ID"""
    sub = await get_subscription(sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub

@router.patch("/{sub_id}/cancel")
async def cancel_sub(sub_id: str, current_user=Depends(get_current_user)):
    """Annuler un abonnement"""
    ok = await cancel_subscription(sub_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"ok": True}
