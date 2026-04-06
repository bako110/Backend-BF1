from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.reportage import ReportageCreate, ReportageUpdate, ReportageOut
from app.services.reportage_service import create_reportage, get_reportage, list_reportages, update_reportage, delete_reportage
from app.models.reportage import Reportage

router = APIRouter()


@router.post("", response_model=ReportageOut)
async def add_reportage(reportage: ReportageCreate, current_user=Depends(get_admin_user)):
	return await create_reportage(reportage)


@router.get("")
async def get_all_reportages(
	skip: int = Query(0, ge=0),
	limit: int = Query(20, ge=1, le=500),
	search: Optional[str] = None,
	current_user=Depends(get_optional_user)
):
	query = {}
	if search:
		search_lower = search.strip()
		query["$or"] = [
			{"title": {"$regex": search_lower, "$options": "i"}},
			{"description": {"$regex": search_lower, "$options": "i"}},
			{"category": {"$regex": search_lower, "$options": "i"}},
			{"tags": {"$in": [search_lower]}},
		]

	total = await Reportage.find(query).count()
	items = await Reportage.find(query).skip(skip).limit(limit).to_list()

	return {"items": items, "total": total, "skip": skip, "limit": limit}


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
