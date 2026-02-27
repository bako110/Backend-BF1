from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.divertissement import DivertissementCreate, DivertissementUpdate, DivertissementOut
from app.services.divertissement_service import (
	create_divertissement, get_divertissement, list_divertissement, update_divertissement, delete_divertissement
)

router = APIRouter()


@router.post("/", response_model=DivertissementOut)
async def add_divertissement(divertissement: DivertissementCreate, current_user=Depends(get_admin_user)):
	return await create_divertissement(divertissement)


@router.get("/", response_model=List[DivertissementOut])
async def get_all_divertissement(
	skip: int = 0, 
	limit: int = 50,
	search: str = None,
	current_user=Depends(get_optional_user)
):
	divertissements = await list_divertissement(skip, limit)
	
	# Si un terme de recherche est fourni, filtrer les résultats
	if search:
		search_lower = search.lower()
		print(f"🔍 [DIVERTISSEMENTS] Recherche complète: '{search}'")
		
		# Obtenir tous les divertissements sans pagination d'abord
		all_divertissements = await list_divertissement(0, 1000)  # Grande limite pour obtenir tous
		
		# Recherche complète dans tous les champs
		filtered_divertissements = []
		for divert in all_divertissements:
			# Recherche dans tous les champs disponibles (avec vérification sécurisée)
			title_match = search_lower in divert.title.lower()
			desc_match = divert.description and search_lower in divert.description.lower()
			host_match = hasattr(divert, 'host') and divert.host and search_lower in divert.host.lower()
			category_match = hasattr(divert, 'category') and divert.category and search_lower in divert.category.lower()
			sub_category_match = hasattr(divert, 'sub_category') and divert.sub_category and search_lower in divert.sub_category.lower()
			duration_match = hasattr(divert, 'duration_minutes') and divert.duration_minutes and search_lower in str(divert.duration_minutes).lower()
			rating_match = hasattr(divert, 'rating') and divert.rating and search_lower in str(divert.rating).lower()
			tags_match = hasattr(divert, 'tags') and divert.tags and any(search_lower in tag.lower() for tag in divert.tags)
			
			if title_match or desc_match or host_match or category_match or sub_category_match or duration_match or rating_match or tags_match:
				filtered_divertissements.append(divert)
				print(f"✅ [DIVERTISSEMENTS] Match trouvé: '{divert.title}' (titre:{title_match}, desc:{desc_match}, host:{host_match}, cat:{category_match})")
		
		print(f"🎯 [DIVERTISSEMENTS] Résultats après recherche complète: {len(filtered_divertissements)}")
		
		# Pagination sur les résultats filtrés
		divertissements = filtered_divertissements[skip:skip + limit]
	
	return divertissements


@router.get("/{divertissement_id}", response_model=DivertissementOut)
async def get_one_divertissement(divertissement_id: str, current_user=Depends(get_optional_user)):
	divertissement = await get_divertissement(divertissement_id)
	if not divertissement:
		raise HTTPException(status_code=404, detail="Divertissement not found")
	return divertissement


@router.put("/{divertissement_id}", response_model=DivertissementOut)
async def update_one_divertissement(divertissement_id: str, divertissement: DivertissementUpdate, current_user=Depends(get_admin_user)):
	updated_divertissement = await update_divertissement(divertissement_id, divertissement)
	if not updated_divertissement:
		raise HTTPException(status_code=404, detail="Divertissement not found")
	return updated_divertissement


@router.delete("/{divertissement_id}")
async def delete_one_divertissement(divertissement_id: str, current_user=Depends(get_admin_user)):
	success = await delete_divertissement(divertissement_id)
	if not success:
		raise HTTPException(status_code=404, detail="Divertissement not found")
	return {"message": "Divertissement deleted successfully"}
