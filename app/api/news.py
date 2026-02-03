from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user, get_optional_user
from app.schemas.news import NewsCreate, NewsOut, NewsUpdate
from app.services.news_service import (
	create_news, get_news, list_news, update_news, delete_news,
	list_news_by_edition, list_live_news, list_news_by_date, set_news_live
)
from pydantic import BaseModel
from typing import List

router = APIRouter()

class NewsLiveUpdate(BaseModel):
	is_live: bool
	live_url: str = None

@router.post("/", response_model=NewsOut)
async def add_news(news: NewsCreate, current_user=Depends(get_admin_user)):
	new_news = await create_news(news)
	
	# Notifier tous les utilisateurs de la nouvelle actualité
	try:
		from app.services.notification_service import notify_all_users_new_news
		await notify_all_users_new_news(new_news.title, str(new_news.id))
	except Exception as e:
		print(f"⚠️ Erreur envoi notifications nouvelle actualité: {e}")
	
	return new_news

@router.get("/")
async def get_all_news(
	skip: int = 0,
	limit: int = 50,
	date: str = None,
	current_user=Depends(get_optional_user)
):
	"""Lister les news avec pagination"""
	if date:
		return await list_news_by_date(date)
	return await list_news(skip, limit)

# Liste des journaux par édition
@router.get("/edition/{edition}")
async def get_news_by_edition(edition: str, skip: int = 0, limit: int = 50, current_user=Depends(get_optional_user)):
	"""Lister les news par édition"""
	return await list_news_by_edition(edition, skip, limit)

@router.get("/live")
async def get_live_news(current_user=Depends(get_optional_user)):
	"""Lister les news en direct"""
	return await list_live_news()

@router.get("/{news_id}")
async def get_one_news(news_id: str, current_user=Depends(get_optional_user)):
	"""Récupérer une news par ID"""
	news = await get_news(news_id)
	if not news:
		raise HTTPException(status_code=404, detail="News not found")
	return news

@router.patch("/{news_id}")
async def update_one_news(news_id: str, data: NewsUpdate, current_user=Depends(get_admin_user)):
	"""Mettre à jour une news (admin seulement)"""
	updated = await update_news(news_id, data)
	if not updated:
		raise HTTPException(status_code=404, detail="News not found")
	return updated

@router.patch("/{news_id}/live")
async def update_news_live(news_id: str, data: NewsLiveUpdate, current_user=Depends(get_admin_user)):
	"""Mettre à jour le statut live d'une news"""
	news = await set_news_live(news_id, data.is_live, data.live_url)
	if not news:
		raise HTTPException(status_code=404, detail="News not found")
	return news

@router.delete("/{news_id}")
async def delete_one_news(news_id: str, current_user=Depends(get_admin_user)):
	"""Supprimer une news (admin seulement)"""
	deleted = await delete_news(news_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="News not found")
	return {"ok": True}
