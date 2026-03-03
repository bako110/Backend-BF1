"""
API de recherche globale
Recherche dans tous les types de contenu : sports, shows, reportages, divertissements, JT&Mag, news, archives
"""

from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from app.models.sport import Sport
from app.models.show import Show
from app.models.reportage import Reportage
from app.models.divertissement import Divertissement
from app.models.jtandmag import JTandMag
from app.models.breakingNews import BreakingNews
from app.models.archive import Archive

router = APIRouter()

@router.get("/")
async def search_content(
    q: str = Query(..., min_length=2, description="Terme de recherche"),
    limit: int = Query(8, ge=1, le=50, description="Nombre de résultats par catégorie")
):
    """
    Recherche globale dans tous les types de contenu
    """
    query = q.strip().lower()
    
    results = {
        "query": q,
        "items": [],
        "categoryResults": {},
        "suggestions": [],
        "totalFound": 0,
        "hasMore": False
    }
    
    try:
        # Recherche dans les sports
        sports = await Sport.find(
            {"$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"sport_type": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(limit).to_list()
        
        sports_formatted = [
            {
                "id": str(s.id),
                "title": s.title,
                "description": s.description,
                "image_url": s.image_url or s.image,
                "type": "sport",
                "sport_type": s.sport_type
            }
            for s in sports
        ]
        
        # Recherche dans les shows
        shows = await Show.find(
            {"$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(limit).to_list()
        
        shows_formatted = [
            {
                "id": str(s.id),
                "title": s.title,
                "description": s.description,
                "image_url": s.image_url or s.thumbnail,
                "type": "show"
            }
            for s in shows
        ]
        
        # Recherche dans les reportages
        reportages = await Reportage.find(
            {"$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(limit).to_list()
        
        reportages_formatted = [
            {
                "id": str(r.id),
                "title": r.title,
                "description": r.description,
                "image_url": r.image_url or r.image,
                "type": "reportage"
            }
            for r in reportages
        ]
        
        # Recherche dans les divertissements
        divertissements = await Divertissement.find(
            {"$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(limit).to_list()
        
        divertissements_formatted = [
            {
                "id": str(d.id),
                "title": d.title,
                "description": d.description,
                "image_url": d.image_url or d.image,
                "type": "divertissement"
            }
            for d in divertissements
        ]
        
        # Recherche dans JT & Mag
        jtandmag = await JTandMag.find(
            {"$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(limit).to_list()
        
        jtandmag_formatted = [
            {
                "id": str(j.id),
                "title": j.title,
                "description": j.description,
                "image_url": j.image_url or j.image,
                "type": "jtandmag"
            }
            for j in jtandmag
        ]
        
        # Recherche dans les actualités
        news = await BreakingNews.find(
            {"$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(limit).to_list()
        
        news_formatted = [
            {
                "id": str(n.id),
                "title": n.title,
                "description": n.content[:200] if n.content else "",
                "image_url": n.image_url,
                "type": "news"
            }
            for n in news
        ]
        
        # Recherche dans les archives
        archives = await Archive.find(
            {"$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(limit).to_list()
        
        archives_formatted = [
            {
                "id": str(a.id),
                "title": a.title,
                "description": a.description,
                "image_url": a.image_url or a.image,
                "type": "archive"
            }
            for a in archives
        ]
        
        # Combiner tous les résultats
        all_items = (
            sports_formatted + 
            shows_formatted + 
            reportages_formatted + 
            divertissements_formatted + 
            jtandmag_formatted + 
            news_formatted + 
            archives_formatted
        )
        
        # Organiser par catégorie
        results["categoryResults"] = {
            "sports": sports_formatted,
            "shows": shows_formatted,
            "reportages": reportages_formatted,
            "divertissements": divertissements_formatted,
            "jtandmag": jtandmag_formatted,
            "news": news_formatted,
            "archives": archives_formatted
        }
        
        results["items"] = all_items
        results["totalFound"] = len(all_items)
        
        # Générer des suggestions basées sur les résultats
        if len(all_items) > 0:
            suggestions = list(set([item["title"][:30] for item in all_items[:5]]))
            results["suggestions"] = suggestions[:3]
        
        return results
        
    except Exception as e:
        print(f"❌ Erreur recherche: {e}")
        return results
