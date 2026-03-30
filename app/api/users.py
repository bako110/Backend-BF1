from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.user import UserCreate, UserOut, UserLoginSchema, UserLocationUpdate
from app.services.user_service import create_user, get_user, list_users, login_user_service, set_user_active, delete_user
from app.models.user import User
from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr
import secrets

router = APIRouter()


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    """
    Demande de réinitialisation du mot de passe par email.
    Retourne toujours 200 pour ne pas révéler l'existence d'un compte.
    """
    user = await User.find_one({"email": data.email})
    if user:
        # Générer un token sécurisé (32 bytes hex)
        reset_token = secrets.token_urlsafe(32)
        # Stocker le token en attendant l'envoi email (à connecter à un service email)
        import datetime as dt
        user.reset_token = reset_token
        user.reset_token_expires = dt.datetime.utcnow() + dt.timedelta(hours=2)
        await user.save()
        # TODO: Envoyer l'email via votre service (SendGrid, SMTP, etc.)
        # Exemple: await send_reset_email(user.email, reset_token)
        print(f"[ForgotPassword] Token pour {user.email}: {reset_token}")

    # Toujours 200 pour ne pas divulguer l'existence du compte
    return {"message": "Si cet email est associé à un compte, vous recevrez un lien de réinitialisation."}

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

@router.patch("/me/location", response_model=UserOut)
async def update_user_location(location: UserLocationUpdate, current_user=Depends(get_current_user)):
    """Mettre à jour la localisation de l'utilisateur connecté"""
    print(f"📍 [API] Mise à jour localisation pour {current_user.username}")
    print(f"📍 [API] Données reçues: {location.dict()}")
    
    # Mettre à jour les champs de localisation
    if location.country_code is not None:
        current_user.location_country_code = location.country_code
        print(f"  ✓ country_code: {location.country_code}")
    if location.is_in_country is not None:
        current_user.location_is_in_country = location.is_in_country
        print(f"  ✓ is_in_country: {location.is_in_country}")
    if location.latitude is not None:
        current_user.location_latitude = location.latitude
        print(f"  ✓ latitude: {location.latitude}")
    if location.longitude is not None:
        current_user.location_longitude = location.longitude
        print(f"  ✓ longitude: {location.longitude}")
    
    current_user.location_updated_at = datetime.utcnow()
    current_user.updated_at = datetime.utcnow()
    
    await current_user.save()
    print(f"✅ [API] Localisation enregistrée pour {current_user.username}")
    
    return current_user

@router.get("/me/location")
async def get_user_location(current_user=Depends(get_current_user)):
    """Récupérer la localisation de l'utilisateur connecté"""
    return {
        "username": current_user.username,
        "country_code": current_user.location_country_code,
        "is_in_country": current_user.location_is_in_country,
        "latitude": current_user.location_latitude,
        "longitude": current_user.location_longitude,
        "updated_at": current_user.location_updated_at,
        "price_multiplier": 1 if current_user.location_is_in_country else 3
    }

@router.get("", response_model=List[UserOut])
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
