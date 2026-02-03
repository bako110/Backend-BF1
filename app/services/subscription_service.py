from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate
from typing import List, Optional

async def get_all_subscriptions(skip: int = 0, limit: int = 1000) -> List:
    """Récupérer tous les abonnements (pour admin)"""
    subscriptions = await Subscription.find().skip(skip).limit(limit).to_list()
    return [sub.dict() for sub in subscriptions]

async def create_subscription(data: SubscriptionCreate) -> Subscription:
	sub = Subscription(**data.dict())
	await sub.insert()
	
	# Mettre à jour le statut premium de l'utilisateur
	from app.models.user import User
	user = await User.get(data.user_id)
	if user:
		user.is_premium = True
		await user.save()
		
		# Envoyer une notification premium
		try:
			from app.services.notification_service import send_premium_notification
			await send_premium_notification(data.user_id)
		except Exception as e:
			print(f"⚠️ Erreur envoi notification premium: {e}")
	
	return sub

async def get_subscription(sub_id: str) -> Optional[Subscription]:
	return await Subscription.get(sub_id)

async def list_subscriptions(user_id: str) -> List[Subscription]:
	return await Subscription.find(Subscription.user_id == user_id).to_list()

async def cancel_subscription(sub_id: str) -> bool:
	sub = await Subscription.get(sub_id)
	if not sub:
		return False
	sub.is_active = False
	await sub.save()
	return True
