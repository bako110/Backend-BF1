from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.user import UserCreate, UserOut, UserLoginSchema
from app.services.user_service import create_user, get_user, list_users, login_user_service, set_user_active, delete_user
from typing import List

router = APIRouter()

@router.post("/register")
async def register_user(user: UserCreate):
    """Créer un nouveau compte utilisateur et le connecter automatiquement"""
    if len(user.password) > 72:
        raise HTTPException(status_code=400, detail="Le mot de passe ne doit pas dépasser 72 caractères.")
    
    # Créer l'utilisateur
    created_user = await create_user(user)
    
    # Connecter automatiquement l'utilisateur après inscription
    login_result = await login_user_service(user.username, user.password)
    
    return login_result

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


@router.patch("/{user_id}/ban", response_model=UserOut)
async def ban_user(user_id: str, current_user=Depends(get_admin_user)):
    """Bannir un utilisateur (admin seulement)"""
    user = await set_user_active(user_id, False)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


@router.patch("/{user_id}/unban", response_model=UserOut)
async def unban_user(user_id: str, current_user=Depends(get_admin_user)):
    """Débannir un utilisateur (admin seulement)"""
    user = await set_user_active(user_id, True)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


@router.delete("/{user_id}")
async def delete_one_user(user_id: str, current_user=Depends(get_admin_user)):
    """Supprimer un utilisateur (admin seulement)"""
    deleted = await delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return {"ok": True}
