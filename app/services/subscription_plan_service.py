from app.models.subscription_plan import SubscriptionPlan
from app.schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanUpdate
from typing import List, Optional
from datetime import datetime


async def list_plans(active_only: bool = True) -> List[SubscriptionPlan]:
    query = SubscriptionPlan.is_active == True if active_only else {}
    if active_only:
        return await SubscriptionPlan.find(query).sort(SubscriptionPlan.duration_months).to_list()
    return await SubscriptionPlan.find_all().sort(-SubscriptionPlan.is_active, SubscriptionPlan.duration_months).to_list()


async def get_plan(plan_id: str) -> Optional[SubscriptionPlan]:
    return await SubscriptionPlan.get(plan_id)


async def create_plan(data: SubscriptionPlanCreate) -> SubscriptionPlan:
    plan = SubscriptionPlan(**data.dict())
    await plan.insert()
    return plan


async def update_plan(plan_id: str, data: SubscriptionPlanUpdate) -> Optional[SubscriptionPlan]:
    plan = await SubscriptionPlan.get(plan_id)
    if not plan:
        return None

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
    plan.updated_at = datetime.utcnow()

    await plan.save()
    return plan


async def delete_plan(plan_id: str) -> bool:
    plan = await SubscriptionPlan.get(plan_id)
    if not plan:
        return False
    await plan.delete()
    return True
