from app.models.series import Series, Season, Episode
from app.schemas.series import SeriesCreate, SeriesUpdate, SeasonCreate, SeasonUpdate, EpisodeCreate, EpisodeUpdate
from typing import List, Optional, Dict
from uuid import UUID

class SeriesService:
    def __init__(self):
        pass

    async def create_series(self, series_data: SeriesCreate) -> Series:
        """Créer une nouvelle série"""
        series = Series(**series_data.dict())
        await series.insert()
        return series

    async def get_series_by_id(self, series_id: str) -> Optional[Series]:
        """Récupérer une série par son ID"""
        return await Series.get(series_id)

    async def get_all_series(self, page: int = 1, limit: int = 20, status: str = None) -> dict:
        """Récupérer toutes les séries avec pagination"""
        skip = (page - 1) * limit
        
        if status:
            query = Series.find(Series.status == status)
        else:
            query = Series.find_all()
        
        # Récupérer les séries avec pagination
        series_list = await query.skip(skip).limit(limit).to_list()
        
        # Compter le total
        total = await query.count()
        
        pages = (total + limit - 1) // limit
        
        return {
            "series": series_list,
            "total": total,
            "page": page,
            "pages": pages
        }

    async def update_series(self, series_id: str, series_data: SeriesUpdate) -> Optional[Series]:
        """Mettre à jour une série"""
        series = await Series.get(series_id)
        if not series:
            return None
        
        update_data = series_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(series, key, value)
        
        await series.save()
        return series

    async def delete_series(self, series_id: str) -> bool:
        """Supprimer une série et tous ses épisodes/saisons"""
        series = await Series.get(series_id)
        if not series:
            return False
        
        # Supprimer d'abord tous les épisodes et saisons liés
        await Episode.find(Episode.series_id == series_id).delete()
        await Season.find(Season.series_id == series_id).delete()
        
        await series.delete()
        return True

class SeasonService:
    def __init__(self):
        pass

    async def create_season(self, season_data: SeasonCreate) -> Season:
        """Créer une nouvelle saison"""
        # Vérifier que la série existe
        series = await Series.get(str(season_data.series_id))
        if not series:
            raise ValueError("Série non trouvée")
        
        # Vérifier que le numéro de saison n'existe pas déjà
        existing = await Season.find_one(
            Season.series_id == str(season_data.series_id),
            Season.season_number == season_data.season_number
        )
        if existing:
            raise ValueError("Cette saison existe déjà pour cette série")
        
        season = Season(**season_data.dict())
        season.series_id = str(season_data.series_id)
        await season.insert()
        
        # Mettre à jour le nombre total de saisons dans la série
        seasons_count = await Season.find(Season.series_id == str(season_data.series_id)).count()
        series.total_seasons = max(series.total_seasons, seasons_count)
        await series.save()
        
        return season

    async def get_seasons_by_series(self, series_id: str) -> List[Season]:
        """Récupérer toutes les saisons d'une série"""
        seasons = await Season.find(Season.series_id == series_id).sort(+Season.season_number).to_list()
        
        # Calculer le nombre d'épisodes pour chaque saison
        for season in seasons:
            season.episode_count = await Episode.find(Episode.season_id == str(season.id)).count()
        
        return seasons

    async def update_season(self, season_id: str, season_data: SeasonUpdate) -> Optional[Season]:
        """Mettre à jour une saison"""
        season = await Season.get(season_id)
        if not season:
            return None
        
        update_data = season_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(season, key, value)
        
        await season.save()
        return season

    async def delete_season(self, season_id: str) -> bool:
        """Supprimer une saison et tous ses épisodes"""
        season = await Season.get(season_id)
        if not season:
            return False
        
        # Supprimer tous les épisodes de cette saison
        await Episode.find(Episode.season_id == season_id).delete()
        
        await season.delete()
        return True

class EpisodeService:
    def __init__(self):
        pass

    async def create_episode(self, episode_data: EpisodeCreate) -> Episode:
        """Créer un nouvel épisode"""
        # Vérifier que la série et la saison existent
        series = await Series.get(str(episode_data.series_id))
        season = await Season.get(str(episode_data.season_id))
        
        if not series or not season:
            raise ValueError("Série ou saison non trouvée")
        
        # Vérifier que le numéro d'épisode n'existe pas déjà dans cette saison
        existing = await Episode.find_one(
            Episode.season_id == str(episode_data.season_id),
            Episode.episode_number == episode_data.episode_number
        )
        if existing:
            raise ValueError("Cet épisode existe déjà dans cette saison")
        
        episode = Episode(**episode_data.dict())
        episode.series_id = str(episode_data.series_id)
        episode.season_id = str(episode_data.season_id)
        await episode.insert()
        
        # Mettre à jour les compteurs
        series.total_episodes = await Episode.find(Episode.series_id == str(episode_data.series_id)).count()
        season.episode_count = await Episode.find(Episode.season_id == str(episode_data.season_id)).count()
        
        await series.save()
        await season.save()
        
        return episode

    async def get_episodes_by_series(self, series_id: str, page: int = 1, limit: int = 20) -> dict:
        """Récupérer tous les épisodes d'une série avec pagination"""
        skip = (page - 1) * limit
        
        query = Episode.find(Episode.series_id == series_id)
        total = await query.count()
        
        episodes = await query.skip(skip).limit(limit).to_list()
        
        pages = (total + limit - 1) // limit
        
        return {
            "episodes": episodes,
            "total": total,
            "page": page,
            "pages": pages
        }

    async def get_episodes_by_season(self, season_id: str) -> List[Episode]:
        """Récupérer tous les épisodes d'une saison"""
        return await Episode.find(Episode.season_id == season_id).sort(+Episode.episode_number).to_list()

    async def update_episode(self, episode_id: str, episode_data: EpisodeUpdate) -> Optional[Episode]:
        """Mettre à jour un épisode"""
        episode = await Episode.get(episode_id)
        if not episode:
            return None
        
        update_data = episode_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(episode, key, value)
        
        await episode.save()
        return episode

    async def delete_episode(self, episode_id: str) -> bool:
        """Supprimer un épisode"""
        episode = await Episode.get(episode_id)
        if not episode:
            return False
        
        series_id = episode.series_id
        season_id = episode.season_id
        
        await episode.delete()
        
        # Mettre à jour les compteurs
        series = await Series.get(series_id)
        season = await Season.get(season_id)
        
        if series:
            series.total_episodes = await Episode.find(Episode.series_id == series_id).count()
            await series.save()
        if season:
            season.episode_count = await Episode.find(Episode.season_id == season_id).count()
            await season.save()
        
        return True

# Instances des services
series_service = SeriesService()
season_service = SeasonService()
episode_service = EpisodeService()