from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.jtandmag import JTandMagCreate, JTandMagUpdate, JTandMagOut
from app.services.jtandmag_service import (
	create_jtandmag, get_jtandmag, list_jtandmag, update_jtandmag, delete_jtandmag
)

router = APIRouter()


@router.post("", response_model=JTandMagOut)
async def add_jtandmag(jtandmag: JTandMagCreate, current_user=Depends(get_admin_user)):
	return await create_jtandmag(jtandmag)


@router.get("", response_model=List[JTandMagOut])
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
		print(f"🔍 [JTANDMAG] Recherche complète: '{search}'")
		
		# Obtenir tous les JT et Mag sans pagination d'abord
		all_jtandmag = await list_jtandmag(0, 1000)  # Grande limite pour obtenir tous
		
		# Recherche complète dans tous les champs
		filtered_jtandmag = []
		for jtm in all_jtandmag:
			# Recherche dans tous les champs disponibles (avec vérification sécurisée)
			title_match = search_lower in jtm.title.lower()
			desc_match = jtm.description and search_lower in jtm.description.lower()
			host_match = hasattr(jtm, 'host') and jtm.host and search_lower in jtm.host.lower()
			category_match = hasattr(jtm, 'category') and jtm.category and search_lower in jtm.category.lower()
			edition_match = hasattr(jtm, 'edition') and jtm.edition and search_lower in jtm.edition.lower()
			sub_category_match = hasattr(jtm, 'sub_category') and jtm.sub_category and search_lower in jtm.sub_category.lower()
			rating_match = hasattr(jtm, 'rating') and jtm.rating and search_lower in str(jtm.rating).lower()
			tags_match = hasattr(jtm, 'tags') and jtm.tags and any(search_lower in tag.lower() for tag in jtm.tags)
			
			if title_match or desc_match or host_match or category_match or edition_match or sub_category_match or rating_match or tags_match:
				filtered_jtandmag.append(jtm)
				print(f"✅ [JTANDMAG] Match trouvé: '{jtm.title}' (titre:{title_match}, desc:{desc_match}, host:{host_match}, cat:{category_match}, edition:{edition_match})")
		
		print(f"🎯 [JTANDMAG] Résultats après recherche complète: {len(filtered_jtandmag)}")
		
		# Pagination sur les résultats filtrés
		jtandmags = filtered_jtandmag[skip:skip + limit]
	
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
