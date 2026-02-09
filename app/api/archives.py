from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from app.models.archive import Archive
from app.models.user import User
from app.schemas.archive import ArchiveCreate, ArchiveUpdate, ArchiveOut
from app.utils.auth import get_current_user, get_admin_user

router = APIRouter()


@router.get("/", response_model=List[ArchiveOut])
async def get_archives(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    is_active: bool = True
):
    """Récupérer toutes les archives (accessibles selon l'abonnement)"""
    query = {"is_active": is_active}
    
    if category:
        query["category"] = category
    
    archives = await Archive.find(query).skip(skip).limit(limit).to_list()
    return archives


@router.get("/{archive_id}", response_model=ArchiveOut)
async def get_archive(
    archive_id: str,
    current_user: User = Depends(get_current_user)
):
    """Récupérer une archive spécifique (nécessite authentification)"""
    archive = await Archive.get(archive_id)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive non trouvée")
    
    # Vérifier si l'utilisateur a accès (premium ou achat individuel)
    if archive.is_premium and not current_user.is_premium:
        # TODO: Vérifier si l'utilisateur a acheté cette archive individuellement
        raise HTTPException(
            status_code=403, 
            detail="Abonnement premium requis pour accéder à cette archive"
        )
    
    # Incrémenter les vues
    archive.views += 1
    await archive.save()
    
    return archive


@router.post("/", response_model=ArchiveOut)
async def create_archive(
    archive: ArchiveCreate,
    current_user: User = Depends(get_admin_user)
):
    """Créer une nouvelle archive (admin uniquement)"""
    new_archive = Archive(**archive.model_dump())
    await new_archive.insert()
    return new_archive


@router.patch("/{archive_id}", response_model=ArchiveOut)
async def update_archive(
    archive_id: str,
    archive_update: ArchiveUpdate,
    current_user: User = Depends(get_admin_user)
):
    """Mettre à jour une archive (admin uniquement)"""
    archive = await Archive.get(archive_id)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive non trouvée")
    
    update_data = archive_update.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        for key, value in update_data.items():
            setattr(archive, key, value)
        await archive.save()
    
    return archive


@router.delete("/{archive_id}")
async def delete_archive(
    archive_id: str,
    current_user: User = Depends(get_admin_user)
):
    """Supprimer une archive (admin uniquement)"""
    archive = await Archive.get(archive_id)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive non trouvée")
    
    await archive.delete()
    return {"message": "Archive supprimée avec succès"}


@router.get("/categories/list", response_model=List[str])
async def get_archive_categories():
    """Récupérer toutes les catégories d'archives disponibles"""
    archives = await Archive.find({"is_active": True}).to_list()
    categories = list(set(archive.category for archive in archives if archive.category))
    return sorted(categories)


@router.get("/{archive_id}/check-access")
async def check_archive_access(
    archive_id: str,
    current_user: User = Depends(get_current_user)
):
    """Vérifier si l'utilisateur a accès à une archive"""
    archive = await Archive.get(archive_id)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive non trouvée")
    
    has_access = not archive.is_premium or current_user.is_premium
    
    return {
        "has_access": has_access,
        "is_premium": archive.is_premium,
        "user_is_premium": current_user.is_premium,
        "price": archive.price if archive.is_premium else 0
    }


@router.post("/{archive_id}/rate")
async def rate_archive(
    archive_id: str,
    rating: float = Query(..., ge=0, le=5),
    current_user: User = Depends(get_current_user)
):
    """Noter une archive (utilisateur connecté)"""
    archive = await Archive.get(archive_id)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive non trouvée")
    
    # Calculer la nouvelle moyenne (simplifiée)
    # TODO: Implémenter un système de notation plus sophistiqué avec stockage des votes
    total_ratings = archive.views if archive.views > 0 else 1
    archive.rating = ((archive.rating * total_ratings) + rating) / (total_ratings + 1)
    await archive.save()
    
    return {"message": "Note enregistrée", "new_rating": archive.rating}
