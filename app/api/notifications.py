from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.notification import NotificationCreate, NotificationOut, AdminNotificationGlobal, AdminNotificationIndividual
from app.services.notification_service import (
	create_notification, get_notification, list_notifications, mark_as_read,
	delete_notification, mark_all_as_read, delete_all_notifications,
	send_global_notification, send_individual_notification
)
from typing import List

router = APIRouter()

# ─── Endpoints Admin ──────────────────────────────────────────────────────────

@router.post("/admin/global", tags=["Admin - Notifications"])
async def admin_send_global(body: AdminNotificationGlobal, current_user=Depends(get_admin_user)):
	"""[ADMIN] Envoyer une notification à TOUS les utilisateurs"""
	count = await send_global_notification(body.title, body.message, body.category)
	return {"ok": True, "sent_to": count}

@router.post("/admin/individual", response_model=NotificationOut, tags=["Admin - Notifications"])
async def admin_send_individual(body: AdminNotificationIndividual, current_user=Depends(get_admin_user)):
	"""[ADMIN] Envoyer une notification à un utilisateur spécifique"""
	notif = await send_individual_notification(body.user_id, body.title, body.message, body.category)
	if not notif:
		raise HTTPException(status_code=404, detail="Utilisateur introuvable")
	return notif

@router.get("/me", response_model=List[NotificationOut])
async def get_my_notifications(current_user=Depends(get_current_user)):
	"""Récupérer mes notifications non lues"""
	return await list_notifications(str(current_user.id), unread_only=True)

@router.get("/user/{user_id}")
async def get_user_notifications(user_id: str, current_user=Depends(get_current_user)):
	"""Récupérer les notifications d'un utilisateur"""
	return await list_notifications(user_id)

@router.get("/{notif_id}")
async def get_one_notification(notif_id: str, current_user=Depends(get_current_user)):
	"""Récupérer une notification par ID"""
	notif = await get_notification(notif_id)
	if not notif:
		raise HTTPException(status_code=404, detail="Notification not found")
	return notif

@router.patch("/{notif_id}/read")
async def mark_notification_read(notif_id: str, current_user=Depends(get_current_user)):
	"""Marquer une notification comme lue"""
	ok = await mark_as_read(notif_id)
	if not ok:
		raise HTTPException(status_code=404, detail="Notification not found")
	return {"ok": True}

@router.get("/unread/count")
async def get_unread_count(current_user=Depends(get_current_user)):
	"""Compter les notifications non lues"""
	notifications = await list_notifications(str(current_user.id))
	unread_count = sum(1 for n in notifications if not n.is_read)
	return {"count": unread_count}

@router.patch("/mark-all-read")
async def mark_all_notifications_read(current_user=Depends(get_current_user)):
	"""Marquer toutes les notifications comme lues"""
	count = await mark_all_as_read(str(current_user.id))
	return {"ok": True, "count": count}

@router.delete("/delete-all")
async def delete_all_notifs(current_user=Depends(get_current_user)):
	"""Supprimer toutes les notifications"""
	count = await delete_all_notifications(str(current_user.id))
	return {"ok": True, "count": count}

@router.delete("/{notif_id}")
async def delete_notif(notif_id: str, current_user=Depends(get_current_user)):
	"""Supprimer une notification"""
	ok = await delete_notification(notif_id, str(current_user.id))
	if not ok:
		raise HTTPException(status_code=404, detail="Notification not found or unauthorized")
	return {"ok": True}
