"""
Système de résilience aux erreurs pour éviter que le serveur ne plante
Si une section échoue, les autres continuent à fonctionner
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Callable, Any
import traceback
import logging

logger = logging.getLogger(__name__)

class ErrorResilience:
    """Gestionnaire de résilience aux erreurs"""
    
    @staticmethod
    async def safe_execute(
        func: Callable,
        *args,
        fallback_value: Any = None,
        error_message: str = "Une erreur est survenue",
        **kwargs
    ):
        """
        Exécute une fonction de manière sécurisée
        Si elle échoue, retourne une valeur par défaut au lieu de planter
        
        Args:
            func: Fonction à exécuter
            fallback_value: Valeur à retourner en cas d'erreur
            error_message: Message d'erreur personnalisé
            *args, **kwargs: Arguments de la fonction
        
        Returns:
            Résultat de la fonction ou fallback_value en cas d'erreur
        """
        try:
            if callable(func):
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                return result
            return fallback_value
        except Exception as e:
            logger.error(f"❌ Erreur dans safe_execute: {error_message}")
            logger.error(f"   Exception: {str(e)}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return fallback_value
    
    @staticmethod
    def create_error_response(
        error: Exception,
        status_code: int = 500,
        detail: str = None
    ) -> JSONResponse:
        """
        Crée une réponse d'erreur standardisée
        
        Args:
            error: Exception levée
            status_code: Code HTTP
            detail: Message détaillé
        
        Returns:
            JSONResponse avec l'erreur
        """
        error_detail = detail or str(error)
        
        logger.error(f"❌ Erreur API: {error_detail}")
        logger.error(f"   Type: {type(error).__name__}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error": error_detail,
                "type": type(error).__name__,
                "message": "Une erreur est survenue, mais le serveur continue de fonctionner"
            }
        )

# Middleware de résilience
async def resilience_middleware(request: Request, call_next):
    """
    Middleware qui capture toutes les erreurs non gérées
    et empêche le serveur de planter
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"❌ Erreur non gérée dans {request.url.path}")
        logger.error(f"   Exception: {str(e)}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
        
        # Retourner une erreur mais ne pas planter le serveur
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Erreur interne du serveur",
                "path": str(request.url.path),
                "message": "Cette section a rencontré une erreur, mais le reste du système fonctionne normalement"
            }
        )

# Décorateur pour sécuriser les endpoints
def safe_endpoint(fallback_value=None):
    """
    Décorateur pour sécuriser un endpoint
    Si l'endpoint échoue, retourne une valeur par défaut
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Laisser passer les HTTPException (erreurs intentionnelles)
                raise
            except Exception as e:
                logger.error(f"❌ Erreur dans endpoint {func.__name__}")
                logger.error(f"   Exception: {str(e)}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                
                # Retourner une réponse d'erreur mais ne pas planter
                return {
                    "success": False,
                    "error": str(e),
                    "data": fallback_value,
                    "message": "Cette fonctionnalité a rencontré une erreur, mais le serveur continue de fonctionner"
                }
        return wrapper
    return decorator

import asyncio
