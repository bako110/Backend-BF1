from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanOut, SubscriptionPlanUpdate
from app.services.subscription_plan_service import create_plan, delete_plan, get_plan, list_plans, update_plan

router = APIRouter()


@router.get("/", response_model=List[SubscriptionPlanOut])
async def get_plans(active_only: bool = True, current_user=Depends(get_optional_user)):
    """Lister les tarifs/plans. Public par défaut (active_only=True)."""
    plans = await list_plans(active_only=active_only)
    return plans


@router.post("/", response_model=SubscriptionPlanOut)
async def add_plan(data: SubscriptionPlanCreate, current_user=Depends(get_admin_user)):
    return await create_plan(data)


@router.get("/{plan_id}", response_model=SubscriptionPlanOut)
async def get_one_plan(plan_id: str, current_user=Depends(get_admin_user)):
    plan = await get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.patch("/{plan_id}", response_model=SubscriptionPlanOut)
async def update_one_plan(plan_id: str, data: SubscriptionPlanUpdate, current_user=Depends(get_admin_user)):
    plan = await update_plan(plan_id, data)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.delete("/{plan_id}")
async def delete_one_plan(plan_id: str, current_user=Depends(get_admin_user)):
    ok = await delete_plan(plan_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"ok": True}
