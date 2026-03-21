"""
API pour générer des usernames uniques
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.models.user import User
import re

router = APIRouter()

class UsernameRequest(BaseModel):
    email: EmailStr

class UsernameResponse(BaseModel):
    username: str
    is_available: bool

def generate_username_from_email(email: str) -> str:
    """
    Génère un username à partir d'un email
    Exemple: john.doe@example.com -> johndoe
    """
    # Extraire la partie avant @
    username_base = email.split('@')[0]
    
    # Nettoyer: enlever les caractères spéciaux, garder seulement lettres et chiffres
    username_base = re.sub(r'[^a-zA-Z0-9]', '', username_base)
    
    # Convertir en minuscules
    username_base = username_base.lower()
    
    # Limiter à 20 caractères
    username_base = username_base[:20]
    
    return username_base

@router.post("/suggest", response_model=UsernameResponse)
async def suggest_username(request: UsernameRequest):
    """
    Suggère un username unique basé sur l'email
    Si le username existe déjà, ajoute un numéro
    """
    try:
        # Générer le username de base
        base_username = generate_username_from_email(request.email)
        
        if not base_username:
            base_username = "user"
        
        # Vérifier si le username est disponible
        existing_user = await User.find_one({"username": base_username})
        
        if not existing_user:
            # Username disponible
            return UsernameResponse(username=base_username, is_available=True)
        
        # Si le username existe, ajouter un numéro
        counter = 1
        while True:
            suggested_username = f"{base_username}{counter}"
            existing_user = await User.find_one({"username": suggested_username})
            
            if not existing_user:
                return UsernameResponse(username=suggested_username, is_available=True)
            
            counter += 1
            
            # Limite de sécurité
            if counter > 9999:
                raise HTTPException(
                    status_code=500,
                    detail="Impossible de générer un username unique"
                )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check/{username}")
async def check_username_availability(username: str):
    """
    Vérifie si un username est disponible
    """
    try:
        existing_user = await User.find_one({"username": username})
        
        return {
            "username": username,
            "is_available": existing_user is None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
