"""API Routes for Statistics"""
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from typing import Dict, Any
from app.utils.auth import get_admin_user
from app.models.user import User
from app.models.movie import Movie
from app.models.reportage import Reportage
from app.models.jtandmag import JTandMag
from app.models.divertissement import Divertissement
from app.models.program import Program
from app.models.breakingNews import BreakingNews
from app.models.reel import Reel
from app.models.comment import Comment
from app.models.subscription import Subscription
from app.models.like import Like
from app.models.favorite import Favorite
from app.models.sport import Sport
from app.models.tele_realite import TeleRealite

router = APIRouter()


@router.get("/test")
async def test_stats():
    """Endpoint de test simple"""
    return {"status": "ok", "message": "Stats endpoint is working"}


async def calculate_growth(model, field_name: str = "created_at") -> Dict[str, Any]:
    """Calcule le nombre total et la croissance par rapport au mois précédent"""
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    
    # Calculer le début du mois précédent
    if now.month == 1:
        start_of_prev_month = datetime(now.year - 1, 12, 1)
        end_of_prev_month = datetime(now.year, 1, 1)
    else:
        start_of_prev_month = datetime(now.year, now.month - 1, 1)
        end_of_prev_month = start_of_month
    
    # Compter le total
    total = await model.count()
    
    # Compter ce mois
    current_month_count = await model.find(
        {field_name: {"$gte": start_of_month}}
    ).count()
    
    # Compter le mois précédent
    prev_month_count = await model.find(
        {field_name: {"$gte": start_of_prev_month, "$lt": end_of_prev_month}}
    ).count()
    
    # Calculer le pourcentage de croissance
    if prev_month_count > 0:
        growth = ((current_month_count - prev_month_count) / prev_month_count) * 100
    else:
        growth = 100 if current_month_count > 0 else 0
    
    return {
        "total": total,
        "current_month": current_month_count,
        "prev_month": prev_month_count,
        "growth": round(growth, 1)
    }


async def safe_calculate_growth(model, field_name: str = "created_at") -> Dict[str, Any]:
    """Calcule la croissance de manière sécurisée"""
    try:
        return await calculate_growth(model, field_name)
    except Exception as e:
        print(f"Error calculating growth for {model.__name__}: {e}")
        return {"total": 0, "current_month": 0, "prev_month": 0, "growth": 0}


@router.get("/dashboard")
async def get_dashboard_stats():
    """Récupère toutes les statistiques pour le dashboard avec croissance"""
    
    import asyncio
    
    # Exécuter tous les calculs en parallèle pour améliorer les performances
    results = await asyncio.gather(
        safe_calculate_growth(User),
        safe_calculate_growth(Movie),
        safe_calculate_growth(Reportage),
        safe_calculate_growth(Reel),
        safe_calculate_growth(Divertissement),
        safe_calculate_growth(Program),
        safe_calculate_growth(BreakingNews),
        safe_calculate_growth(JTandMag),
        safe_calculate_growth(Subscription),
        safe_calculate_growth(Comment),
        safe_calculate_growth(Like),
        safe_calculate_growth(Favorite),
        safe_calculate_growth(Sport),
        safe_calculate_growth(TeleRealite),
    )

    stats = {
        "users": results[0],
        "movies": results[1],
        "reportages": results[2],
        "reels": results[3],
        "divertissements": results[4],
        "programs": results[5],
        "news": results[6],
        "jtandmag": results[7],
        "subscriptions": results[8],
        "comments": results[9],
        "likes": results[10],
        "favorites": results[11],
        "sports": results[12],
        "tele_realite": results[13],
    }
    
    return stats
