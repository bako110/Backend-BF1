"""Service pour la gestion des méthodes de paiement"""
from datetime import datetime
from typing import List, Optional
from beanie.operators import Eq
from app.models.payment_method import PaymentMethod
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodUpdate


async def create_payment_method(data: PaymentMethodCreate) -> PaymentMethod:
    """Créer une nouvelle méthode de paiement"""
    method = PaymentMethod(**data.model_dump())
    await method.insert()
    return method


async def get_payment_method(method_id: str) -> Optional[PaymentMethod]:
    """Récupérer une méthode de paiement par ID"""
    return await PaymentMethod.get(method_id)


async def get_payment_method_by_code(code: str) -> Optional[PaymentMethod]:
    """Récupérer une méthode de paiement par code"""
    return await PaymentMethod.find_one(Eq(PaymentMethod.code, code))


async def list_payment_methods(
    active_only: bool = False,
    skip: int = 0,
    limit: int = 50
) -> List[PaymentMethod]:
    """Lister les méthodes de paiement"""
    query = PaymentMethod.find()
    
    if active_only:
        query = query.find(Eq(PaymentMethod.is_active, True))
    
    return await query.sort(+PaymentMethod.order).skip(skip).limit(limit).to_list()


async def update_payment_method(
    method_id: str,
    data: PaymentMethodUpdate
) -> Optional[PaymentMethod]:
    """Mettre à jour une méthode de paiement"""
    method = await PaymentMethod.get(method_id)
    if not method:
        return None
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await method.update({"$set": update_data})
    
    return method


async def delete_payment_method(method_id: str) -> bool:
    """Supprimer une méthode de paiement"""
    method = await PaymentMethod.get(method_id)
    if not method:
        return False
    
    await method.delete()
    return True


async def toggle_payment_method(method_id: str) -> Optional[PaymentMethod]:
    """Activer/désactiver une méthode de paiement"""
    method = await PaymentMethod.get(method_id)
    if not method:
        return None
    
    method.is_active = not method.is_active
    method.updated_at = datetime.utcnow()
    await method.save()
    
    return method
