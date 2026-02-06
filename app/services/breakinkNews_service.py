from app.models.breakingNews import BreakingNews
from app.schemas.breakingNews import BreakingNewsCreate, BreakingNewsUpdate
from typing import List, Optional
from datetime import datetime


async def create_news(data: BreakingNewsCreate) -> BreakingNews:
	news = BreakingNews(**data.dict())
	await news.insert()
	return news


async def get_news(news_id: str) -> Optional[BreakingNews]:
	return await BreakingNews.get(news_id)


async def list_news(skip: int = 0, limit: int = 50) -> List[BreakingNews]:
	"""Lister les breaking news avec pagination"""
	return await BreakingNews.find_all().sort(-BreakingNews.created_at).skip(skip).limit(limit).to_list()


async def update_news(news_id: str, data: BreakingNewsUpdate) -> Optional[BreakingNews]:
	"""Mettre à jour une breaking news"""
	news = await BreakingNews.get(news_id)
	if not news:
		return None

	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(news, field, value)

	news.updated_at = datetime.utcnow()
	await news.save()
	return news


async def delete_news(news_id: str) -> bool:
	"""Supprimer une breaking news"""
	news = await BreakingNews.get(news_id)
	if not news:
		return False
	await news.delete()
	return True
