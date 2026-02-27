from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_current_user, get_admin_user, get_optional_user
from app.utils.cache import cache_manager
from app.schemas.show import ShowCreate, ShowOut, ShowUpdate
from app.services.show_service import (
	create_show, get_show, list_shows, update_show, delete_show,
	list_shows_by_category, list_shows_by_edition, list_shows_by_host,
	list_live_shows, list_replay_shows, list_shows_by_date, list_shows_sorted, set_show_live
)
from pydantic import BaseModel

router = APIRouter()

class ShowLiveUpdate(BaseModel):
	is_live: bool
	stream_url: str = None

@router.patch("/{show_id}/live", response_model=ShowOut)
async def update_show_live(show_id: str, data: ShowLiveUpdate, current_user=Depends(get_admin_user)):
	show = await set_show_live(show_id, data.is_live, data.stream_url)
	if not show:
		raise HTTPException(status_code=404, detail="Show not found")
	return show
@router.post("/", response_model=ShowOut)
async def add_show(show: ShowCreate, current_user=Depends(get_admin_user)):
	result = await create_show(show)
	await cache_manager.delete_pattern("shows:*")
	
	# Notifier tous les utilisateurs de la nouvelle émission
	try:
		from app.services.notification_service import notify_all_users_new_show
		await notify_all_users_new_show(result.title, str(result.id))
	except Exception as e:
		print(f"⚠️ Erreur envoi notifications nouvelle émission: {e}")
	
	return result
@router.get("/", response_model=List[ShowOut])
async def get_all_shows(
	sort: str = None,
	order: str = "desc",
	date: str = None,
	page: int = 1,
	page_size: int = 20,
	search: str = None,
	current_user=Depends(get_optional_user)
):
	cache_key = f"shows:list:{sort}:{order}:{date}:{page}:{page_size}:{search}"
	cached = await cache_manager.get(cache_key)
	if cached:
		return cached
	
	if sort:
		shows = await list_shows_sorted(sort, order)
	elif date:
		shows = await list_shows_by_date(date)
	
	# Recherche si un terme est fourni
	if search:
		search_lower = search.lower()
		print(f"🔍 [SHOWS] Recherche complète: '{search}'")
		
		# Obtenir toutes les émissions sans pagination d'abord
		all_shows = await list_shows()
		
		# Recherche complète dans tous les champs
		filtered_shows = []
		for show in all_shows:
			# Recherche dans tous les champs disponibles
			title_match = search_lower in show.title.lower()
			desc_match = show.description and search_lower in show.description.lower()
			host_match = hasattr(show, 'host') and show.host and search_lower in show.host.lower()
			category_match = hasattr(show, 'category') and show.category and search_lower in show.category.lower()
			edition_match = hasattr(show, 'edition') and show.edition and search_lower in show.edition.lower()
			sub_category_match = hasattr(show, 'sub_category') and show.sub_category and search_lower in show.sub_category.lower()
			tags_match = hasattr(show, 'tags') and show.tags and any(search_lower in tag.lower() for tag in show.tags)
			season_match = hasattr(show, 'season') and show.season and search_lower in str(show.season).lower()
			episode_match = hasattr(show, 'episode') and show.episode and search_lower in str(show.episode).lower()
			
			if title_match or desc_match or host_match or category_match or edition_match or sub_category_match or tags_match or season_match or episode_match:
				filtered_shows.append(show)
				print(f"✅ [SHOWS] Match trouvé: '{show.title}' (titre:{title_match}, desc:{desc_match}, host:{host_match}, cat:{category_match}, edition:{edition_match})")
		
		print(f"🎯 [SHOWS] Résultats après recherche complète: {len(filtered_shows)}")
		
		# Appliquer les autres filtres si nécessaire
		if sort:
			if sort == "date":
				filtered_shows.sort(key=lambda x: getattr(x, 'created_at', x.updated_at or datetime.min), reverse=(order == "desc"))
			elif sort == "title":
				filtered_shows.sort(key=lambda x: x.title.lower(), reverse=(order == "desc"))
			elif sort == "views":
				filtered_shows.sort(key=lambda x: getattr(x, 'views', 0), reverse=(order == "desc"))
		
		# Pagination sur les résultats filtrés
		total_filtered = len(filtered_shows)
		start = (page - 1) * page_size
		end = start + page_size
		shows = filtered_shows[start:end]
		
		result_shows = shows
		total_count = total_filtered
	else:
		# Recherche normale sans terme de recherche
		if sort:
			shows = await list_shows_sorted(sort, order)
		elif date:
			shows = await list_shows_by_date(date)
		else:
			shows = await list_shows()
		
		# Pagination normale
		total_count = len(shows)
		start = (page - 1) * page_size
		end = start + page_size
		shows = shows[start:end]
		
		result_shows = shows
	
	# Pagination
	start = (page - 1) * page_size
	end = start + page_size
	shows = shows[start:end]
	
	await cache_manager.set(cache_key, shows, ttl=300)
	return shows

# Filtrer par catégorie
@router.get("/category/{category}", response_model=List[ShowOut])
async def get_shows_by_category(category: str, current_user=Depends(get_optional_user)):
	return await list_shows_by_category(category)

# Filtrer par édition (ex: Journal 13H30, 19H30)
@router.get("/edition/{edition}", response_model=List[ShowOut])
async def get_shows_by_edition(edition: str, current_user=Depends(get_optional_user)):
	return await list_shows_by_edition(edition)

# Filtrer par animateur
@router.get("/host/{host}", response_model=List[ShowOut])
async def get_shows_by_host(host: str, current_user=Depends(get_optional_user)):
	return await list_shows_by_host(host)

# Filtrer les émissions en direct
@router.get("/live", response_model=List[ShowOut])
async def get_live_shows(current_user=Depends(get_optional_user)):
	cache_key = "shows:live"
	cached = await cache_manager.get(cache_key)
	if cached:
		return cached
	shows = await list_live_shows()
	await cache_manager.set(cache_key, shows, ttl=60)
	return shows

# Filtrer les émissions en replay
@router.get("/replay", response_model=List[ShowOut])
async def get_replay_shows(current_user=Depends(get_optional_user)):
	cache_key = "shows:replay"
	cached = await cache_manager.get(cache_key)
	if cached:
		return cached
	shows = await list_replay_shows()
	await cache_manager.set(cache_key, shows, ttl=300)
	return shows
@router.get("/{show_id}", response_model=ShowOut)

async def get_one_show(show_id: str, current_user=Depends(get_optional_user)):
	show = await get_show(show_id)
	if not show:
		raise HTTPException(status_code=404, detail="Show not found")
	return show
@router.put("/{show_id}", response_model=ShowOut)

async def update_one_show(show_id: str, show: ShowUpdate, current_user=Depends(get_current_user)):
	updated = await update_show(show_id, show)
	if not updated:
		raise HTTPException(status_code=404, detail="Show not found")
	await cache_manager.delete_pattern("shows:*")
	return updated

@router.delete("/{show_id}")
async def delete_one_show(show_id: str, current_user=Depends(get_current_user)):
	deleted = await delete_show(show_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="Show not found")
	await cache_manager.delete_pattern("shows:*")
	return {"ok": True}
# Endpoints émissions
