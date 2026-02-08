from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import datetime

class UserSettingsBase(BaseModel):
    # Notifications
    push_notifications: bool = True
    email_notifications: bool = True
    live_notifications: bool = True
    news_notifications: bool = True
    
    # Préférences de lecture
    auto_play: bool = True
    video_quality: str = "auto"
    subtitles_enabled: bool = False
    
    # Confidentialité
    profile_visibility: str = "public"
    show_watch_history: bool = True
    
    # Langue et région
    language: str = "fr"
    region: str = "BF"
    
    # Thème
    theme: str = "dark"


class UserSettingsCreate(UserSettingsBase):
    pass


class UserSettingsUpdate(BaseModel):
    push_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    live_notifications: Optional[bool] = None
    news_notifications: Optional[bool] = None
    auto_play: Optional[bool] = None
    video_quality: Optional[str] = None
    subtitles_enabled: Optional[bool] = None
    profile_visibility: Optional[str] = None
    show_watch_history: Optional[bool] = None
    language: Optional[str] = None
    region: Optional[str] = None
    theme: Optional[str] = None


class UserSettingsOut(UserSettingsBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('id', 'user_id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        """Convertit ObjectId en string"""
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        populate_by_name = True
