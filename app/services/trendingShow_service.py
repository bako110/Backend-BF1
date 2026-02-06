from app.models.trendingShow import TrendingShow
from app.schemas.trendingShow import TrendingShowCreate, TrendingShowUpdate
from typing import List, Optional
from datetime import datetime


async def create_trending_show(data: TrendingShowCreate) -> TrendingShow:
	show = TrendingShow(**data.dict())
	await show.insert()
	return show


async def get_trending_show(show_id: str) -> Optional[TrendingShow]:
	return await TrendingShow.get(show_id)


async def list_trending_shows(skip: int = 0, limit: int = 50) -> List[TrendingShow]:
	return await TrendingShow.find_all().sort(-TrendingShow.created_at).skip(skip).limit(limit).to_list()


async def update_trending_show(show_id: str, data: TrendingShowUpdate) -> Optional[TrendingShow]:
	show = await TrendingShow.get(show_id)
	if not show:
		return None

	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(show, field, value)

	show.updated_at = datetime.utcnow()
	await show.save()
	return show


async def delete_trending_show(show_id: str) -> bool:
	show = await TrendingShow.get(show_id)
	if not show:
		return False
	await show.delete()
	return True
