from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class SupportTicket(Document):
    """Ticket de support pour l'aide utilisateur"""
    user_id: str = Field(..., description="ID de l'utilisateur")
    subject: str = Field(..., description="Sujet du ticket")
    message: str = Field(..., description="Message/Description du problème")
    category: str = Field(..., description="Catégorie: bug, feature, question, other")
    priority: str = Field("normal", description="Priorité: low, normal, high, urgent")
    status: str = Field("open", description="Statut: open, in_progress, resolved, closed")
    
    # Réponses
    responses: List[dict] = Field(default_factory=list, description="Réponses au ticket")
    
    # Métadonnées
    device_info: Optional[str] = Field(None, description="Informations sur l'appareil")
    app_version: Optional[str] = Field(None, description="Version de l'application")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    class Settings:
        name = "support_tickets"
        indexes = [
            "user_id",
            "status",
            "category",
            "created_at",
            [("user_id", 1), ("status", 1), ("created_at", -1)]
        ]


class FAQ(Document):
    """Questions fréquemment posées"""
    question: str = Field(..., description="Question")
    answer: str = Field(..., description="Réponse")
    category: str = Field(..., description="Catégorie de la FAQ")
    order: int = Field(0, description="Ordre d'affichage")
    is_active: bool = Field(True, description="FAQ active")
    views: int = Field(0, description="Nombre de vues")
    helpful_count: int = Field(0, description="Nombre de 'utile'")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "faqs"
        indexes = [
            "category",
            "is_active",
            "order",
        ]
