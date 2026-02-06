from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.trendingShow import TrendingShowCreate, TrendingShowUpdate, TrendingShowOut
from app.services.trendingShow_service import (
	create_trending_show, get_trending_show, list_trending_shows, update_trending_show, delete_trending_show
)

router = APIRouter()


@router.post("/", response_model=TrendingShowOut)
async def add_trending_show(show: TrendingShowCreate, current_user=Depends(get_admin_user)):
	return await create_trending_show(show)


@router.get("/", response_model=List[TrendingShowOut])
async def get_all_trending_shows(
	skip: int = 0,
	limit: int = 50,
	current_user=Depends(get_optional_user)
):
	return await list_trending_shows(skip, limit)


@router.get("/{show_id}", response_model=TrendingShowOut)
async def get_one_trending_show(show_id: str, current_user=Depends(get_optional_user)):
	show = await get_trending_show(show_id)
	if not show:
		raise HTTPException(status_code=404, detail="Trending show not found")
	return show


@router.patch("/{show_id}", response_model=TrendingShowOut)
async def update_one_trending_show(show_id: str, data: TrendingShowUpdate, current_user=Depends(get_admin_user)):
	updated = await update_trending_show(show_id, data)
	if not updated:
		raise HTTPException(status_code=404, detail="Trending show not found")
	return updated


@router.delete("/{show_id}")
async def delete_one_trending_show(show_id: str, current_user=Depends(get_admin_user)):
	deleted = await delete_trending_show(show_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="Trending show not found")
	return {"ok": True}
