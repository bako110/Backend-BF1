from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.emission_category import EmissionCategoryCreate, EmissionCategoryResponse, EmissionCategoryUpdate
from app.models.emission_category import EmissionCategory
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("", response_model=EmissionCategoryResponse)
async def create_emission_category(category: EmissionCategoryCreate, current_user=Depends(get_admin_user)):
    """Créer une nouvelle catégorie d'émission (Admin uniquement)"""
    # Vérifier si la catégorie existe déjà
    existing = await EmissionCategory.find_one(EmissionCategory.name == category.name)
    if existing:
        raise HTTPException(status_code=400, detail="Une catégorie avec ce nom existe déjà")
    
    new_category = EmissionCategory(**category.dict())
    await new_category.insert()
    return new_category


@router.get("", response_model=List[EmissionCategoryResponse])
async def get_all_emission_categories(current_user=Depends(get_optional_user)):
    """Lister toutes les catégories d'émissions (triées par ordre)"""
    categories = await EmissionCategory.find_all().sort("+order").to_list()
    return categories


@router.get("/{category_id}", response_model=EmissionCategoryResponse)
async def get_emission_category(category_id: str, current_user=Depends(get_optional_user)):
    """Récupérer une catégorie d'émission par ID"""
    category = await EmissionCategory.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return category


@router.put("/{category_id}", response_model=EmissionCategoryResponse)
async def update_emission_category(
    category_id: str, 
    data: EmissionCategoryUpdate,
    current_user=Depends(get_admin_user)
):
    """Mettre à jour une catégorie d'émission (Admin uniquement)"""
    category = await EmissionCategory.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    
    # Vérifier si le nouveau nom existe déjà
    if data.name and data.name != category.name:
        existing = await EmissionCategory.find_one(EmissionCategory.name == data.name)
        if existing:
            raise HTTPException(status_code=400, detail="Une catégorie avec ce nom existe déjà")
    
    # Mettre à jour les champs
    update_data = data.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        for field, value in update_data.items():
            setattr(category, field, value)
        await category.save()
    
    return category


@router.delete("/{category_id}")
async def delete_emission_category(category_id: str, current_user=Depends(get_admin_user)):
    """Supprimer une catégorie d'émission (Admin uniquement)"""
    category = await EmissionCategory.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    
    await category.delete()
    return {"message": "Catégorie supprimée avec succès"}
