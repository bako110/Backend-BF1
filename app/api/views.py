"""
API pour gérer les vues des contenus
Permet d'incrémenter les vues sans authentification
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models.show import Show
from app.models.reportage import Reportage
from app.models.jtandmag import JTandMag
from app.models.divertissement import Divertissement
from app.models.archive import Archive
from app.models.movie import Movie
from app.models.reel import Reel
from app.models.sport import Sport

router = APIRouter()

class ViewRequest(BaseModel):
    content_id: str
    content_type: str  # 'show', 'reportage', 'divertissement', 'archive', 'jtandmag', 'movie', 'reel', 'sport'

@router.post("/increment")
async def increment_view(view_request: ViewRequest):
    """
    Incrémenter le nombre de vues d'un contenu
    Accessible sans authentification pour permettre le comptage pour tous les utilisateurs
    """
    try:
        content_id = view_request.content_id
        content_type = view_request.content_type
        
        print(f"📊 Incrémentation des vues pour {content_type} ID: {content_id}")
        
        # Déterminer le modèle selon le type de contenu
        model_map = {
            'show': Show,
            'reportage': Reportage,
            'divertissement': Divertissement,
            'archive': Archive,
            'jtandmag': JTandMag,
            'movie': Movie,
            'reel': Reel,
            'sport': Sport,
            'sports': Sport
        }
        
        if content_type not in model_map:
            raise HTTPException(
                status_code=400,
                detail=f"Type de contenu invalide: {content_type}"
            )
        
        Model = model_map[content_type]
        
        # Récupérer le contenu
        content = await Model.get(content_id)
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"{content_type} non trouvé"
            )
        
        # Incrémenter les vues
        content.views = (content.views or 0) + 1
        await content.save()
        
        print(f"✅ Vues incrémentées: {content.views}")
        
        return {
            "success": True,
            "content_id": content_id,
            "content_type": content_type,
            "views": content.views
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur incrémentation vues: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'incrémentation des vues: {str(e)}"
        )

@router.get("/{content_type}/{content_id}")
async def get_views(content_type: str, content_id: str):
    """
    Récupérer le nombre de vues d'un contenu
    Accessible sans authentification
    """
    try:
        model_map = {
            'show': Show,
            'replay': Replay,
            'interview': Interview,
            'archive': Archive,
            'trending_show': TrendingShow,
            'movie': Movie,
            'reel': Reel
        }
        
        if content_type not in model_map:
            raise HTTPException(
                status_code=400,
                detail=f"Type de contenu invalide: {content_type}"
            )
        
        Model = model_map[content_type]
        content = await Model.get(content_id)
        
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"{content_type} non trouvé"
            )
        
        return {
            "content_id": content_id,
            "content_type": content_type,
            "views": content.views or 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur récupération vues: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des vues: {str(e)}"
        )
