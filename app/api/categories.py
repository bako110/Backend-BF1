from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.models.category import Category
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    """Créer une nouvelle catégorie"""
    # Vérifier si la catégorie existe déjà
    existing = await Category.find_one(Category.name == category.name)
    if existing:
        raise HTTPException(status_code=400, detail="Une catégorie avec ce nom existe déjà")
    
    new_category = Category(**category.dict())
    await new_category.insert()
    return new_category


@router.get("/", response_model=List[CategoryResponse])
async def get_all_categories(current_user=Depends(get_optional_user)):
    """Lister toutes les catégories"""
    categories = await Category.find_all().to_list()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str, current_user=Depends(get_optional_user)):
    """Récupérer une catégorie par ID"""
    category = await Category.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str, 
    data: CategoryUpdate
):
    """Mettre à jour une catégorie"""
    category = await Category.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    
    # Vérifier si le nouveau nom existe déjà
    if data.name and data.name != category.name:
        existing = await Category.find_one(Category.name == data.name)
        if existing:
            raise HTTPException(status_code=400, detail="Une catégorie avec ce nom existe déjà")
    
    update_data = data.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await category.set(update_data)
    
    return category


@router.delete("/{category_id}")
async def delete_category(category_id: str):
    """Supprimer une catégorie"""
    category = await Category.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    
    await category.delete()
    return {"ok": True}
