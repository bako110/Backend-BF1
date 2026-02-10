"""
Modèle Beanie pour les sessions d'enregistrement
"""

from beanie import Document
from datetime import datetime
from typing import Optional
from pydantic import Field


class RecordingSession(Document):
    stream_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    status: str = Field(default="recording")  # recording, stopped, saved
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "recording_sessions"
        indexes = [
            "status",
            "created_at",
        ]
