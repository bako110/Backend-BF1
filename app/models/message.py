from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Message(Document):
    sender_id: str = Field(..., description="ID de l'expéditeur")
    receiver_id: str = Field(..., description="ID du destinataire")
    subject: str = Field(..., description="Sujet du message")
    content: str = Field(..., description="Contenu du message")
    is_read: bool = Field(False, description="Message lu ou non")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = Field(None, description="Date de lecture")

    class Settings:
        name = "messages"
        indexes = [
            "sender_id",
            "receiver_id",
            "is_read",
            "created_at"
        ]
