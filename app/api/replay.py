from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.replay import ReplayCreate, ReplayUpdate, ReplayOut
from app.services.replay_service import create_replay, get_replay, list_replays, update_replay, delete_replay

router = APIRouter()


@router.post("/", response_model=ReplayOut)
async def add_replay(replay: ReplayCreate, current_user=Depends(get_admin_user)):
	return await create_replay(replay)


@router.get("/", response_model=List[ReplayOut])
async def get_all_replays(
	skip: int = 0,
	limit: int = 50,
	current_user=Depends(get_optional_user)
):
	return await list_replays(skip, limit)


@router.get("/{replay_id}", response_model=ReplayOut)
async def get_one_replay(replay_id: str, current_user=Depends(get_optional_user)):
	replay = await get_replay(replay_id)
	if not replay:
		raise HTTPException(status_code=404, detail="Replay not found")
	return replay


@router.patch("/{replay_id}", response_model=ReplayOut)
async def update_one_replay(replay_id: str, data: ReplayUpdate, current_user=Depends(get_admin_user)):
	updated = await update_replay(replay_id, data)
	if not updated:
		raise HTTPException(status_code=404, detail="Replay not found")
	return updated


@router.delete("/{replay_id}")
async def delete_one_replay(replay_id: str, current_user=Depends(get_admin_user)):
	deleted = await delete_replay(replay_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="Replay not found")
	return {"ok": True}
