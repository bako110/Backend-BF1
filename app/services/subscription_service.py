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
