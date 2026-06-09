from app.models.subscription_plan import SubscriptionPlan
from app.schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanUpdate
from typing import List, Optional
from datetime import datetime


# ── Catégories avec prix mensuel de base (en XOF) ────────────────────────────
CATEGORIES = [
    {"code": "basic",    "name": "Basic",    "monthly_price": 1000},
    {"code": "standard", "name": "Standard", "monthly_price": 2000},
    {"code": "premium",  "name": "Premium",  "monthly_price": 3500},
]

# ── Durées avec réductions automatiques ──────────────────────────────────────
# discount = réduction appliquée sur le total (prix barré → prix affiché)
DURATIONS = [
    {"months": 1,  "label": "1 mois",   "discount": 0.00},   # pas de réduction
    {"months": 3,  "label": "3 mois",   "discount": 0.10},   # -10%
    {"months": 12, "label": "12 mois",  "discount": 0.25},   # -25%
]


def _compute_prices(monthly_price: int, months: int, discount: float):
    """
    Calcule price_cents (prix promo) et original_price_cents (prix barré).
    Retourne (price_cents, original_price_cents).
    - original_price_cents = monthly_price × months (sans réduction)
    - price_cents = original_price_cents × (1 - discount) arrondi à 50 XOF près
    Les deux sont en centimes (× 100).
    """
    original = monthly_price * months                          # XOF total sans réduction
    discounted = original * (1 - discount)
    # Arrondir à 50 XOF près pour des prix propres
    discounted = round(discounted / 50) * 50

    original_cents  = original   * 100
    discounted_cents = discounted * 100

    if discount == 0:
        return discounted_cents, None          # pas de promo → original_price_cents = None
    return discounted_cents, original_cents    # prix promo + prix barré


async def initialize_default_plans() -> dict:
    """Initialise les 9 plans (3 catégories × 3 durées) avec réductions automatiques.
    - Plans inexistants : créés avec les prix calculés.
    - Plans existants   : NOM et CATÉGORIE mis à jour, PRIX conservés (modifiables par l'admin).
    """
    created = []
    skipped = []

    for category in CATEGORIES:
        for dur in DURATIONS:
            months   = dur["months"]
            discount = dur["discount"]
            code     = f"{category['code']}_{months}m"
            name     = f"{category['name']} - {dur['label']}"
            price_cents, original_price_cents = _compute_prices(
                category["monthly_price"], months, discount
            )

            existing = await SubscriptionPlan.find_one({"code": code})

            if existing:
                # Mettre à jour nom/catégorie sans toucher aux prix
                changed = False
                if existing.name != name:
                    existing.name = name
                    changed = True
                if existing.category != category["code"]:
                    existing.category = category["code"]
                    changed = True
                if existing.duration_months != months:
                    existing.duration_months = months
                    changed = True
                if changed:
                    existing.updated_at = datetime.utcnow()
                    await existing.save()
                skipped.append(code)
            else:
                plan = SubscriptionPlan(
                    code=code,
                    name=name,
                    category=category["code"],
                    duration_months=months,
                    price_cents=price_cents,
                    original_price_cents=original_price_cents,
                    currency="XOF",
                    is_active=True,
                )
                await plan.insert()
                created.append(code)

    return {
        "created": created,
        "skipped": skipped,
        "total": len(created) + len(skipped),
        "message": (
            f"✅ {len(created)} plans créés avec réductions automatiques, "
            f"{len(skipped)} plans existants conservés (prix inchangés)"
        ),
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
