
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from typing import List, Optional

async def delete_notification(notif_id: str, user_id: str) -> bool:
	notif = await Notification.get(notif_id)
	if not notif or notif.user_id != user_id:
		return False
	await notif.delete()
	return True

async def create_notification(data: NotificationCreate) -> Notification:
	notif = Notification(**data.dict())
	await notif.insert()
	return notif

async def get_notification(notif_id: str) -> Optional[Notification]:
	return await Notification.get(notif_id)

async def list_notifications(user_id: str) -> List[Notification]:
	return await Notification.find(Notification.user_id == user_id).to_list()

async def mark_as_read(notif_id: str) -> bool:
	notif = await Notification.get(notif_id)
	if not notif:
		return False
	notif.is_read = True
	await notif.save()
	return True
