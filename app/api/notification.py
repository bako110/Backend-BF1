from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user
from app.schemas.notification import NotificationCreate, NotificationOut
from app.services.notification_service import create_notification, get_notification, list_notifications, mark_as_read
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=NotificationOut)
async def add_notification(notification: NotificationCreate, current_user=Depends(get_current_user)):
    return await create_notification(notification)

@router.get("/{user_id}", response_model=List[NotificationOut])
async def get_user_notifications(user_id: str, current_user=Depends(get_current_user)):
    return await list_notifications(user_id)

@router.get("/detail/{notif_id}", response_model=NotificationOut)
async def get_one_notification(notif_id: str, current_user=Depends(get_current_user)):
    notif = await get_notification(notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif

@router.put("/read/{notif_id}")
async def mark_notification_as_read(notif_id: str, current_user=Depends(get_current_user)):
    success = await mark_as_read(notif_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"ok": True}

@router.delete("/{notif_id}")
async def delete_notification(notif_id: str, user_id: str, current_user=Depends(get_current_user)):
    from app.services.notification_service import delete_notification
    success = await delete_notification(notif_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found or not owned by user")
    return {"ok": True}
