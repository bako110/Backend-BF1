from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional, List
from bson import ObjectId


# ==================== LIVE CHANNEL SCHEMAS ====================

class LiveChannelBase(BaseModel):
    name: str = Field(..., description="Nom de la chaîne")
    description: Optional[str] = Field(None, description="Description")
    order: int = Field(default=0, description="Ordre d'affichage")
    is_active: bool = Field(default=True, description="Chaîne active")
    is_news_channel: bool = Field(default=False, description="Chaîne d'info continue")


class LiveChannelCreate(LiveChannelBase):
    logo_url: Optional[str] = Field(None, description="Logo de la chaîne")


class LiveChannelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None
    is_news_channel: Optional[bool] = None


class LiveChannelOut(LiveChannelBase):
    id: str = Field(..., alias="id")
    logo_url: Optional[HttpUrl] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        from_attributes = True


# ==================== PROGRAM SCHEMAS ====================

class ProgramBase(BaseModel):
    title: str = Field(..., description="Titre du programme")
    description: Optional[str] = Field(None, description="Description")
    type: str = Field(..., description="Type: Actualités, Sport, Culture, etc.")
    category: Optional[str] = Field(None, description="Catégorie secondaire")
    host: Optional[str] = Field(None, description="Présentateur")
    guests: List[str] = Field(default_factory=list, description="Invités")
    has_replay: bool = Field(default=False, description="Replay disponible")
    rating: Optional[str] = Field(None, description="Classification")


class ProgramCreate(ProgramBase):
    start_time: datetime = Field(..., description="Date/heure de début")
    end_time: datetime = Field(..., description="Date/heure de fin")
    image_url: Optional[str] = Field(None, description="Image")
    thumbnail_url: Optional[str] = Field(None, description="Miniature")
    channel_id: Optional[str] = Field(None, description="ID chaîne")
    show_id: Optional[str] = Field(None, description="ID émission liée")
    replay_url: Optional[str] = Field(None, description="URL replay")


class ProgramUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    type: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    host: Optional[str] = None
    guests: Optional[List[str]] = None
    is_live: Optional[bool] = None
    has_replay: Optional[bool] = None
    replay_url: Optional[str] = None
    channel_id: Optional[str] = None
    show_id: Optional[str] = None
    rating: Optional[str] = None


class ProgramOut(ProgramBase):
    id: str = Field(..., alias="id")
    start_time: datetime
    end_time: datetime
    image_url: Optional[HttpUrl] = None
    thumbnail_url: Optional[HttpUrl] = None
    is_live: bool
    replay_url: Optional[str] = None
    channel_id: Optional[str] = None
    show_id: Optional[str] = None
    duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True
        from_attributes = True


# ==================== PROGRAM GRID / GROUPED SCHEMAS ====================

class ProgramDayGroup(BaseModel):
    """Groupe de programmes pour un jour"""
    date: str = Field(..., description="Date format ISO (YYYY-MM-DD)")
    day_name: str = Field(..., description="Nom du jour (Lundi, Mardi...)")
    day_label: str = Field(..., description="Label complet (Lundi 15/01)")
    programs: List[ProgramOut] = Field(default_factory=list)


class ProgramGridOut(BaseModel):
    """Grille complète des programmes groupés par jour"""
    days: List[ProgramDayGroup] = Field(default_factory=list)
    total_programs: int = Field(default=0)
    date_range: dict = Field(default_factory=dict, description="{start, end}")


class ProgramWeekOut(BaseModel):
    """Programmes de la semaine"""
    days: List[ProgramDayGroup] = Field(default_factory=list)
    types_available: List[str] = Field(default_factory=list, description="Types présents")
    total_count: int = Field(default=0)


# ==================== PROGRAM REMINDER SCHEMAS ====================

class ProgramReminderBase(BaseModel):
    minutes_before: int = Field(default=15, ge=1, le=1440, description="Minutes avant")
    reminder_type: str = Field(default="push", description="push, inapp, email, sms")


class ProgramReminderCreate(ProgramReminderBase):
    program_id: str = Field(..., description="ID du programme")


class ProgramReminderUpdate(BaseModel):
    minutes_before: Optional[int] = None
    reminder_type: Optional[str] = None
    status: Optional[str] = None


class ProgramReminderOut(ProgramReminderBase):
    id: str = Field(..., alias="id")
    user_id: str
    program_id: str
    status: str
    scheduled_for: datetime
    sent_at: Optional[datetime] = None
    program_title: Optional[str] = None
    program_start_time: Optional[datetime] = None
    channel_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator('id', 'user_id', 'program_id', pre=True)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True
        from_attributes = True


# ==================== PROGRAM FILTER SCHEMAS ====================

class ProgramFilterParams(BaseModel):
    """Paramètres de filtrage pour les programmes"""
    date: Optional[str] = Field(None, description="Date spécifique (YYYY-MM-DD)")
    start_date: Optional[str] = Field(None, description="Date de début (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Date de fin (YYYY-MM-DD)")
    type: Optional[str] = Field(None, description="Filtrer par type")
    category: Optional[str] = Field(None, description="Filtrer par catégorie")
    channel_id: Optional[str] = Field(None, description="Filtrer par chaîne")
    is_live: Optional[bool] = Field(None, description="En direct uniquement")
    has_replay: Optional[bool] = Field(None, description="Avec replay uniquement")
    host: Optional[str] = Field(None, description="Filtrer par présentateur")
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)
