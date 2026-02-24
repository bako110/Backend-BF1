from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.jtandmag import JTandMagCreate, JTandMagUpdate, JTandMagOut
from app.services.jtandmag_service import (
	create_jtandmag, get_jtandmag, list_jtandmag, update_jtandmag, delete_jtandmag
)

router = APIRouter()


@router.post("/", response_model=JTandMagOut)
async def add_jtandmag(jtandmag: JTandMagCreate, current_user=Depends(get_admin_user)):
	return await create_jtandmag(jtandmag)


@router.get("/", response_model=List[JTandMagOut])
async def get_all_jtandmag(
	skip: int = 0, 
	limit: int = 50,
	search: str = None,
	current_user=Depends(get_optional_user)
):
	jtandmags = await list_jtandmag(skip, limit)
	
	# Si un terme de recherche est fourni, filtrer les résultats
	if search:
		search_lower = search.lower()
		jtandmags = [
			jtm for jtm in jtandmags
			if search_lower in jtm.title.lower() or
			   (jtm.description and search_lower in jtm.description.lower()) or
			   (jtm.host and search_lower in jtm.host.lower()) or
			   (jtm.edition and search_lower in jtm.edition.lower())
		]
	
	return jtandmags


@router.get("/{jtandmag_id}", response_model=JTandMagOut)
async def get_one_jtandmag(jtandmag_id: str, current_user=Depends(get_optional_user)):
	jtandmag = await get_jtandmag(jtandmag_id)
	if not jtandmag:
		raise HTTPException(status_code=404, detail="JT and Mag not found")
	return jtandmag


@router.put("/{jtandmag_id}", response_model=JTandMagOut)
async def update_one_jtandmag(jtandmag_id: str, jtandmag: JTandMagUpdate, current_user=Depends(get_admin_user)):
	updated_jtandmag = await update_jtandmag(jtandmag_id, jtandmag)
	if not updated_jtandmag:
		raise HTTPException(status_code=404, detail="JT and Mag not found")
	return updated_jtandmag


@router.delete("/{jtandmag_id}")
async def delete_one_jtandmag(jtandmag_id: str, current_user=Depends(get_admin_user)):
	success = await delete_jtandmag(jtandmag_id)
	if not success:
		raise HTTPException(status_code=404, detail="JT and Mag not found")
	return {"message": "JT and Mag deleted successfully"}
