from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check():
    """
    Endpoint de health check pour vérifier que le backend est opérationnel.
    Utilisé par le splash screen pour attendre que le backend soit prêt.
    """
    return {
        "status": "ok",
        "message": "Backend BF1 is running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/status")
async def get_status():
    """
    Endpoint de status détaillé du backend
    """
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "api": "running"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
