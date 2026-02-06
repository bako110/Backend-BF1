from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.popularPrograms import PopularProgramsCreate, PopularProgramsUpdate, PopularProgramsOut
from app.services.popularPrograms import (
	create_program, get_program, list_programs, update_program, delete_program
)

router = APIRouter()


@router.post("/", response_model=PopularProgramsOut)
async def add_program(program: PopularProgramsCreate, current_user=Depends(get_admin_user)):
	return await create_program(program)


@router.get("/", response_model=List[PopularProgramsOut])
async def get_all_programs(
	skip: int = 0,
	limit: int = 50,
	current_user=Depends(get_optional_user)
):
	return await list_programs(skip, limit)


@router.get("/{program_id}", response_model=PopularProgramsOut)
async def get_one_program(program_id: str, current_user=Depends(get_optional_user)):
	program = await get_program(program_id)
	if not program:
		raise HTTPException(status_code=404, detail="Program not found")
	return program


@router.patch("/{program_id}", response_model=PopularProgramsOut)
async def update_one_program(program_id: str, data: PopularProgramsUpdate, current_user=Depends(get_admin_user)):
	updated = await update_program(program_id, data)
	if not updated:
		raise HTTPException(status_code=404, detail="Program not found")
	return updated


@router.delete("/{program_id}")
async def delete_one_program(program_id: str, current_user=Depends(get_admin_user)):
	deleted = await delete_program(program_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="Program not found")
	return {"ok": True}
