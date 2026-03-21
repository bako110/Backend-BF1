from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.subscription import SubscriptionCreate, SubscriptionOut
from app.services.subscription_service import (
    create_subscription, 
    get_subscription, 
    list_subscriptions, 
    cancel_subscription, 
    get_all_subscriptions,
    sync_user_premium_status,
    check_user_has_active_subscription,
    deactivate_expired_subscriptions
)
from typing import List

router = APIRouter()

@router.get("")
async def list_all_subscriptions(current_user=Depends(get_admin_user), skip: int = 0, limit: int = 1000):
    """Lister tous les abonnements (admin seulement)"""
    return await get_all_subscriptions(skip, limit)

@router.post("")
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

@router.post("/sync-premium-status")
async def sync_premium_status(current_user=Depends(get_current_user)):
    """Synchroniser le statut premium de l'utilisateur actuel"""
    is_premium = await sync_user_premium_status(str(current_user.id))
    return {
        "user_id": str(current_user.id),
        "is_premium": is_premium,
        "message": "Statut premium synchronisé"
    }

@router.get("/check-premium-status")
async def check_premium_status(current_user=Depends(get_current_user)):
    """Vérifier si l'utilisateur actuel a un abonnement actif"""
    has_active = await check_user_has_active_subscription(str(current_user.id))
    return {
        "user_id": str(current_user.id),
        "has_active_subscription": has_active,
        "current_is_premium": current_user.is_premium
    }

@router.post("/admin/deactivate-expired")
async def admin_deactivate_expired(current_user=Depends(get_admin_user)):
    """Désactiver tous les abonnements expirés (admin seulement)"""
    count = await deactivate_expired_subscriptions()
    return {
        "deactivated_count": count,
        "message": f"{count} abonnements expirés ont été désactivés"
    }

@router.post("/admin/sync-all-users")
async def admin_sync_all_users(current_user=Depends(get_admin_user)):
    """Synchroniser le statut premium de tous les utilisateurs (admin seulement)"""
    from app.models.user import User
    
    users = await User.find_all().to_list()
    synced = 0
    updated = 0
    
    for user in users:
        old_status = user.is_premium
        new_status = await sync_user_premium_status(str(user.id))
        
        if old_status != new_status:
            updated += 1
        
        synced += 1
    
    return {
        "synced_users": synced,
        "updated_users": updated,
        "message": f"{synced} utilisateurs synchronisés, {updated} mis à jour"
    }
