from app.models.show import Show
from app.models.like import Like
from app.models.comment import Comment
from app.schemas.show import ShowCreate, ShowUpdate
from typing import List, Optional, Dict
from datetime import datetime


async def set_show_live(show_id: str, is_live: bool, live_url: Optional[str] = None) -> Optional[Show]:
	show = await Show.get(show_id)
	if not show:
		return None
	show.is_live = is_live
	show.stream_url = live_url
	show.updated_at = datetime.utcnow()
	await show.save()
	return show

async def create_show(data: ShowCreate) -> Show:
	show = Show(**data.dict())
	await show.insert()
	return show

async def get_show(show_id: str) -> Optional[Show]:
	return await Show.get(show_id)

async def get_show_with_stats(show_id: str) -> Optional[Dict]:
	"""Récupérer une émission avec statistiques de likes/comments"""
	show = await Show.get(show_id)
	if not show:
		return None
	
	# Compter les likes et comments
	likes_count = await Like.find(
		Like.content_id == show_id,
		Like.content_type == "show"
	).count()
	
	comments_count = await Comment.find(
		Comment.content_id == show_id,
		Comment.content_type == "show"
	).count()
	
	show_dict = show.dict()
	show_dict['likes_count'] = likes_count
	show_dict['comments_count'] = comments_count
	return show_dict

async def list_shows() -> List[Show]:
	return await Show.find_all().to_list()

async def list_shows_by_category(category: str) -> List[Show]:
	return await Show.find(Show.category == category).to_list()

async def list_shows_by_edition(edition: str) -> List[Show]:
	return await Show.find(Show.edition == edition).to_list()

async def list_shows_by_host(host: str) -> List[Show]:
	return await Show.find(Show.host == host).to_list()

async def list_live_shows() -> List[Show]:
	return await Show.find(Show.is_live == True).to_list()

async def list_replay_shows() -> List[Show]:
	return await Show.find(Show.is_replay == True).to_list()

async def list_shows_by_date(date: str) -> List[Show]:
	try:
		date_obj = datetime.strptime(date, "%Y-%m-%d")
	except Exception:
		return []
	return await Show.find({"replay_at": {"$gte": date_obj, "$lt": date_obj.replace(hour=23, minute=59, second=59)}}).to_list()

async def list_shows_sorted(sort: str = "popularity", order: str = "desc") -> List[Show]:
	# Dummy sort by featured for example, real popularity would need a field
	sort_field = "is_featured" if sort == "popularity" else sort
	sort_order = -1 if order == "desc" else 1
	return await Show.find_all().sort([(sort_field, sort_order)]).to_list()

async def update_show(show_id: str, data: ShowUpdate) -> Optional[Show]:
	show = await Show.get(show_id)
	if not show:
		return None
	
	# Mise à jour partielle (seulement les champs fournis)
	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(show, field, value)
	
	show.updated_at = datetime.utcnow()
	await show.save()
	return show

async def delete_show(show_id: str) -> bool:
	show = await Show.get(show_id)
	if not show:
		return False
	await show.delete()
	return True
