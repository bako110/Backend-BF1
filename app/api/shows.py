from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_current_user, get_admin_user, get_optional_user
from app.utils.cache import cache_manager
from app.schemas.show import ShowCreate, ShowOut
from app.services.show_service import (
	create_show, get_show, list_shows, update_show, delete_show,
	list_shows_by_category, list_shows_by_edition, list_shows_by_host,
	list_live_shows, list_replay_shows, list_shows_by_date, list_shows_sorted, set_show_live
)
from pydantic import BaseModel

router = APIRouter()

class ShowLiveUpdate(BaseModel):
	is_live: bool
	live_url: str = None

@router.patch("/{show_id}/live", response_model=ShowOut)
async def update_show_live(show_id: str, data: ShowLiveUpdate, current_user=Depends(get_admin_user)):
	show = await set_show_live(show_id, data.is_live, data.live_url)
	if not show:
		raise HTTPException(status_code=404, detail="Show not found")
	return show
@router.post("/", response_model=ShowOut)
async def add_show(show: ShowCreate, current_user=Depends(get_admin_user)):
	result = await create_show(show)
	await cache_manager.delete_pattern("shows:*")
	return result
@router.get("/", response_model=List[ShowOut])
async def get_all_shows(
	sort: str = None,
	order: str = "desc",
	date: str = None,
	page: int = 1,
	page_size: int = 20,
	current_user=Depends(get_optional_user)
):
	cache_key = f"shows:list:{sort}:{order}:{date}:{page}:{page_size}"
	cached = await cache_manager.get(cache_key)
	if cached:
		return cached
	
	if sort:
		shows = await list_shows_sorted(sort, order)
	elif date:
		shows = await list_shows_by_date(date)
	else:
		shows = await list_shows()
	
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

async def update_one_show(show_id: str, show: ShowCreate, current_user=Depends(get_current_user)):
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
