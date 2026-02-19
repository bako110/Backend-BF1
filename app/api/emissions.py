"""
Routes API pour la gestion des émissions
Définit tous les endpoints pour les opérations sur les émissions
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.services.emission_service import EmissionService
from app.schemas.emission import (
    EmissionCreate,
    EmissionUpdate,
    EmissionResponse,
    EmissionList,
    EmissionStats,
    CategoryList,
    SearchRequest,
    LikeRequest,
    ViewIncrementRequest
)
from app.utils.auth import get_admin_user, get_optional_user

router = APIRouter()


def get_emission_service() -> EmissionService:
    """Dependency injection pour le service des émissions"""
    return EmissionService()


@router.get("/", response_model=EmissionList, summary="Lister toutes les émissions")
async def get_all_emissions(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    featured: Optional[bool] = Query(None, description="Filtrer les émissions en vedette"),
    is_new: Optional[bool] = Query(None, description="Filtrer les nouvelles émissions"),
    page: int = Query(1, ge=1, description="Page actuelle"),
    per_page: int = Query(20, ge=1, le=100, description="Éléments par page"),
    service: EmissionService = Depends(get_emission_service)
):
    """
    Récupère la liste de toutes les émissions avec pagination et filtres.
    
    - **category**: Filtre par catégorie (jt, magazines, documentaires, divertissement, sport, emission)
    - **featured**: Filtre les émissions en vedette
    - **is_new**: Filtre les nouvelles émissions
    - **page**: Numéro de page pour la pagination
    - **per_page**: Nombre d'éléments par page (max 100)
    """
    result = await service.get_all_emissions(
        category=category,
        featured=featured,
        is_new=is_new,
        page=page,
        per_page=per_page
    )
    return result


@router.get("/featured", response_model=List[EmissionResponse], summary="Émissions en vedette")
async def get_featured_emissions(
    limit: int = Query(10, ge=1, le=50, description="Nombre maximum de résultats"),
    service: EmissionService = Depends(get_emission_service)
):
    """
    Récupère les émissions en vedette.
    
    - **limit**: Nombre maximum de résultats (max 50)
    """
    return await service.get_featured_emissions(limit=limit)


@router.get("/new", response_model=List[EmissionResponse], summary="Nouvelles émissions")
async def get_new_emissions(
    limit: int = Query(10, ge=1, le=50, description="Nombre maximum de résultats"),
    service: EmissionService = Depends(get_emission_service)
):
    """
    Récupère les nouvelles émissions.
    
    - **limit**: Nombre maximum de résultats (max 50)
    """
    return await service.get_new_emissions(limit=limit)


@router.get("/categories", response_model=CategoryList, summary="Liste des catégories")
async def get_categories(service: EmissionService = Depends(get_emission_service)):
    """
    Récupère la liste des catégories avec le nombre d'émissions par catégorie.
    """
    categories = await service.get_categories()
    return {
        "categories": categories,
        "total_categories": len(categories)
    }


@router.get("/search", response_model=List[EmissionResponse], summary="Rechercher des émissions")
async def search_emissions(
    query: str = Query(..., min_length=1, max_length=100, description="Terme de recherche"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    limit: int = Query(20, ge=1, le=100, description="Limite de résultats"),
    offset: int = Query(0, ge=0, description="Offset pour pagination"),
    service: EmissionService = Depends(get_emission_service)
):
    """
    Recherche des émissions par terme de recherche.
    
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
    return await service.search_emissions(search_request)


@router.get("/{emission_id}", response_model=EmissionResponse, summary="Détails d'une émission")
async def get_emission_by_id(
    emission_id: str,
    service: EmissionService = Depends(get_emission_service)
):
    """
    Récupère les détails d'une émission spécifique.
    
    - **emission_id**: ID unique de l'émission
    """
    return await service.get_emission_by_id(emission_id)


@router.get("/{emission_id}/stats", response_model=EmissionStats, summary="Statistiques d'une émission")
async def get_emission_stats(
    emission_id: str,
    service: EmissionService = Depends(get_emission_service)
):
    """
    Récupère les statistiques d'une émission (vues, likes, etc.).
    
    - **emission_id**: ID unique de l'émission
    """
    return await service.get_emission_stats(emission_id)


@router.post("/{emission_id}/views", summary="Incrémenter les vues")
async def increment_views(
    emission_id: str,
    request: Optional[ViewIncrementRequest] = None,
    service: EmissionService = Depends(get_emission_service)
):
    """
    Incrémente le nombre de vues d'une émission.
    
    - **emission_id**: ID unique de l'émission
    - **request**: Données optionnelles (user_id, session_id)
    """
    success = await service.increment_views(emission_id, request)
    return {"success": success, "message": "Vues incrémentées avec succès"}


@router.post("/{emission_id}/likes", summary="Gérer les likes")
async def toggle_like(
    emission_id: str,
    request: LikeRequest,
    service: EmissionService = Depends(get_emission_service)
):
    """
    Ajoute ou retire un like d'une émission.
    
    - **emission_id**: ID unique de l'émission
    - **request**: Action (add/remove) et user_id optionnel
    """
    result = await service.toggle_like(emission_id, request)
    return result


# Routes administratives (protégées par authentification)

@router.post("/", response_model=EmissionResponse, summary="Créer une émission")
async def create_emission(
    emission_data: EmissionCreate,
    service: EmissionService = Depends(get_emission_service),
    current_user = Depends(get_admin_user)
):
    """
    Crée une nouvelle émission.
    
    *Nécessite des droits d'administration*
    """
    return await service.create_emission(emission_data)


@router.put("/{emission_id}", response_model=EmissionResponse, summary="Mettre à jour une émission")
async def update_emission(
    emission_id: str,
    emission_data: EmissionUpdate,
    service: EmissionService = Depends(get_emission_service),
    current_user = Depends(get_admin_user)
):
    """
    Met à jour une émission existante.
    
    *Nécessite des droits d'administration*
    """
    return await service.update_emission(emission_id, emission_data)


@router.delete("/{emission_id}", summary="Supprimer une émission")
async def delete_emission(
    emission_id: str,
    service: EmissionService = Depends(get_emission_service),
    current_user = Depends(get_admin_user)
):
    """
    Supprime (désactive) une émission.
    
    *Nécessite des droits d'administration*
    """
    success = await service.delete_emission(emission_id)
    return {"success": success, "message": "Émission supprimée avec succès"}