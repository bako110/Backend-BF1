"""
Routes API pour la gestion des sports
Définit tous les endpoints pour les opérations sur les sports
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.services.sport_service import SportService
from app.schemas.sport import (
    SportCreate,
    SportUpdate,
    SportResponse,
    SportList,
    SportStats,
    CategoryList,
    SearchRequest,
    LikeRequest,
    ViewIncrementRequest
)
from app.utils.auth import get_admin_user, get_optional_user

router = APIRouter()


def get_sport_service() -> SportService:
    """Dependency injection pour le service des sports"""
    return SportService()


@router.get("", response_model=SportList, summary="Lister tous les sports")
async def get_all_sports(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    featured: Optional[bool] = Query(None, description="Filtrer les sports en vedette"),
    is_new: Optional[bool] = Query(None, description="Filtrer les nouveaux sports"),
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(20, ge=1, le=100, description="Éléments par page"),
    search: Optional[str] = Query(None, description="Rechercher dans tous les champs"),
    service: SportService = Depends(get_sport_service)
):
    """
    Récupère la liste de tous les sports avec pagination, filtres et recherche complète.
    """
    if search:
        search_lower = search.lower()
        all_sports = await service.get_all_sports_raw()

        filtered_sports = []
        for sport in all_sports:
            title_match = search_lower in sport.title.lower()
            desc_match = sport.description and search_lower in sport.description.lower()
            host_match = hasattr(sport, 'host') and sport.host and search_lower in sport.host.lower()
            category_match = hasattr(sport, 'category') and sport.category and search_lower in sport.category.lower()
            sub_category_match = hasattr(sport, 'sub_category') and sport.sub_category and search_lower in sport.sub_category.lower()
            tags_match = hasattr(sport, 'tags') and sport.tags and any(search_lower in tag.lower() for tag in sport.tags)

            if title_match or desc_match or host_match or category_match or sub_category_match or tags_match:
                filtered_sports.append(sport)

        if category:
            filtered_sports = [e for e in filtered_sports if e.category == category]
        if featured is not None:
            filtered_sports = [e for e in filtered_sports if getattr(e, 'featured', False) == featured]
        if is_new is not None:
            filtered_sports = [e for e in filtered_sports if getattr(e, 'is_new', False) == is_new]

        total_filtered = len(filtered_sports)
        paginated_sports = filtered_sports[skip:skip + limit]

        return {
            "items": [SportResponse.from_orm(sport) for sport in paginated_sports],
            "total": total_filtered,
            "skip": skip,
            "limit": limit,
        }

    result = await service.get_all_sports(
        category=category,
        featured=featured,
        is_new=is_new,
        skip=skip,
        limit=limit
    )

    return result


@router.get("/featured", response_model=List[SportResponse], summary="Sports en vedette")
async def get_featured_sports(
    limit: int = Query(10, ge=1, le=50, description="Nombre maximum de résultats"),
    service: SportService = Depends(get_sport_service)
):
    """
    Récupère les sports en vedette.
    
    - **limit**: Nombre maximum de résultats (max 50)
    """
    return await service.get_featured_sports(limit=limit)


@router.get("/new", response_model=List[SportResponse], summary="Nouveaux sports")
async def get_new_sports(
    limit: int = Query(10, ge=1, le=50, description="Nombre maximum de résultats"),
    service: SportService = Depends(get_sport_service)
):
    """
    Récupère les nouveaux sports.
    
    - **limit**: Nombre maximum de résultats (max 50)
    """
    return await service.get_new_sports(limit=limit)


@router.get("/categories", response_model=CategoryList, summary="Liste des catégories")
async def get_categories(service: SportService = Depends(get_sport_service)):
    """
    Récupère la liste des catégories avec le nombre de sports par catégorie.
    """
    categories = await service.get_categories()
    return {
        "categories": categories,
        "total_categories": len(categories)
    }


@router.get("/search", response_model=List[SportResponse], summary="Rechercher des sports")
async def search_sports(
    query: str = Query(..., min_length=1, max_length=100, description="Terme de recherche"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    limit: int = Query(20, ge=1, le=100, description="Limite de résultats"),
    offset: int = Query(0, ge=0, description="Offset pour pagination"),
    service: SportService = Depends(get_sport_service)
):
    """
    Recherche des sports par terme de recherche.
    
    - **query**: Terme de recherche (recherche dans titre, description, présentateur)
    - **category**: Filtre par catégorie optionnel
    - **limit**: Nombre maximum de résultats (max 100)
    - **offset**: Offset pour la pagination
    """
    search_request = SearchRequest(
        query=query,
        category=category,
        limit=limit,
        offset=offset
    )
    return await service.search_sports(search_request)


@router.get("/{sport_id}", response_model=SportResponse, summary="Détails d'un sport")
async def get_sport_by_id(
    sport_id: str,
    service: SportService = Depends(get_sport_service)
):
    """
    Récupère les détails d'un sport spécifique.
    
    - **sport_id**: ID unique du sport
    """
    return await service.get_sport_by_id(sport_id)


@router.get("/{sport_id}/stats", response_model=SportStats, summary="Statistiques d'un sport")
async def get_sport_stats(
    sport_id: str,
    service: SportService = Depends(get_sport_service)
):
    """
    Récupère les statistiques d'un sport (vues, likes, etc.).
    
    - **sport_id**: ID unique du sport
    """
    return await service.get_sport_stats(sport_id)


@router.post("/{sport_id}/views", summary="Incrémenter les vues")
async def increment_views(
    sport_id: str,
    request: Optional[ViewIncrementRequest] = None,
    service: SportService = Depends(get_sport_service)
):
    """
    Incrémente le nombre de vues d'un sport.
    
    - **sport_id**: ID unique du sport
    - **request**: Données optionnelles (user_id, session_id)
    """
    success = await service.increment_views(sport_id, request)
    return {"success": success, "message": "Vues incrémentées avec succès"}


@router.post("/{sport_id}/likes", summary="Gérer les likes")
async def toggle_like(
    sport_id: str,
    request: LikeRequest,
    service: SportService = Depends(get_sport_service)
):
    """
    Ajoute ou retire un like d'un sport.
    
    - **sport_id**: ID unique du sport
    - **request**: Action (add/remove) et user_id optionnel
    """
    result = await service.toggle_like(sport_id, request)
    return result


# Routes administratives (protégées par authentification)

@router.post("", response_model=SportResponse, summary="Créer un sport")
async def create_sport(
    sport_data: SportCreate,
    service: SportService = Depends(get_sport_service),
    current_user = Depends(get_admin_user)
):
    """
    Crée une nouvelle émission.
    
    *Nécessite des droits d'administration*
    """
    return await service.create_sport(sport_data)


@router.put("/{sport_id}", response_model=SportResponse, summary="Mettre à jour un sport")
async def update_sport(
    sport_id: str,
    sport_data: SportUpdate,
    service: SportService = Depends(get_sport_service),
    current_user = Depends(get_admin_user)
):
    """
    Met à jour un sport existant.
    
    *Nécessite des droits d'administration*
    """
    return await service.update_sport(sport_id, sport_data)


@router.delete("/{sport_id}", summary="Supprimer un sport")
async def delete_sport(
    sport_id: str,
    service: SportService = Depends(get_sport_service),
    current_user = Depends(get_admin_user)
):
    """
    Supprime (désactive) un sport.
    
    *Nécessite des droits d'administration*
    """
    success = await service.delete_sport(sport_id)
    return {"success": success, "message": "Sport supprimé avec succès"}