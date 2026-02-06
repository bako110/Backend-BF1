from app.models.reel import Reel
from app.schemas.reel import ReelCreate, ReelUpdate
from typing import List, Optional
from datetime import datetime


async def create_reel(data: ReelCreate) -> Reel:
	reel = Reel(**data.dict())
	await reel.insert()
	return reel


async def get_reel(reel_id: str) -> Optional[Reel]:
	return await Reel.get(reel_id)


async def list_reels(skip: int = 0, limit: int = 50) -> List[Reel]:
	return await Reel.find_all().sort(-Reel.created_at).skip(skip).limit(limit).to_list()


async def update_reel(reel_id: str, data: ReelUpdate) -> Optional[Reel]:
	reel = await Reel.get(reel_id)
	if not reel:
		return None

	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(reel, field, value)

	reel.updated_at = datetime.utcnow()
	await reel.save()
	return reel


async def delete_reel(reel_id: str) -> bool:
	reel = await Reel.get(reel_id)
	if not reel:
		return False
	await reel.delete()
	return True
