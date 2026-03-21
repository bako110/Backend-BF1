from app.models.subscription_plan import SubscriptionPlan
from app.schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanUpdate
from typing import List, Optional
from datetime import datetime


CATEGORIES = [
    {"code": "basic", "name": "Basic", "monthly_price": 2500},
    {"code": "standard", "name": "Standard", "monthly_price": 5000},
    {"code": "premium", "name": "Premium", "monthly_price": 15000}
]

DURATIONS = [1, 3, 12]  # en mois


async def initialize_default_plans() -> dict:
    """Initialise les 9 plans d'abonnement par défaut (3 catégories × 3 durées)"""
    created = []
    updated = []
    
    for category in CATEGORIES:
        for duration in DURATIONS:
            code = f"{category['code']}_{duration}m"
            name = f"{category['name']} - {duration} mois"
            total_price = category['monthly_price'] * duration
            price_cents = total_price * 100  # Convertir en centimes
            
            # Vérifier si le plan existe déjà
            existing = await SubscriptionPlan.find_one({"code": code})
            
            if existing:
                # Mettre à jour le plan existant (sauf le prix, gardé par l'admin)
                existing.name = name
                existing.category = category['code']
                existing.duration_months = duration
                existing.updated_at = datetime.utcnow()
                await existing.save()
                updated.append(code)
            else:
                # Créer un nouveau plan
                plan = SubscriptionPlan(
                    code=code,
                    name=name,
                    category=category['code'],
                    duration_months=duration,
                    price_cents=price_cents,
                    currency="XOF",
                    is_active=True
                )
                await plan.insert()
                created.append(code)
    
    return {
        "created": created,
        "updated": updated,
        "total": len(created) + len(updated),
        "message": f"✅ {len(created)} plans créés, {len(updated)} mis à jour"
    }


async def list_plans(active_only: bool = True) -> List[SubscriptionPlan]:
    query = SubscriptionPlan.is_active == True if active_only else {}
    if active_only:
        return await SubscriptionPlan.find(query).sort([("category", 1), ("duration_months", 1)]).to_list()
    return await SubscriptionPlan.find_all().sort([("-is_active", -1), ("category", 1), ("duration_months", 1)]).to_list()


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
