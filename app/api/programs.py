"""API Routes for Programs, Live Channels and Reminders"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from app.utils.auth import get_current_user, get_admin_user, get_optional_user
from app.schemas.program import (
    ProgramCreate, ProgramUpdate, ProgramOut, ProgramGridOut, ProgramWeekOut,
    ProgramFilterParams, ProgramReminderCreate, ProgramReminderUpdate, ProgramReminderOut,
    LiveChannelCreate, LiveChannelUpdate, LiveChannelOut
)
from app.services import program_service

router = APIRouter()


# ==================== LIVE CHANNEL ROUTES ====================

@router.post("/channels", response_model=LiveChannelOut, tags=["Live Channels"])
async def create_channel(
    data: LiveChannelCreate,
    current_user=Depends(get_admin_user)
):
    """Créer une nouvelle chaîne TV (admin only)"""
    channel = await program_service.create_channel(data)
    return channel


@router.get("/channels", response_model=List[LiveChannelOut], tags=["Live Channels"])
async def list_channels(
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_optional_user)
):
    """Lister toutes les chaînes TV"""
    channels = await program_service.list_channels(
        is_active=is_active, skip=skip, limit=limit
    )
    return channels


@router.get("/channels/{channel_id}", response_model=LiveChannelOut, tags=["Live Channels"])
async def get_channel(
    channel_id: str,
    current_user=Depends(get_optional_user)
):
    """Récupérer une chaîne par ID"""
    channel = await program_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Chaîne non trouvée")
    return channel


@router.patch("/channels/{channel_id}", response_model=LiveChannelOut, tags=["Live Channels"])
async def update_channel(
    channel_id: str,
    data: LiveChannelUpdate,
    current_user=Depends(get_admin_user)
):
    """Mettre à jour une chaîne (admin only)"""
    channel = await program_service.update_channel(channel_id, data)
    if not channel:
        raise HTTPException(status_code=404, detail="Chaîne non trouvée")
    return channel


@router.delete("/channels/{channel_id}", tags=["Live Channels"])
async def delete_channel(
    channel_id: str,
    current_user=Depends(get_admin_user)
):
    """Supprimer une chaîne (admin only)"""
    deleted = await program_service.delete_channel(channel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chaîne non trouvée")
    return {"ok": True, "message": "Chaîne supprimée"}


# ==================== PROGRAM ROUTES ====================

@router.post("/", response_model=ProgramOut, tags=["Programs"])
async def create_program(
    data: ProgramCreate,
    current_user=Depends(get_admin_user)
):
    """Créer un nouveau programme (admin only)"""
    program = await program_service.create_program(data)
    return program


@router.get("/", response_model=List[ProgramOut], tags=["Programs"])
async def list_programs(
    params: ProgramFilterParams = Depends(),
    current_user=Depends(get_optional_user)
):
    """Lister les programmes avec filtres"""
    programs = await program_service.list_programs(
        date=params.date,
        start_date=params.start_date,
        end_date=params.end_date,
        type=params.type,
        category=params.category,
        channel_id=params.channel_id,
        is_live=params.is_live,
        has_replay=params.has_replay,
        host=params.host,
        skip=params.skip,
        limit=params.limit
    )
    return programs


@router.get("/{program_id}", response_model=ProgramOut, tags=["Programs"])
async def get_program(
    program_id: str,
    current_user=Depends(get_optional_user)
):
    """Récupérer un programme par ID"""
    program = await program_service.get_program(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Programme non trouvé")
    return program


@router.patch("/{program_id}", response_model=ProgramOut, tags=["Programs"])
async def update_program(
    program_id: str,
    data: ProgramUpdate,
    current_user=Depends(get_admin_user)
):
    """Mettre à jour un programme (admin only)"""
    program = await program_service.update_program(program_id, data)
    if not program:
        raise HTTPException(status_code=404, detail="Programme non trouvé")
    return program


@router.delete("/{program_id}", tags=["Programs"])
async def delete_program(
    program_id: str,
    current_user=Depends(get_admin_user)
):
    """Supprimer un programme (admin only)"""
    deleted = await program_service.delete_program(program_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Programme non trouvé")
    return {"ok": True, "message": "Programme supprimé"}


@router.post("/{program_id}/live", response_model=ProgramOut, tags=["Programs"])
async def mark_program_live(
    program_id: str,
    is_live: bool = Query(True, description="Marquer comme en direct ou non"),
    current_user=Depends(get_admin_user)
):
    """Marquer/démarquer un programme comme étant en direct (admin only)"""
    program = await program_service.mark_program_live(program_id, is_live)
    if not program:
        raise HTTPException(status_code=404, detail="Programme non trouvé")
    return program


# ==================== PROGRAM GRID / WEEK ROUTES ====================

@router.get("/grid/weekly", response_model=ProgramWeekOut, tags=["Program Grid"])
async def get_program_week(
    weeks_ahead: int = Query(0, ge=0, le=4, description="Semaines à l'avance (0 = cette semaine)"),
    type: Optional[str] = Query(None, description="Filtrer par type"),
    current_user=Depends(get_optional_user)
):
    """
    Récupère la grille des programmes de la semaine, groupés par jour.
    Retourne aussi les types disponibles pour le filtrage.
    """
    result = await program_service.get_program_week(
        weeks_ahead=weeks_ahead,
        type=type
    )
    return result


@router.get("/grid/daily", response_model=ProgramGridOut, tags=["Program Grid"])
async def get_program_grid(
    start_date: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    type: Optional[str] = Query(None, description="Filtrer par type"),
    channel_id: Optional[str] = Query(None, description="Filtrer par chaîne"),
    current_user=Depends(get_optional_user)
):
    """
    Récupère la grille des programmes groupés par jour pour une période donnée.
    Par défaut: semaine courante (lundi à dimanche).
    """
    result = await program_service.get_program_grid(
        start_date=start_date,
        end_date=end_date,
        type=type,
        channel_id=channel_id
    )
    return result


@router.get("/live/current", response_model=List[ProgramOut], tags=["Programs"])
async def get_currently_live(
    current_user=Depends(get_optional_user)
):
    """Récupère les programmes actuellement en cours de diffusion"""
    programs = await program_service.get_currently_live()
    return programs


@router.get("/upcoming/list", response_model=List[ProgramOut], tags=["Programs"])
async def get_upcoming_programs(
    minutes_ahead: int = Query(60, ge=5, le=1440, description="Minutes à l'avance"),
    limit: int = Query(10, ge=1, le=50),
    current_user=Depends(get_optional_user)
):
    """Récupère les programmes à venir dans les X prochaines minutes"""
    programs = await program_service.get_upcoming_programs(
        minutes_ahead=minutes_ahead,
        limit=limit
    )
    return programs


# ==================== PROGRAM REMINDER ROUTES ====================

@router.post("/{program_id}/reminders", response_model=ProgramReminderOut, tags=["Reminders"])
async def create_reminder(
    program_id: str,
    data: ProgramReminderCreate,
    current_user=Depends(get_current_user)
):
    """Créer un rappel pour un programme"""
    try:
        # Override program_id from URL
        reminder_data = ProgramReminderCreate(
            program_id=program_id,
            minutes_before=data.minutes_before,
            reminder_type=data.reminder_type
        )
        
        reminder = await program_service.create_reminder(
            user_id=str(current_user.id),
            data=reminder_data
        )
        if not reminder:
            raise HTTPException(status_code=404, detail="Programme non trouvé")
        return reminder
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur création rappel: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.get("/reminders/my", response_model=List[ProgramReminderOut], tags=["Reminders"])
async def get_my_reminders(
    status: Optional[str] = Query(None, description="Filtrer par statut: scheduled, sent, cancelled"),
    upcoming_only: bool = Query(False, description="Uniquement les rappels à venir"),
    current_user=Depends(get_current_user)
):
    """Récupérer mes rappels de programmes"""
    reminders = await program_service.get_user_reminders(
        user_id=str(current_user.id),
        status=status,
        upcoming_only=upcoming_only
    )
    return reminders


@router.patch("/reminders/{reminder_id}", response_model=ProgramReminderOut, tags=["Reminders"])
async def update_reminder(
    reminder_id: str,
    data: ProgramReminderUpdate,
    current_user=Depends(get_current_user)
):
    """Mettre à jour un rappel"""
    reminder = await program_service.update_reminder(
        user_id=str(current_user.id),
        reminder_id=reminder_id,
        data=data
    )
    if not reminder:
        raise HTTPException(status_code=404, detail="Rappel non trouvé ou non autorisé")
    return reminder


@router.post("/reminders/{reminder_id}/cancel", tags=["Reminders"])
async def cancel_reminder(
    reminder_id: str,
    current_user=Depends(get_current_user)
):
    """Annuler un rappel (garde l'historique)"""
    cancelled = await program_service.cancel_reminder(
        user_id=str(current_user.id),
        reminder_id=reminder_id
    )
    if not cancelled:
        raise HTTPException(status_code=404, detail="Rappel non trouvé ou non autorisé")
    return {"ok": True, "message": "Rappel annulé"}


@router.delete("/reminders/{reminder_id}", tags=["Reminders"])
async def delete_reminder(
    reminder_id: str,
    current_user=Depends(get_current_user)
):
    """Supprimer définitivement un rappel"""
    deleted = await program_service.delete_reminder(
        user_id=str(current_user.id),
        reminder_id=reminder_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Rappel non trouvé ou non autorisé")
    return {"ok": True, "message": "Rappel supprimé"}
