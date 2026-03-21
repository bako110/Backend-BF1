from app.models.popularPrograms import PopularPrograms
from app.schemas.popularPrograms import PopularProgramsCreate, PopularProgramsUpdate
from typing import List, Optional
from datetime import datetime


async def create_program(data: PopularProgramsCreate) -> PopularPrograms:
	program = PopularPrograms(**data.dict())
	await program.insert()
	return program


async def get_program(program_id: str) -> Optional[PopularPrograms]:
	return await PopularPrograms.get(program_id)


async def list_programs(skip: int = 0, limit: int = 50) -> List[PopularPrograms]:
	return await PopularPrograms.find_all().sort(-PopularPrograms.created_at).skip(skip).limit(limit).to_list()


async def update_program(program_id: str, data: PopularProgramsUpdate) -> Optional[PopularPrograms]:
	program = await PopularPrograms.get(program_id)
	if not program:
		return None

	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(program, field, value)

	program.updated_at = datetime.utcnow()
	await program.save()
	return program


async def delete_program(program_id: str) -> bool:
	program = await PopularPrograms.get(program_id)
	if not program:
		return False
	await program.delete()
	return True
