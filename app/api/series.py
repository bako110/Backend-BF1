from fastapi import APIRouter, HTTPException, Depends, Query
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.series import (
    SeriesCreate, SeriesUpdate, SeriesOut, SeriesListResponse,
    SeasonCreate, SeasonUpdate, SeasonOut, SeasonListResponse,
    EpisodeCreate, EpisodeUpdate, EpisodeOut, EpisodeListResponse
)
from app.services.series_service import series_service, season_service, episode_service
from typing import List, Optional

router = APIRouter()

# ===== ROUTES SERIES =====

@router.post("/series", response_model=SeriesOut)
async def create_series(series: SeriesCreate, current_user=Depends(get_admin_user)):
    """Créer une nouvelle série (admin seulement)"""
    try:
        new_series = await series_service.create_series(series)
        return new_series
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/series", response_model=SeriesListResponse)
async def get_all_series(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user=Depends(get_current_user)
):
    """Récupérer toutes les séries avec pagination"""
    try:
        result = await series_service.get_all_series(page, limit, status)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/series/{series_id}", response_model=SeriesOut)
async def get_series(series_id: str, current_user=Depends(get_current_user)):
    """Récupérer une série par son ID"""
    series = await series_service.get_series_by_id(series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Série non trouvée")
    return series

@router.patch("/series/{series_id}", response_model=SeriesOut)
async def update_series(
    series_id: str, 
    series: SeriesUpdate, 
    current_user=Depends(get_admin_user)
):
    """Mettre à jour une série (admin seulement)"""
    try:
        updated_series = await series_service.update_series(series_id, series)
        if not updated_series:
            raise HTTPException(status_code=404, detail="Série non trouvée")
        return updated_series
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/series/{series_id}")
async def delete_series(series_id: str, current_user=Depends(get_admin_user)):
    """Supprimer une série et tous ses contenus (admin seulement)"""
    success = await series_service.delete_series(series_id)
    if not success:
        raise HTTPException(status_code=404, detail="Série non trouvée")
    return {"message": "Série supprimée avec succès"}

# ===== ROUTES SEASONS =====

@router.post("/series/{series_id}/seasons", response_model=SeasonOut)
async def create_season(
    series_id: str,
    season: SeasonCreate,
    current_user=Depends(get_admin_user)
):
    """Créer une nouvelle saison pour une série (admin seulement)"""
    try:
        # Vérifier que l'ID de la série correspond
        season.series_id = series_id
        new_season = await season_service.create_season(season)
        return new_season
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/series/{series_id}/seasons", response_model=SeasonListResponse)
async def get_seasons_by_series(
    series_id: str,
    current_user=Depends(get_current_user)
):
    """Récupérer toutes les saisons d'une série"""
    try:
        seasons = await season_service.get_seasons_by_series(series_id)
        return {
            "seasons": seasons,
            "total": len(seasons)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/seasons/{season_id}", response_model=SeasonOut)
async def update_season(
    season_id: str,
    season: SeasonUpdate,
    current_user=Depends(get_admin_user)
):
    """Mettre à jour une saison (admin seulement)"""
    try:
        updated_season = await season_service.update_season(season_id, season)
        if not updated_season:
            raise HTTPException(status_code=404, detail="Saison non trouvée")
        return updated_season
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/seasons/{season_id}")
async def delete_season(season_id: str, current_user=Depends(get_admin_user)):
    """Supprimer une saison et tous ses épisodes (admin seulement)"""
    success = await season_service.delete_season(season_id)
    if not success:
        raise HTTPException(status_code=404, detail="Saison non trouvée")
    return {"message": "Saison supprimée avec succès"}

# ===== ROUTES EPISODES =====

@router.post("/seasons/{season_id}/episodes", response_model=EpisodeOut)
async def create_episode(
    season_id: str,
    episode: EpisodeCreate,
    current_user=Depends(get_admin_user)
):
    """Créer un nouvel épisode pour une saison (admin seulement)"""
    try:
        # Vérifier que l'ID de la saison correspond
        episode.season_id = season_id
        new_episode = await episode_service.create_episode(episode)
        return new_episode
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/series/{series_id}/episodes", response_model=EpisodeListResponse)
async def get_episodes_by_series(
    series_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user)
):
    """Récupérer tous les épisodes d'une série avec pagination"""
    try:
        result = await episode_service.get_episodes_by_series(series_id, page, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seasons/{season_id}/episodes", response_model=List[EpisodeOut])
async def get_episodes_by_season(
    season_id: str,
    current_user=Depends(get_current_user)
):
    """Récupérer tous les épisodes d'une saison"""
    try:
        episodes = await episode_service.get_episodes_by_season(season_id)
        return episodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/episodes/{episode_id}", response_model=EpisodeOut)
async def update_episode(
    episode_id: str,
    episode: EpisodeUpdate,
    current_user=Depends(get_admin_user)
):
    """Mettre à jour un épisode (admin seulement)"""
    try:
        updated_episode = await episode_service.update_episode(episode_id, episode)
        if not updated_episode:
            raise HTTPException(status_code=404, detail="Épisode non trouvé")
        return updated_episode
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/episodes/{episode_id}")
async def delete_episode(episode_id: str, current_user=Depends(get_admin_user)):
    """Supprimer un épisode (admin seulement)"""
    success = await episode_service.delete_episode(episode_id)
    if not success:
        raise HTTPException(status_code=404, detail="Épisode non trouvé")
    return {"message": "Épisode supprimé avec succès"}