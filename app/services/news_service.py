from app.models.news import News
from app.schemas.news import NewsCreate, NewsUpdate
from typing import List, Optional
from datetime import datetime

async def set_news_live(news_id: str, is_live: bool, live_url: Optional[str] = None) -> Optional[News]:
	"""Mettre à jour le statut live d'une news"""
	news = await News.get(news_id)
	if not news:
		return None
	news.is_live = is_live
	news.live_url = live_url
	await news.save()
	return news

async def create_news(data: NewsCreate) -> News:
	news = News(**data.dict())
	await news.insert()
	return news

async def get_news(news_id: str) -> Optional[News]:
	return await News.get(news_id)

async def list_news(skip: int = 0, limit: int = 50) -> List[News]:
	"""Lister les news avec pagination"""
	return await News.find_all().sort(-News.published_at).skip(skip).limit(limit).to_list()

async def list_news_by_edition(edition: str, skip: int = 0, limit: int = 50) -> List[News]:
	"""Lister les news par édition"""
	return await News.find(News.edition == edition).sort(-News.published_at).skip(skip).limit(limit).to_list()

async def list_live_news() -> List[News]:
	"""Lister les news en direct"""
	return await News.find(News.is_live == True).to_list()

async def list_news_by_date(date: str) -> List[News]:
	"""Lister les news par date"""
	try:
		date_obj = datetime.strptime(date, "%Y-%m-%d")
	except Exception:
		return []
	return await News.find({"published_at": {"$gte": date_obj, "$lt": date_obj.replace(hour=23, minute=59, second=59)}}).to_list()

async def update_news(news_id: str, data: NewsUpdate) -> Optional[News]:
	"""Mettre à jour une news"""
	news = await News.get(news_id)
	if not news:
		return None
	
	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(news, field, value)
	
	await news.save()
	return news

async def delete_news(news_id: str) -> bool:
	"""Supprimer une news"""
	news = await News.get(news_id)
	if not news:
		return False
	await news.delete()
	return True
