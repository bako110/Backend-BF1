from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class Feedback(Document):
    """
    Retour d'expérience ("feedback") envoyé par un utilisateur depuis l'app.

    Distinct de SupportTicket (suivi de problème avec réponses) et de
    ContactMessage (formulaire de contact public) : c'est un avis court,
    éventuellement noté, que l'admin consulte et trie sans forcément répondre.
    """
    user_id: Optional[str] = Field(None, description="ID de l'auteur (null si anonyme)")
    username: Optional[str] = Field(None, description="Nom affiché de l'auteur au moment de l'envoi")
    email: Optional[str] = Field(None, description="E-mail de contact éventuel")
    message: str = Field(..., description="Contenu du retour")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Note de 1 à 5 (optionnelle)")
    category: str = Field("other", description="bug | idea | compliment | other")

    # Métadonnées client
    app_version: Optional[str] = Field(None, description="Version de l'app")
    platform: Optional[str] = Field(None, description="ios | android | web")
    device_info: Optional[str] = Field(None, description="Modèle / OS")

    # Suivi admin
    status: str = Field("new", description="new | reviewed | archived")
    is_read: bool = Field(False, description="Lu par un admin")
    admin_note: Optional[str] = Field(None, description="Note interne admin")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "feedbacks"
        indexes = [
            "status",
            "category",
            "is_read",
            "created_at",
            [("status", 1), ("created_at", -1)],
        ]
