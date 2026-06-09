from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from fastapi import HTTPException

from app.models.missed import Missed
from app.schemas.missed import MissedCreate, MissedUpdate


class MissedService:
    """Service pour la gestion des contenus manqués"""

    async def _find_missed_by_id(self, missed_id: str) -> Optional[Missed]:
        """Méthode utilitaire pour trouver un contenu manqué par ID"""
        try:
            missed = await Missed.get(missed_id)
            if missed:
                return missed
        except Exception:
            pass
        
        try:
            missed = await Missed.find_one({"id": missed_id})
            if missed:
                return missed
        except Exception:
            pass
        
        if ObjectId.is_valid(missed_id):
            try:
                missed = await Missed.find_one({"_id": ObjectId(missed_id)})
                if missed:
                    return missed
            except Exception:
                pass
        
        return None

    async def create_missed(self, missed_data: MissedCreate) -> Missed:
        """Créer un nouveau contenu manqué"""
        missed_dict = missed_data.model_dump()
        missed_dict["views"] = 0
        missed_dict["likes"] = 0
        missed_dict["created_at"] = datetime.utcnow()
        missed_dict["updated_at"] = datetime.utcnow()
        
        if not missed_dict.get("published_at"):
            missed_dict["published_at"] = datetime.utcnow()
        
        missed = Missed(**missed_dict)
        await missed.insert()
        return missed

    async def get_missed_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Récupérer la liste paginée des contenus manqués"""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        total = await Missed.find(query).count()
        
        items = await Missed.find(query).sort("-aired_at").skip(skip).limit(limit).to_list()
        
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def get_missed_by_id(self, missed_id: str) -> Optional[Missed]:
        """Récupérer un contenu manqué par ID"""
        return await self._find_missed_by_id(missed_id)

    async def update_missed(self, missed_id: str, missed_data: MissedUpdate) -> Optional[Missed]:
        """Mettre à jour un contenu manqué"""
        missed = await self._find_missed_by_id(missed_id)
        
        if not missed:
            return None
        
        update_data = missed_data.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
        
        update_data["updated_at"] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(missed, key, value)
        
        await missed.save()
        return missed

    async def delete_missed(self, missed_id: str) -> bool:
        """Supprimer un contenu manqué"""
        missed = await self._find_missed_by_id(missed_id)
        
        if not missed:
            return False
        
        await missed.delete()
        return True

    async def increment_missed_views(self, missed_id: str) -> bool:
        """Incrémenter le nombre de vues d'un contenu manqué"""
        missed = await self._find_missed_by_id(missed_id)
        
        if not missed:
            return False
        
        missed.views += 1
        await missed.save()
        return True

    async def get_missed_by_category(
        self, 
        category: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> Dict[str, Any]:
        """Récupérer les contenus manqués par catégorie"""
        query = {"category": category, "is_active": True}
        
        total = await Missed.find(query).count()
        
        items = await Missed.find(query).sort("-aired_at").skip(skip).limit(limit).to_list()
        
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def search_missed(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> Dict[str, Any]:
        """Rechercher des contenus manqués"""
        from beanie.operators import Or, RegEx
        
        search_query = Or(
            RegEx(Missed.title, query, options="i"),
            RegEx(Missed.description, query, options="i"),
            RegEx(Missed.tags, query, options="i")
        )
        
        total = await Missed.find(search_query, Missed.is_active == True).count()
        
        items = await Missed.find(
            search_query, 
            Missed.is_active == True
        ).sort("-aired_at").skip(skip).limit(limit).to_list()
        
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }


missed_service = MissedService()
