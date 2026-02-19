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
	current_user=Depends(get_optional_user)
):
	return await list_reportages(skip, limit)


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
