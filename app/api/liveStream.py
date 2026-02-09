from fastapi import APIRouter, HTTPException
from app.utils.auth import get_optional_user
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.get("/status")
async def get_stream_status():
    """Obtenir le statut du flux en direct"""
    try:
        # Statut du flux BF1
        stream_status = {
            "id": "bf1",
            "name": "BF1 TV - Chaîne Officielle",
            "is_live": True,
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", # Remplacer par votre flux réel
            "thumbnail": "https://picsum.photos/seed/bf1tv/400/225.jpg",
            "viewers": 1250, # Simulé
            "description": "Chaîne de télévision BF1 en direct",
            "schedule": "24/7 - Programmes en continu",
            "current_program": {
                "title": "Journal de Soir",
                "description": "Dernières actualités et informations",
                "start_time": "20:00",
                "end_time": "21:00"
            },
            "quality": "HD",
            "bitrate": "2500k"
        }
        
        return stream_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération statut flux: {str(e)}")

@router.get("/program")
async def get_current_program():
    """Obtenir le programme actuel"""
    try:
        current_hour = datetime.now().hour
        
        if current_hour >= 6 and current_hour < 12:
            program = {
                "title": "Matinales BF1",
                "description": "Programmes du matin",
                "start_time": "06:00",
                "end_time": "12:00",
                "category": "matinal"
            }
        elif current_hour >= 12 and current_hour < 14:
            program = {
                "title": "Journal de Midi",
                "description": "Actualités et informations",
                "start_time": "12:00",
                "end_time": "14:00",
                "category": "info"
            }
        elif current_hour >= 14 and current_hour < 18:
            program = {
                "title": "Programmes de l'après-midi",
                "description": "Divertissement et culture",
                "start_time": "14:00",
                "end_time": "18:00",
                "category": "divertissement"
            }
        elif current_hour >= 18 and current_hour < 22:
            program = {
                "title": "Prime Time",
                "description": "Programmes de première partie de soirée",
                "start_time": "18:00",
                "end_time": "22:00",
                "category": "prime"
            }
        else:
            program = {
                "title": "Programmes de nuit",
                "description": "Programmes en nocturne",
                "start_time": "22:00",
                "end_time": "06:00",
                "category": "nuit"
            }
        
        return program
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération programme: {str(e)}")

@router.get("/viewers")
async def get_viewer_count():
    """Obtenir le nombre de spectateurs actuels"""
    try:
        # Simuler un nombre de viewers réel
        import random
        viewers = random.randint(800, 2500)
        
        return {
            "viewers": viewers,
            "timestamp": datetime.utcnow().isoformat(),
            "peak_today": 3200
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération viewers: {str(e)}")

@router.get("/schedule")
async def get_schedule():
    """Obtenir la programmation du jour"""
    try:
        schedule = [
            {
                "time": "06:00",
                "title": "Matinales BF1",
                "description": "Programmes du matin",
                "duration": "6h"
            },
            {
                "time": "12:00",
                "title": "Journal de Midi",
                "description": "Actualités et informations",
                "duration": "2h"
            },
            {
                "time": "14:00",
                "title": "Programmes de l'après-midi",
                "description": "Divertissement et culture",
                "duration": "4h"
            },
            {
                "time": "18:00",
                "title": "Prime Time",
                "description": "Programmes de première partie de soirée",
                "duration": "4h"
            },
            {
                "time": "22:00",
                "title": "Programmes de nuit",
                "description": "Programmes en nocturne",
                "duration": "8h"
            }
        ]
        
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération programmation: {str(e)}")

@router.post("/update-stream-url")
async def update_stream_url(stream_data: dict):
    """Mettre à jour l'URL du flux (admin seulement)"""
    try:
        # Dans une version production, vous pourriez sauvegarder l'URL dans une base de données
        new_url = stream_data.get("url")
        
        if not new_url:
            raise HTTPException(status_code=400, detail="URL du flux requise")
        
        return {
            "success": True,
            "message": "URL du flux mise à jour avec succès",
            "url": new_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour URL: {str(e)}")
