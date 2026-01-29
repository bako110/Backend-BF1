from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.user import UserCreate, UserOut, UserLoginSchema
from app.services.user_service import create_user, get_user, list_users, login_user_service
from typing import List

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate):
    """Créer un nouveau compte utilisateur"""
    if len(user.password) > 72:
        raise HTTPException(status_code=400, detail="Le mot de passe ne doit pas dépasser 72 caractères.")
    return await create_user(user)

@router.post("/login")
async def login_user(data: UserLoginSchema):
    """Connexion avec email, username ou téléphone"""
    result = await login_user_service(data.identifier, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    return result

@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Récupérer les informations de l'utilisateur connecté"""
    return current_user

@router.get("/", response_model=List[UserOut])
async def get_all_users(current_user=Depends(get_admin_user)):
    """Lister tous les utilisateurs (admin seulement)"""
    return await list_users()

@router.get("/{user_id}", response_model=UserOut)
async def get_one_user(user_id: str, current_user=Depends(get_current_user)):
    """Récupérer un utilisateur par ID"""
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user
