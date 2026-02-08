from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime

from app.models.user_settings import UserSettings
from app.schemas.user_settings import UserSettingsCreate, UserSettingsUpdate, UserSettingsOut
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/my-settings", response_model=UserSettingsOut)
async def get_my_settings(current_user: User = Depends(get_current_user)):
    """Récupérer les paramètres de l'utilisateur connecté"""
    settings = await UserSettings.find_one(UserSettings.user_id == str(current_user.id))
    
    if not settings:
        # Créer des paramètres par défaut si inexistants
        settings = UserSettings(user_id=str(current_user.id))
        await settings.insert()
    
    return settings


@router.put("/my-settings", response_model=UserSettingsOut)
async def update_my_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour les paramètres de l'utilisateur connecté"""
    settings = await UserSettings.find_one(UserSettings.user_id == str(current_user.id))
    
    if not settings:
        # Créer des paramètres par défaut si inexistants
        settings = UserSettings(user_id=str(current_user.id))
        await settings.insert()
    
    # Mettre à jour les champs fournis
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    settings.updated_at = datetime.utcnow()
    await settings.save()
    
    return settings


@router.post("/my-settings/reset", response_model=UserSettingsOut)
async def reset_my_settings(current_user: User = Depends(get_current_user)):
    """Réinitialiser les paramètres aux valeurs par défaut"""
    settings = await UserSettings.find_one(UserSettings.user_id == str(current_user.id))
    
    if settings:
        await settings.delete()
    
    # Créer de nouveaux paramètres par défaut
    new_settings = UserSettings(user_id=str(current_user.id))
    await new_settings.insert()
    
    return new_settings
