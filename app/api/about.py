from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.models.about import AppInfo, TeamMember
from app.schemas.about import (
    AppInfoCreate, AppInfoUpdate, AppInfoOut,
    TeamMemberCreate, TeamMemberUpdate, TeamMemberOut
)
from app.utils.auth import get_admin_user
from app.models.user import User

router = APIRouter()


# ==================== App Info ====================

@router.get("/info", response_model=AppInfoOut)
async def get_app_info():
    """Récupérer les informations de l'application"""
    app_info = await AppInfo.find_one(AppInfo.is_active == True)
    
    if not app_info:
        # Créer des informations par défaut si aucune n'existe
        default_info = AppInfo(
            app_name="BF1 TV",
            version="1.0.0",
            build_number="100",
            release_date=datetime.utcnow(),
            description="Chaîne TV officielle BF1. Retrouvez le direct, les émissions, films, actualités et plus.",
            website="https://www.bf1tv.com",
            support_email="support@bf1tv.com",
            contact_phone="+221 XX XXX XX XX",
            facebook_url="https://facebook.com/bf1tv",
            twitter_url="https://twitter.com/bf1tv",
            instagram_url="https://instagram.com/bf1tv",
            youtube_url="https://youtube.com/bf1tv",
            privacy_policy_url="https://www.bf1tv.com/privacy",
            terms_url="https://www.bf1tv.com/terms",
            features=[
                "Direct TV en streaming",
                "Replays et émissions à la demande",
                "Interviews exclusives",
                "Archives vidéo premium",
                "Notifications en temps réel"
            ],
            changelog=[
                {
                    "version": "1.0.0",
                    "date": "2026-02-13",
                    "changes": ["Lancement initial de l'application"]
                }
            ],
            is_active=True
        )
        await default_info.insert()
        app_info = default_info
    
    return app_info


@router.get("/info/version/{version}", response_model=AppInfoOut)
async def get_app_info_by_version(version: str):
    """Récupérer les informations d'une version spécifique"""
    app_info = await AppInfo.find_one(AppInfo.version == version)
    
    if not app_info:
        raise HTTPException(status_code=404, detail="Version non trouvée")
    
    return app_info


@router.post("/info", response_model=AppInfoOut, status_code=status.HTTP_201_CREATED)
async def create_app_info(
    app_info: AppInfoCreate,
    current_user: User = Depends(get_admin_user)
):
    """Créer une nouvelle version de l'application (Admin uniquement)"""
    new_app_info = AppInfo(**app_info.dict())
    await new_app_info.insert()
    return new_app_info


@router.put("/info/{info_id}", response_model=AppInfoOut)
async def update_app_info(
    info_id: str,
    app_info_update: AppInfoUpdate,
    current_user: User = Depends(get_admin_user)
):
    """Mettre à jour les informations de l'application (Admin uniquement)"""
    app_info = await AppInfo.get(info_id)
    
    if not app_info:
        raise HTTPException(status_code=404, detail="Informations non trouvées")
    
    update_data = app_info_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app_info, field, value)
    
    app_info.updated_at = datetime.utcnow()
    await app_info.save()
    
    return app_info


@router.delete("/info/{info_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app_info(
    info_id: str,
    current_user: User = Depends(get_admin_user)
):
    """Supprimer une version de l'application (Admin uniquement)"""
    app_info = await AppInfo.get(info_id)
    
    if not app_info:
        raise HTTPException(status_code=404, detail="Informations non trouvées")
    
    await app_info.delete()


# ==================== Team Members ====================

@router.get("/team", response_model=List[TeamMemberOut])
async def get_team_members(
    limit: int = Query(50, ge=1, le=100)
):
    """Récupérer les membres de l'équipe"""
    team_members = await TeamMember.find(TeamMember.is_active == True).sort(TeamMember.order).limit(limit).to_list()
    return team_members


@router.get("/team/{member_id}", response_model=TeamMemberOut)
async def get_team_member(member_id: str):
    """Récupérer un membre de l'équipe spécifique"""
    member = await TeamMember.get(member_id)
    
    if not member:
        raise HTTPException(status_code=404, detail="Membre non trouvé")
    
    return member


@router.post("/team", response_model=TeamMemberOut, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    member: TeamMemberCreate,
    current_user: User = Depends(get_admin_user)
):
    """Ajouter un membre à l'équipe (Admin uniquement)"""
    new_member = TeamMember(**member.dict())
    await new_member.insert()
    return new_member


@router.put("/team/{member_id}", response_model=TeamMemberOut)
async def update_team_member(
    member_id: str,
    member_update: TeamMemberUpdate,
    current_user: User = Depends(get_admin_user)
):
    """Mettre à jour un membre de l'équipe (Admin uniquement)"""
    member = await TeamMember.get(member_id)
    
    if not member:
        raise HTTPException(status_code=404, detail="Membre non trouvé")
    
    update_data = member_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)
    
    member.updated_at = datetime.utcnow()
    await member.save()
    
    return member


@router.delete("/team/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(
    member_id: str,
    current_user: User = Depends(get_admin_user)
):
    """Supprimer un membre de l'équipe (Admin uniquement)"""
    member = await TeamMember.get(member_id)
    
    if not member:
        raise HTTPException(status_code=404, detail="Membre non trouvé")
    
    await member.delete()
