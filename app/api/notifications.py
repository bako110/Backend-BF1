from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.notification import NotificationCreate, NotificationOut
from app.services.notification_service import create_notification, get_notification, list_notifications, mark_as_read, delete_notification
from typing import List

router = APIRouter()

@router.post("/", response_model=NotificationOut)
async def add_notification(notification: NotificationCreate, current_user=Depends(get_admin_user)):
	"""Créer une notification (admin ou broadcast)"""
	return await create_notification(notification)

@router.get("/me")
async def get_my_notifications(current_user=Depends(get_current_user)):
	"""Récupérer mes notifications"""
	return await list_notifications(str(current_user.id))

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
	unread_count = sum(1 for n in notifications if not n.get('is_read', False))
	return {"count": unread_count}

@router.delete("/{notif_id}")
async def delete_notif(notif_id: str, current_user=Depends(get_current_user)):
	"""Supprimer une notification"""
	ok = await delete_notification(notif_id, str(current_user.id))
	if not ok:
		raise HTTPException(status_code=404, detail="Notification not found or unauthorized")
	return {"ok": True}
