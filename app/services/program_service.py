"""Service layer for Programs, Live Channels and Reminders"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from beanie.operators import GTE, LTE, And, Eq, In
from app.models.program import Program, LiveChannel, ProgramReminder
from app.schemas.program import (
    ProgramCreate, ProgramUpdate, ProgramOut, ProgramDayGroup,
    ProgramWeekOut, ProgramGridOut, LiveChannelCreate, LiveChannelUpdate,
    ProgramReminderCreate, ProgramReminderUpdate
)


# ==================== LIVE CHANNEL SERVICES ====================

async def create_channel(data: LiveChannelCreate) -> LiveChannel:
    channel = LiveChannel(**data.model_dump())
    await channel.insert()
    return channel


async def get_channel(channel_id: str) -> Optional[LiveChannel]:
    return await LiveChannel.get(channel_id)


async def list_channels(
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50
) -> List[LiveChannel]:
    query = LiveChannel.find()
    if is_active is not None:
        query = query.find(Eq(LiveChannel.is_active, is_active))
    return await query.sort(+LiveChannel.order).skip(skip).limit(limit).to_list()


async def update_channel(
    channel_id: str,
    data: LiveChannelUpdate
) -> Optional[LiveChannel]:
    channel = await LiveChannel.get(channel_id)
    if not channel:
        return None
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await channel.update({"$set": update_data})
    return channel


async def delete_channel(channel_id: str) -> bool:
    channel = await LiveChannel.get(channel_id)
    if not channel:
        return False
    await channel.delete()
    return True


# ==================== PROGRAM SERVICES ====================

async def create_program(data: ProgramCreate) -> Program:
    # Calculer la durée si pas fournie
    duration = data.duration_minutes
    if not duration and data.start_time and data.end_time:
        delta = data.end_time - data.start_time
        duration = int(delta.total_seconds() / 60)
    
    program = Program(
        **data.model_dump(exclude={"duration_minutes"}),
        duration_minutes=duration
    )
    await program.insert()
    return program


async def get_program(program_id: str) -> Optional[Program]:
    return await Program.get(program_id)


async def list_programs(
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
    channel_id: Optional[str] = None,
    is_live: Optional[bool] = None,
    has_replay: Optional[bool] = None,
    host: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Program]:
    query = Program.find()
    
    # Filtre par date spécifique
    if date:
        start_dt = datetime.fromisoformat(date)
        end_dt = start_dt + timedelta(days=1)
        query = query.find(And(
            GTE(Program.start_time, start_dt),
            LTE(Program.start_time, end_dt)
        ))
    
    # Filtre par plage de dates
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.find(GTE(Program.start_time, start_dt))
    
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.find(LTE(Program.start_time, end_dt))
    
    # Autres filtres
    if type:
        query = query.find(Eq(Program.type, type))
    if category:
        query = query.find(Eq(Program.category, category))
    if channel_id:
        query = query.find(Eq(Program.channel_id, channel_id))
    if is_live is not None:
        query = query.find(Eq(Program.is_live, is_live))
    if has_replay is not None:
        query = query.find(Eq(Program.has_replay, has_replay))
    if host:
        query = query.find(Eq(Program.host, host))
    
    return await query.sort(+Program.start_time).skip(skip).limit(limit).to_list()


async def update_program(
    program_id: str,
    data: ProgramUpdate
) -> Optional[Program]:
    program = await Program.get(program_id)
    if not program:
        return None
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    # Recalculer la durée si horaires modifiés
    if "start_time" in update_data or "end_time" in update_data:
        start = update_data.get("start_time", program.start_time)
        end = update_data.get("end_time", program.end_time)
        if start and end:
            update_data["duration_minutes"] = int((end - start).total_seconds() / 60)
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await program.update({"$set": update_data})
    return program


async def delete_program(program_id: str) -> bool:
    program = await Program.get(program_id)
    if not program:
        return False
    await program.delete()
    return True


async def mark_program_live(program_id: str, is_live: bool = True) -> Optional[Program]:
    """Marquer/démarquer un programme comme étant en direct"""
    program = await Program.get(program_id)
    if not program:
        return None
    await program.update({"$set": {"is_live": is_live, "updated_at": datetime.utcnow()}})
    program.is_live = is_live
    return program


# ==================== PROGRAM GRID / GROUPED ====================

def _group_programs_by_day(programs: List[Program]) -> List[ProgramDayGroup]:
    """Groupe les programmes par jour pour l'affichage grille"""
    days_map: Dict[str, Dict[str, Any]] = {}
    days_order = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    for program in programs:
        start_dt = program.start_time
        date_key = start_dt.strftime('%Y-%m-%d')
        day_name = days_order[start_dt.weekday()]  # weekday() 0=Lundi
        day_label = f"{day_name} {start_dt.day:02d}/{start_dt.month:02d}"
        
        if date_key not in days_map:
            days_map[date_key] = {
                "date": date_key,
                "day_name": day_name,
                "day_label": day_label,
                "programs": [],
                "sort_key": start_dt.toordinal()  # Pour trier par date
            }
        
        # Convertir le programme en dict avec l'ID en string
        program_dict = program.dict()
        if program.id:
            program_dict['id'] = str(program.id)
        
        days_map[date_key]["programs"].append(program_dict)
    
    # Trier par date et créer les objets
    sorted_days = sorted(days_map.values(), key=lambda x: x["sort_key"])
    
    # Convertir chaque programme en dict pour le schéma
    result = []
    for day_data in sorted_days:
        result.append(ProgramDayGroup(
            date=day_data["date"],
            day_name=day_data["day_name"],
            day_label=day_data["day_label"],
            programs=day_data["programs"]
        ))
    
    return result


async def get_program_grid(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    type: Optional[str] = None,
    channel_id: Optional[str] = None
) -> ProgramGridOut:
    """Récupère la grille des programmes groupés par jour"""
    
    # Par défaut: semaine courante
    if not start_date:
        today = datetime.now()
        # Lundi de cette semaine
        start_dt = today - timedelta(days=today.weekday())
        start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start_dt = datetime.fromisoformat(start_date)
    
    if not end_date:
        # Dimanche de cette semaine (6 jours après lundi)
        end_dt = start_dt + timedelta(days=7)
    else:
        end_dt = datetime.fromisoformat(end_date)
    
    # Récupérer les programmes
    query = Program.find(
        And(
            GTE(Program.start_time, start_dt),
            LTE(Program.start_time, end_dt)
        )
    )
    
    if type:
        query = query.find(Eq(Program.type, type))
    if channel_id:
        query = query.find(Eq(Program.channel_id, channel_id))
    
    programs = await query.sort(+Program.start_time).to_list()
    
    # Grouper par jour
    days = _group_programs_by_day(programs)
    
    return ProgramGridOut(
        days=days,
        total_programs=len(programs),
        date_range={
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat()
        }
    )


async def get_program_week(
    weeks_ahead: int = 0,
    type: Optional[str] = None
) -> ProgramWeekOut:
    """Récupère les programmes de la semaine (7 jours)"""
    
    today = datetime.now()
    # Ajouter des semaines si demandé
    start_dt = today + timedelta(weeks=weeks_ahead)
    
    # Lundi de la semaine cible
    start_dt = start_dt - timedelta(days=start_dt.weekday())
    start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 7 jours après
    end_dt = start_dt + timedelta(days=7)
    
    # Récupérer tous les programmes
    query = Program.find(
        And(
            GTE(Program.start_time, start_dt),
            LTE(Program.start_time, end_dt)
        )
    )
    
    if type:
        query = query.find(Eq(Program.type, type))
    
    programs = await query.sort(+Program.start_time).to_list()
    
    # Grouper par jour
    days = _group_programs_by_day(programs)
    
    # Extraire les types disponibles
    types_available = list(set(p.type for p in programs if p.type))
    
    return ProgramWeekOut(
        days=days,
        types_available=types_available,
        total_count=len(programs)
    )


async def get_currently_live() -> List[Program]:
    """Récupère les programmes en cours de diffusion"""
    now = datetime.utcnow()
    return await Program.find(
        And(
            LTE(Program.start_time, now),
            GTE(Program.end_time, now)
        )
    ).sort(+Program.start_time).to_list()


async def get_upcoming_programs(
    minutes_ahead: int = 60,
    limit: int = 10
) -> List[Program]:
    """Récupère les programmes à venir dans les X minutes"""
    now = datetime.utcnow()
    future = now + timedelta(minutes=minutes_ahead)
    
    return await Program.find(
        And(
            GTE(Program.start_time, now),
            LTE(Program.start_time, future)
        )
    ).sort(+Program.start_time).limit(limit).to_list()


# ==================== PROGRAM REMINDER SERVICES ====================

async def create_reminder(
    user_id: str,
    data: ProgramReminderCreate
) -> Optional[ProgramReminder]:
    """Créer un rappel pour un programme"""
    
    # Vérifier que le programme existe
    program = await Program.get(data.program_id)
    if not program:
        return None
    
    # Vérifier si un rappel existe déjà
    existing = await ProgramReminder.find_one(
        And(
            Eq(ProgramReminder.user_id, user_id),
            Eq(ProgramReminder.program_id, data.program_id),
            Eq(ProgramReminder.status, "scheduled")
        )
    )
    if existing:
        return existing  # Rappel déjà programmé
    
    # Calculer l'heure d'envoi du rappel
    reminder_time = program.start_time - timedelta(minutes=data.minutes_before)
    
    # Récupérer le nom de la chaîne si disponible
    channel_name = None
    if program.channel_id:
        channel = await LiveChannel.get(program.channel_id)
        if channel:
            channel_name = channel.name
    
    reminder = ProgramReminder(
        user_id=user_id,
        program_id=data.program_id,
        minutes_before=data.minutes_before,
        reminder_type=data.reminder_type,
        scheduled_for=reminder_time,
        program_title=program.title,
        program_start_time=program.start_time,
        channel_name=channel_name
    )
    await reminder.insert()
    return reminder


async def get_user_reminders(
    user_id: str,
    status: Optional[str] = None,
    upcoming_only: bool = False
) -> List[ProgramReminder]:
    """Récupère les rappels d'un utilisateur"""
    
    query = ProgramReminder.find(Eq(ProgramReminder.user_id, user_id))
    
    if status:
        query = query.find(Eq(ProgramReminder.status, status))
    
    if upcoming_only:
        now = datetime.utcnow()
        query = query.find(GTE(ProgramReminder.scheduled_for, now))
    
    return await query.sort(+ProgramReminder.scheduled_for).to_list()


async def cancel_reminder(
    user_id: str,
    reminder_id: str
) -> bool:
    """Annuler un rappel"""
    reminder = await ProgramReminder.get(reminder_id)
    if not reminder or reminder.user_id != user_id:
        return False
    
    await reminder.update({
        "$set": {
            "status": "cancelled",
            "updated_at": datetime.utcnow()
        }
    })
    return True


async def delete_reminder(
    user_id: str,
    reminder_id: str
) -> bool:
    """Supprimer définitivement un rappel"""
    reminder = await ProgramReminder.get(reminder_id)
    if not reminder or reminder.user_id != user_id:
        return False
    
    await reminder.delete()
    return True


async def update_reminder(
    user_id: str,
    reminder_id: str,
    data: ProgramReminderUpdate
) -> Optional[ProgramReminder]:
    """Mettre à jour un rappel"""
    reminder = await ProgramReminder.get(reminder_id)
    if not reminder or reminder.user_id != user_id:
        return None
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    # Si minutes_before modifié, recalculer scheduled_for
    if "minutes_before" in update_data:
        program = await Program.get(reminder.program_id)
        if program:
            update_data["scheduled_for"] = program.start_time - timedelta(
                minutes=update_data["minutes_before"]
            )
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await reminder.update({"$set": update_data})
    
    return reminder


async def get_pending_reminders_to_send() -> List[ProgramReminder]:
    """Récupère les rappels prêts à être envoyés (pour le job)"""
    now = datetime.utcnow()
    return await ProgramReminder.find(
        And(
            Eq(ProgramReminder.status, "scheduled"),
            LTE(ProgramReminder.scheduled_for, now)
        )
    ).sort(+ProgramReminder.scheduled_for).to_list()


async def mark_reminder_sent(reminder_id: str) -> bool:
    """Marquer un rappel comme envoyé"""
    reminder = await ProgramReminder.get(reminder_id)
    if not reminder:
        return False
    
    await reminder.update({
        "$set": {
            "status": "sent",
            "sent_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    })
    return True
