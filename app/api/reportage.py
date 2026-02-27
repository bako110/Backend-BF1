from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.reportage import ReportageCreate, ReportageUpdate, ReportageOut
from app.services.reportage_service import create_reportage, get_reportage, list_reportages, update_reportage, delete_reportage

router = APIRouter()


@router.post("/", response_model=ReportageOut)
async def add_reportage(reportage: ReportageCreate, current_user=Depends(get_admin_user)):
	return await create_reportage(reportage)


@router.get("/", response_model=List[ReportageOut])
async def get_all_reportages(
	skip: int = 0, 
	limit: int = 50,
	search: str = None,
	current_user=Depends(get_optional_user)
):
	reportages = await list_reportages(skip, limit)
	
	# Si un terme de recherche est fourni, filtrer les résultats
	if search:
		search_lower = search.lower()
		print(f" [REPORTAGES] Recherche complète: '{search}'")
		
		# Obtenir tous les reportages sans pagination d'abord
		all_reportages = await list_reportages(0, 1000)  # Grande limite pour obtenir tous
		
		# Recherche complète dans tous les champs
		filtered_reportages = []
		for reportage in all_reportages:
			# Recherche dans tous les champs disponibles
			title_match = search_lower in reportage.title.lower()
			desc_match = reportage.description and search_lower in reportage.description.lower()
			host_match = hasattr(reportage, 'host') and reportage.host and search_lower in reportage.host.lower()
			category_match = hasattr(reportage, 'category') and reportage.category and search_lower in reportage.category.lower()
			sub_category_match = hasattr(reportage, 'sub_category') and reportage.sub_category and search_lower in reportage.sub_category.lower()
			theme_match = hasattr(reportage, 'theme') and reportage.theme and search_lower in reportage.theme.lower()
			location_match = hasattr(reportage, 'location') and reportage.location and search_lower in reportage.location.lower()
			journalist_match = hasattr(reportage, 'journalist') and reportage.journalist and search_lower in reportage.journalist.lower()
			tags_match = hasattr(reportage, 'tags') and reportage.tags and any(search_lower in tag.lower() for tag in reportage.tags)
			
			if title_match or desc_match or host_match or category_match or sub_category_match or theme_match or location_match or journalist_match or tags_match:
				filtered_reportages.append(reportage)
				print(f" [REPORTAGES] Match trouvé: '{reportage.title}' (titre:{title_match}, desc:{desc_match}, host:{host_match}, cat:{category_match})")
		
		print(f" [REPORTAGES] Résultats après recherche complète: {len(filtered_reportages)}")
		
		# Pagination sur les résultats filtrés
		reportages = filtered_reportages[skip:skip + limit]
	
	return reportages


@router.get("/{reportage_id}", response_model=ReportageOut)
async def get_one_reportage(reportage_id: str, current_user=Depends(get_optional_user)):
	reportage = await get_reportage(reportage_id)
	if not reportage:
		raise HTTPException(status_code=404, detail="Reportage not found")
	return reportage


@router.put("/{reportage_id}", response_model=ReportageOut)
async def update_one_reportage(reportage_id: str, reportage: ReportageUpdate, current_user=Depends(get_admin_user)):
	updated_reportage = await update_reportage(reportage_id, reportage)
	if not updated_reportage:
		raise HTTPException(status_code=404, detail="Reportage not found")
	return updated_reportage


@router.delete("/{reportage_id}")
async def delete_one_reportage(reportage_id: str, current_user=Depends(get_admin_user)):
	success = await delete_reportage(reportage_id)
	if not success:
		raise HTTPException(status_code=404, detail="Reportage not found")
	return {"message": "Reportage deleted successfully"}
