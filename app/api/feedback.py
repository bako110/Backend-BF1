from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackOut
from app.utils.auth import get_optional_user, get_admin_user
from app.models.user import User

router = APIRouter()


# ── Utilisateur : envoyer un retour ─────────────────────────────────────────

@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    payload: FeedbackCreate,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Envoyer un retour d'expérience (auth optionnelle : accepte les anonymes)."""
    fb = Feedback(
        user_id=str(current_user.id) if current_user else None,
        username=getattr(current_user, "username", None) if current_user else None,
        email=payload.email or (getattr(current_user, "email", None) if current_user else None),
        message=payload.message.strip(),
        rating=payload.rating,
        category=payload.category,
        app_version=payload.app_version,
        platform=payload.platform,
        device_info=payload.device_info,
    )
    await fb.insert()
    return fb


# ── Admin : consultation & tri ─────────────────────────────────────────────

@router.get("", response_model=List[FeedbackOut])
async def list_feedbacks(
    status_filter: Optional[str] = Query(None, alias="status", description="new | reviewed | archived"),
    category: Optional[str] = Query(None, description="bug | idea | compliment | other"),
    unread_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    _admin: User = Depends(get_admin_user),
):
    """Lister les retours (admin uniquement)."""
    query = Feedback.find_all()
    if status_filter:
        query = query.find(Feedback.status == status_filter)
    if category:
        query = query.find(Feedback.category == category)
    if unread_only:
        query = query.find(Feedback.is_read == False)  # noqa: E712
    return await query.sort(-Feedback.created_at).skip(skip).limit(limit).to_list()


@router.get("/stats")
async def feedback_stats(_admin: User = Depends(get_admin_user)):
    """Compteurs pour le tableau de bord admin."""
    total = await Feedback.find_all().count()
    unread = await Feedback.find(Feedback.is_read == False).count()  # noqa: E712
    by_status = {}
    for st in ("new", "reviewed", "archived"):
        by_status[st] = await Feedback.find(Feedback.status == st).count()
    by_category = {}
    for cat in ("bug", "idea", "compliment", "other"):
        by_category[cat] = await Feedback.find(Feedback.category == cat).count()

    # Moyenne des notes renseignées
    rated = await Feedback.find(Feedback.rating != None).to_list()  # noqa: E711
    avg_rating = round(sum(f.rating for f in rated) / len(rated), 2) if rated else None

    return {
        "total": total,
        "unread": unread,
        "by_status": by_status,
        "by_category": by_category,
        "avg_rating": avg_rating,
        "rated_count": len(rated),
    }


@router.get("/{feedback_id}", response_model=FeedbackOut)
async def get_feedback(feedback_id: str, _admin: User = Depends(get_admin_user)):
    fb = await Feedback.get(feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Retour introuvable")
    return fb


@router.patch("/{feedback_id}", response_model=FeedbackOut)
async def update_feedback(
    feedback_id: str,
    payload: FeedbackUpdate,
    _admin: User = Depends(get_admin_user),
):
    """Marquer lu / changer le statut / ajouter une note interne (admin)."""
    fb = await Feedback.get(feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Retour introuvable")

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(fb, field, value)
    fb.updated_at = datetime.utcnow()
    await fb.save()
    return fb


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(feedback_id: str, _admin: User = Depends(get_admin_user)):
    fb = await Feedback.get(feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Retour introuvable")
    await fb.delete()
