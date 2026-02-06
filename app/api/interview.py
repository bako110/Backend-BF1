from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewOut
from app.services.interview_service import (
	create_interview, get_interview, list_interviews, update_interview, delete_interview
)

router = APIRouter()


@router.post("/", response_model=InterviewOut)
async def add_interview(interview: InterviewCreate, current_user=Depends(get_admin_user)):
	return await create_interview(interview)


@router.get("/", response_model=List[InterviewOut])
async def get_all_interviews(
	skip: int = 0,
	limit: int = 50,
	current_user=Depends(get_optional_user)
):
	return await list_interviews(skip, limit)


@router.get("/{interview_id}", response_model=InterviewOut)
async def get_one_interview(interview_id: str, current_user=Depends(get_optional_user)):
	interview = await get_interview(interview_id)
	if not interview:
		raise HTTPException(status_code=404, detail="Interview not found")
	return interview


@router.patch("/{interview_id}", response_model=InterviewOut)
async def update_one_interview(interview_id: str, data: InterviewUpdate, current_user=Depends(get_admin_user)):
	updated = await update_interview(interview_id, data)
	if not updated:
		raise HTTPException(status_code=404, detail="Interview not found")
	return updated


@router.delete("/{interview_id}")
async def delete_one_interview(interview_id: str, current_user=Depends(get_admin_user)):
	deleted = await delete_interview(interview_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="Interview not found")
	return {"ok": True}
