from beanie import Document
from pydantic import Field
from pymongo import IndexModel
from datetime import datetime
from typing import Optional

# Rétention des messages du chat live : 90 jours (purge automatique via index TTL Mongo)
LIVE_CHAT_TTL_SECONDS = 90 * 24 * 3600


class LiveChatMessage(Document):
    """
    Message du chat en direct du live BF1.

    Persisté en base (contrairement à l'ancien stockage RAM), ce qui permet :
    - de recharger l'historique après un redémarrage serveur,
    - d'afficher une vraie fenêtre glissante (les ~20 dernières minutes) à l'arrivée,
    - de paginer vers le passé ("charger les messages plus anciens").

    Purge automatique après 90 jours grâce à l'index TTL sur `created_at`.
    """
    user_id: Optional[str] = Field(None, description="ID de l'auteur (null si anonyme)")
    username: str = Field("Anonyme", description="Nom affiché de l'auteur")
    avatar_url: Optional[str] = Field(None, description="Avatar de l'auteur")
    text: str = Field(..., description="Contenu du message")
    is_hidden: bool = Field(False, description="Masqué par la modération")
    edited: bool = Field(False, description="Message modifié par son auteur")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "live_chat_messages"
        indexes = [
            # Un seul index sur created_at : il sert à la fois
            #  - aux requêtes par plage (fenêtre 20 min) et au tri/pagination,
            #  - à la purge automatique après LIVE_CHAT_TTL_SECONDS (90 j).
            IndexModel(
                [("created_at", 1)],
                name="live_chat_created_at_ttl",
                expireAfterSeconds=LIVE_CHAT_TTL_SECONDS,
            ),
        ]
