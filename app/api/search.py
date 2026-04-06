"""
API de recherche globale
Recherche dans tous les types de contenu : sports, shows, reportages, divertissements, JT&Mag, news, archives
"""

from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from app.models.sport import Sport
from app.models.reportage import Reportage
from app.models.divertissement import Divertissement
from app.models.jtandmag import JTandMag
from app.models.breakingNews import BreakingNews
from app.models.archive import Archive
from app.models.tele_realite import TeleRealite

router = APIRouter()

@router.get("")
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
                "description": s.description or "",
                "image_url": s.image or s.thumbnail or "",
                "type": "sport",
                "sport_type": s.sport_type or ""
            }
            for s in sports
        ]
        
        # Recherche dans télé-réalité & événements
        tele_realite_items = await TeleRealite.find(
            {"$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}},
            ]}
        ).limit(limit).to_list()

        tele_realite_formatted = [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description or "",
                "image_url": getattr(t, 'thumbnail', None) or getattr(t, 'image', None) or "",
                "type": t.sub_type or "tele_realite",
            }
            for t in tele_realite_items
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
                "description": r.description or "",
                "image_url": getattr(r, 'image_url', None) or getattr(r, 'thumbnail', None) or getattr(r, 'image', None) or "",
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
                "description": d.description or "",
                "image_url": getattr(d, 'image_url', None) or getattr(d, 'image', None) or "",
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
                "description": j.description or "",
                "image_url": getattr(j, 'image_url', None) or getattr(j, 'image', None) or "",
                "type": "jtandmag"
            }
            for j in jtandmag
        ]
        
        # Recherche dans les actualités
        news = await BreakingNews.find(
            {"$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(limit).to_list()
        
        news_formatted = [
            {
                "id": str(n.id),
                "title": n.title,
                "description": (n.description[:200] if n.description else ""),
                "image_url": getattr(n, 'image', None) or "",
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
                "description": a.description or "",
                "image_url": getattr(a, 'image_url', None) or getattr(a, 'image', None) or "",
                "type": "archive"
            }
            for a in archives
        ]
        
        # Combiner tous les résultats
        all_items = (
            sports_formatted +
            tele_realite_formatted +
            reportages_formatted +
            divertissements_formatted +
            jtandmag_formatted +
            news_formatted +
            archives_formatted
        )

        # Organiser par catégorie
        results["categoryResults"] = {
            "sports": sports_formatted,
            "tele_realite": tele_realite_formatted,
            "reportages": reportages_formatted,
            "divertissements": divertissements_formatted,
            "jtandmag": jtandmag_formatted,
            "news": news_formatted,
            "archives": archives_formatted,
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
