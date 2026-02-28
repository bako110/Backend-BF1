from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.breakingNews import BreakingNewsCreate, BreakingNewsOut, BreakingNewsUpdate
from app.services.breakinkNews_service import create_news, get_news, list_news, update_news, delete_news
from typing import List

router = APIRouter()

@router.post("/", response_model=BreakingNewsOut)
async def add_news(news: BreakingNewsCreate, current_user=Depends(get_admin_user)):
	new_news = await create_news(news)
	
	# Notifier tous les utilisateurs de la nouvelle actualité
	try:
		# Notification push pour les mobiles
		from app.services.push_notification_service import push_notification_service
		await push_notification_service.send_flash_info_notification({
			'title': new_news.title,
			'description': new_news.description,
			'_id': str(new_news.id)
		})
		
		# Notification système existante
		from app.services.notification_service import notify_all_users_new_news
		await notify_all_users_new_news(new_news.title, str(new_news.id))
	except Exception as e:
		print(f"⚠️ Erreur envoi notifications nouvelle actualité: {e}")
	
	return new_news

@router.get("/", response_model=List[BreakingNewsOut])
async def get_all_news(
	skip: int = 0,
	limit: int = 50,
	search: str = None,
	current_user=Depends(get_optional_user)
):
	"""Lister les breaking news avec pagination et recherche optionnelle"""
	news_list = await list_news(skip, limit)
	
	print(f"🔍 [NEWS] Recherche: '{search}', total avant filtrage: {len(news_list)}")
	
	# Si un terme de recherche est fourni, filtrer les résultats
	if search:
		search_lower = search.lower()
		filtered_news = []
		for news in news_list:
			title_match = search_lower in news.title.lower()
			desc_match = news.description and search_lower in news.description.lower()
			cat_match = news.category and search_lower in news.category.lower()
			
			if title_match or desc_match or cat_match:
				filtered_news.append(news)
				print(f"✅ [NEWS] Match trouvé: '{news.title}' (titre:{title_match}, desc:{desc_match}, cat:{cat_match})")
		
		news_list = filtered_news
		print(f"🎯 [NEWS] Résultats après filtrage: {len(news_list)}")
	
	return news_list

@router.get("/test-search")
async def test_search():
	"""Endpoint de test pour diagnostiquer la recherche"""
	news_list = await list_news(0, 100)  # Toutes les news
	
	result = {
		"total_news": len(news_list),
		"sample_titles": [news.title for news in news_list[:5]],
		"sample_data": [
			{
				"id": news.id,
				"title": news.title,
				"description": news.description,
				"category": getattr(news, 'category', None)
			} for news in news_list[:3]
		]
	}
	
	print(f"🧪 [TEST] Total news: {len(news_list)}")
	return result

@router.patch("/{news_id}", response_model=BreakingNewsOut)
async def update_one_news(news_id: str, data: BreakingNewsUpdate, current_user=Depends(get_admin_user)):
	"""Mettre à jour une breaking news (admin seulement)"""
	updated = await update_news(news_id, data)
	if not updated:
		raise HTTPException(status_code=404, detail="News not found")
	return updated

from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.breakingNews import BreakingNewsCreate, BreakingNewsOut, BreakingNewsUpdate
from app.services.breakinkNews_service import create_news, get_news, list_news, update_news, delete_news
from typing import List

router = APIRouter()

@router.post("/", response_model=BreakingNewsOut)
async def add_news(news: BreakingNewsCreate, current_user=Depends(get_admin_user)):
	new_news = await create_news(news)
	
	# Notifier tous les utilisateurs de la nouvelle actualité
	try:
		# Notification push pour les mobiles
		from app.services.push_notification_service import push_notification_service
		await push_notification_service.send_flash_info_notification({
			'title': new_news.title,
			'description': new_news.description,
			'_id': str(new_news.id)
		})
		
		# Notification système existante
		from app.services.notification_service import notify_all_users_new_news
		await notify_all_users_new_news(new_news.title, str(new_news.id))
	except Exception as e:
		print(f"⚠️ Erreur envoi notifications nouvelle actualité: {e}")
	
	return new_news

@router.get("/", response_model=List[BreakingNewsOut])
async def get_all_news(
	skip: int = 0,
	limit: int = 50,
	search: str = None,
	current_user=Depends(get_optional_user)
):
	"""Lister les breaking news avec pagination et recherche optionnelle"""
	news_list = await list_news(skip, limit)
	
	# Si un terme de recherche est fourni, filtrer les résultats
	if search:
		search_lower = search.lower()
		news_list = [
			news for news in news_list
			if search_lower in news.title.lower() or
			   (news.description and search_lower in news.description.lower()) or
			   (news.category and search_lower in news.category.lower())
		]
	
	return news_list

@router.get("/{news_id}", response_model=BreakingNewsOut)
async def get_one_news(news_id: str, current_user=Depends(get_optional_user)):
	"""Récupérer une breaking news par ID"""
	news = await get_news(news_id)
	if not news:
		raise HTTPException(status_code=404, detail="News not found")
	return news

@router.patch("/{news_id}", response_model=BreakingNewsOut)
async def update_one_news(news_id: str, data: BreakingNewsUpdate, current_user=Depends(get_admin_user)):
	"""Mettre à jour une breaking news (admin seulement)"""
	updated = await update_news(news_id, data)
	if not updated:
		raise HTTPException(status_code=404, detail="News not found")
	return updated

@router.delete("/{news_id}")
async def delete_one_news(news_id: str, current_user=Depends(get_admin_user)):
	"""Supprimer une news (admin seulement)"""
	deleted = await delete_news(news_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="News not found")
	return {"ok": True}
	
@router.delete("/{news_id}")
async def delete_one_news(news_id: str, current_user=Depends(get_admin_user)):
	"""Supprimer une news (admin seulement)"""
	deleted = await delete_news(news_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="News not found")
	return {"ok": True}
