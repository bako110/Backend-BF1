from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.reel import ReelCreate, ReelUpdate, ReelOut
from app.services.reel_service import create_reel, get_reel, list_reels, update_reel, delete_reel

router = APIRouter()


@router.post("/", response_model=ReelOut)
async def add_reel(reel: ReelCreate, current_user=Depends(get_admin_user)):
	return await create_reel(reel)


@router.get("/", response_model=List[ReelOut])
async def get_all_reels(
	skip: int = 0,
	limit: int = 50,
	current_user=Depends(get_optional_user)
):
	return await list_reels(skip, limit)


@router.get("/{reel_id}", response_model=ReelOut)
async def get_one_reel(reel_id: str, current_user=Depends(get_optional_user)):
	reel = await get_reel(reel_id)
	if not reel:
		raise HTTPException(status_code=404, detail="Reel not found")
	return reel


@router.patch("/{reel_id}", response_model=ReelOut)
async def update_one_reel(reel_id: str, data: ReelUpdate, current_user=Depends(get_admin_user)):
	updated = await update_reel(reel_id, data)
	if not updated:
		raise HTTPException(status_code=404, detail="Reel not found")
	return updated


@router.delete("/{reel_id}")
async def delete_one_reel(reel_id: str, current_user=Depends(get_admin_user)):
	deleted = await delete_reel(reel_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="Reel not found")
	return {"ok": True}
