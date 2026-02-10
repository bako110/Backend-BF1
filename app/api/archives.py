from fastapi import APIRouter, HTTPException, Depends, Query, Request, status
from typing import List, Optional
from datetime import datetime

from app.models.archive import Archive
from app.models.archive_purchase import ArchivePurchase
from typing import Optional
from app.models.user import User
from app.schemas.archive import ArchiveCreate, ArchiveUpdate, ArchiveOut
from app.schemas.archive_purchase import ArchivePurchaseCreate, ArchivePurchaseOut
from app.utils.auth import get_current_user, get_admin_user, get_optional_user

router = APIRouter()


@router.get("/")
async def get_archives(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    is_active: bool = True,
    sort_by: str = Query("created_at", description="Trier par: created_at, popularity, rating, views, price"),
    order: str = Query("desc", description="Ordre: asc ou desc")
):
    """Récupérer toutes les archives avec filtres et tri avancés"""
    query = {"is_active": is_active}
    
    if category:
        query["category"] = category
    
    # Déterminer le tri
    sort_field = sort_by
    sort_direction = -1 if order == "desc" else 1
    
    archives = await Archive.find(query).sort(
        [(sort_field, sort_direction)]
    ).skip(skip).limit(limit).to_list()
    
    # Convertir les ObjectId en string manuellement
    return [
        {
            "id": str(archive.id),
            "title": archive.title,
            "description": archive.description,
            "category": archive.category,
            "thumbnail": archive.thumbnail,
            "video_url": archive.video_url,
            "duration_minutes": archive.duration_minutes,
            "price": archive.price,
            "guest_name": archive.guest_name,
            "guest_role": archive.guest_role,
            "archived_date": archive.archived_date,
            "is_premium": archive.is_premium,
            "is_active": archive.is_active,
            "views": archive.views,
            "rating": archive.rating,
            "rating_count": archive.rating_count,
            "purchases_count": archive.purchases_count,
            "popularity_score": archive.popularity_score,
            "created_at": archive.created_at,
            "updated_at": archive.updated_at
        }
        for archive in archives
    ]


@router.get("/{archive_id}", response_model=ArchiveOut)
async def get_archive(
    archive_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Récupérer une archive spécifique (accessible sans authentification pour le contenu gratuit)"""
    archive = await Archive.get(archive_id)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive non trouvée")
    
    # Vérifier si l'utilisateur a accès (premium ou achat individuel)
    if archive.is_premium:
        if not current_user:
            raise HTTPException(
                status_code=401, 
                detail="Authentification requise pour accéder au contenu premium"
            )
        
        if not current_user.is_premium:
            # Vérifier si l'utilisateur a acheté cette archive individuellement
            purchase = await ArchivePurchase.find_one({
                "user_id": str(current_user.id),
                "archive_id": archive_id,
                "status": "completed"
            })
            
            if not purchase:
                raise HTTPException(
                    status_code=403, 
                    detail="Abonnement premium ou achat individuel requis pour accéder à cette archive"
                )
    
    # Incrémenter les vues
    archive.views += 1
    await archive.save()
    
    return archive


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_archive(
    archive: ArchiveCreate,
    current_user: User = Depends(get_admin_user)
):
    """Créer une nouvelle archive (admin uniquement)"""
    new_archive = Archive(**archive.model_dump())
    await new_archive.insert()
    
    # Convertir l'ObjectId en string manuellement
    return {
        "id": str(new_archive.id),
        "title": new_archive.title,
        "description": new_archive.description,
        "category": new_archive.category,
        "thumbnail": new_archive.thumbnail,
        "video_url": new_archive.video_url,
        "duration_minutes": new_archive.duration_minutes,
        "price": new_archive.price,
        "guest_name": new_archive.guest_name,
        "guest_role": new_archive.guest_role,
        "archived_date": new_archive.archived_date,
        "is_premium": new_archive.is_premium,
        "is_active": new_archive.is_active,
        "views": new_archive.views,
        "rating": new_archive.rating,
        "rating_count": new_archive.rating_count,
        "purchases_count": new_archive.purchases_count,
        "popularity_score": new_archive.popularity_score,
        "created_at": new_archive.created_at,
        "updated_at": new_archive.updated_at
    }


@router.patch("/{archive_id}")
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
    
    # Convertir l'ObjectId en string manuellement
    return {
        "id": str(archive.id),
        "title": archive.title,
        "description": archive.description,
        "category": archive.category,
        "thumbnail": archive.thumbnail,
        "video_url": archive.video_url,
        "duration_minutes": archive.duration_minutes,
        "price": archive.price,
        "guest_name": archive.guest_name,
        "guest_role": archive.guest_role,
        "archived_date": archive.archived_date,
        "is_premium": archive.is_premium,
        "is_active": archive.is_active,
        "views": archive.views,
        "rating": archive.rating,
        "rating_count": archive.rating_count,
        "purchases_count": archive.purchases_count,
        "popularity_score": archive.popularity_score,
        "created_at": archive.created_at,
        "updated_at": archive.updated_at
    }


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
    
    # Vérifier l'accès premium ou achat individuel
    has_premium_access = current_user.is_premium
    has_purchased = False
    
    if archive.is_premium and not has_premium_access:
        purchase = await ArchivePurchase.find_one({
            "user_id": str(current_user.id),
            "archive_id": archive_id,
            "status": "completed"
        })
        has_purchased = purchase is not None
    
    has_access = not archive.is_premium or has_premium_access or has_purchased
    
    return {
        "has_access": has_access,
        "is_premium": archive.is_premium,
        "user_is_premium": has_premium_access,
        "has_purchased": has_purchased,
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
    
    # Calculer la nouvelle moyenne avec le nombre de ratings
    old_total = archive.rating * archive.rating_count
    archive.rating_count += 1
    archive.rating = (old_total + rating) / archive.rating_count
    
    # Mettre à jour le score de popularité
    archive.popularity_score = (
        archive.views * 0.3 + 
        archive.rating * archive.rating_count * 0.5 + 
        archive.purchases_count * 0.2
    )
    
    await archive.save()
    
    return {
        "message": "Note enregistrée",
        "new_rating": archive.rating,
        "rating_count": archive.rating_count
    }


@router.post("/{archive_id}/purchase", response_model=ArchivePurchaseOut)
async def purchase_archive(
    archive_id: str,
    purchase_data: ArchivePurchaseCreate,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Acheter une archive individuellement"""
    archive = await Archive.get(archive_id)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive non trouvée")
    
    # Vérifier si l'utilisateur a déjà acheté cette archive
    existing_purchase = await ArchivePurchase.find_one({
        "user_id": str(current_user.id),
        "archive_id": archive_id,
        "status": "completed"
    })
    
    if existing_purchase:
        raise HTTPException(status_code=400, detail="Vous avez déjà acheté cette archive")
    
    # Vérifier si l'utilisateur est déjà premium
    if current_user.is_premium:
        raise HTTPException(status_code=400, detail="Vous avez déjà accès à cette archive via votre abonnement premium")
    
    # Créer l'achat
    new_purchase = ArchivePurchase(
        user_id=str(current_user.id),
        archive_id=archive_id,
        amount_paid=archive.price,
        payment_method=purchase_data.payment_method,
        transaction_id=purchase_data.transaction_id,
        ip_address=request.client.host if request.client else None
    )
    
    await new_purchase.insert()
    
    # Incrémenter le compteur d'achats de l'archive
    archive.purchases_count += 1
    archive.popularity_score = (
        archive.views * 0.3 + 
        archive.rating * archive.rating_count * 0.5 + 
        archive.purchases_count * 0.2
    )
    await archive.save()
    
    return new_purchase


@router.get("/user/purchases", response_model=List[ArchivePurchaseOut])
async def get_user_purchases(
    current_user: User = Depends(get_current_user)
):
    """Récupérer tous les achats d'archives de l'utilisateur"""
    purchases = await ArchivePurchase.find({
        "user_id": str(current_user.id),
        "status": "completed"
    }).to_list()
    
    return purchases


@router.get("/stats/popular", response_model=List[ArchiveOut])
async def get_popular_archives(
    limit: int = Query(10, ge=1, le=50)
):
    """Récupérer les archives les plus populaires"""
    archives = await Archive.find({
        "is_active": True
    }).sort([("popularity_score", -1)]).limit(limit).to_list()
    
    return archives


@router.get("/stats/trending", response_model=List[ArchiveOut])
async def get_trending_archives(
    limit: int = Query(10, ge=1, le=50)
):
    """Récupérer les archives tendances (basé sur les vues récentes)"""
    # Archives créées dans les 30 derniers jours, triées par vues
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    archives = await Archive.find({
        "is_active": True,
        "created_at": {"$gte": thirty_days_ago}
    }).sort([("views", -1)]).limit(limit).to_list()
    
    return archives


@router.get("/stats/overview")
async def get_archives_stats(
    current_user: User = Depends(get_admin_user)
):
    """Obtenir les statistiques globales des archives (admin uniquement)"""
    total_archives = await Archive.find({"is_active": True}).count()
    total_premium = await Archive.find({"is_active": True, "is_premium": True}).count()
    total_purchases = await ArchivePurchase.find({"status": "completed"}).count()
    
    # Statistiques de vues et ratings
    all_archives = await Archive.find({"is_active": True}).to_list()
    total_views = sum(a.views for a in all_archives)
    avg_rating = sum(a.rating for a in all_archives) / len(all_archives) if all_archives else 0
    
    # Revenus totaux (estimé)
    all_purchases = await ArchivePurchase.find({"status": "completed"}).to_list()
    total_revenue = sum(p.amount_paid for p in all_purchases)
    
    return {
        "total_archives": total_archives,
        "total_premium_archives": total_premium,
        "total_purchases": total_purchases,
        "total_views": total_views,
        "average_rating": round(avg_rating, 2),
        "total_revenue": round(total_revenue, 2),
        "currency": "EUR"
    }
