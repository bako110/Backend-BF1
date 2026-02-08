from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.models.support import SupportTicket, FAQ
from app.schemas.support import (
    SupportTicketCreate, SupportTicketUpdate, SupportTicketOut,
    FAQCreate, FAQUpdate, FAQOut, SupportTicketResponse
)
from app.utils.auth import get_current_user, get_admin_user
from app.models.user import User

router = APIRouter()


# ==================== Support Tickets ====================

@router.post("/tickets", response_model=SupportTicketOut, status_code=status.HTTP_201_CREATED)
async def create_support_ticket(
    ticket: SupportTicketCreate,
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau ticket de support"""
    new_ticket = SupportTicket(
        user_id=str(current_user.id),
        **ticket.dict()
    )
    await new_ticket.insert()
    return new_ticket


@router.get("/tickets/my", response_model=List[SupportTicketOut])
async def get_my_tickets(
    status_filter: Optional[str] = Query(None, description="Filtrer par statut"),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les tickets de support de l'utilisateur connecté"""
    query = SupportTicket.find(SupportTicket.user_id == str(current_user.id))
    
    if status_filter:
        query = query.find(SupportTicket.status == status_filter)
    
    tickets = await query.sort(-SupportTicket.created_at).to_list()
    return tickets


@router.get("/tickets/{ticket_id}", response_model=SupportTicketOut)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user)
):
    """Récupérer un ticket de support spécifique"""
    ticket = await SupportTicket.get(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")
    
    # Vérifier que l'utilisateur est le propriétaire du ticket
    if ticket.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return ticket


@router.post("/tickets/{ticket_id}/responses", response_model=SupportTicketOut)
async def add_ticket_response(
    ticket_id: str,
    response: SupportTicketResponse,
    current_user: User = Depends(get_current_user)
):
    """Ajouter une réponse à un ticket de support"""
    ticket = await SupportTicket.get(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")
    
    # Vérifier que l'utilisateur est le propriétaire du ticket ou admin
    if ticket.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Ajouter la réponse
    response_data = {
        "message": response.message,
        "author": "admin" if current_user.is_admin else "user",
        "author_name": current_user.username,
        "created_at": datetime.utcnow().isoformat()
    }
    
    ticket.responses.append(response_data)
    ticket.updated_at = datetime.utcnow()
    
    # Si admin répond, passer en "in_progress"
    if current_user.is_admin and ticket.status == "open":
        ticket.status = "in_progress"
    
    await ticket.save()
    return ticket


@router.put("/tickets/{ticket_id}", response_model=SupportTicketOut)
async def update_ticket(
    ticket_id: str,
    ticket_update: SupportTicketUpdate,
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un ticket de support"""
    ticket = await SupportTicket.get(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")
    
    # Vérifier que l'utilisateur est le propriétaire du ticket ou admin
    if ticket.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Mettre à jour les champs fournis
    update_data = ticket_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
    
    ticket.updated_at = datetime.utcnow()
    
    # Si le statut passe à "resolved", enregistrer la date
    if ticket.status == "resolved" and not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()
    
    await ticket.save()
    return ticket


@router.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user)
):
    """Supprimer un ticket de support"""
    ticket = await SupportTicket.get(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")
    
    # Vérifier que l'utilisateur est le propriétaire du ticket ou admin
    if ticket.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    await ticket.delete()


# ==================== FAQs ====================

@router.get("/faqs", response_model=List[FAQOut])
async def get_faqs(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    limit: int = Query(50, ge=1, le=100)
):
    """Récupérer les FAQs"""
    query = FAQ.find(FAQ.is_active == True)
    
    if category:
        query = query.find(FAQ.category == category)
    
    faqs = await query.sort(FAQ.order).limit(limit).to_list()
    return faqs


@router.get("/faqs/{faq_id}", response_model=FAQOut)
async def get_faq(faq_id: str):
    """Récupérer une FAQ spécifique"""
    faq = await FAQ.get(faq_id)
    
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ non trouvée")
    
    # Incrémenter le compteur de vues
    faq.views += 1
    await faq.save()
    
    return faq


@router.post("/faqs/{faq_id}/helpful", response_model=FAQOut)
async def mark_faq_helpful(faq_id: str):
    """Marquer une FAQ comme utile"""
    faq = await FAQ.get(faq_id)
    
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ non trouvée")
    
    faq.helpful_count += 1
    await faq.save()
    
    return faq


# ==================== Admin Endpoints ====================

@router.post("/faqs", response_model=FAQOut, status_code=status.HTTP_201_CREATED)
async def create_faq(
    faq: FAQCreate,
    current_user: User = Depends(get_admin_user)
):
    """Créer une nouvelle FAQ (Admin uniquement)"""
    new_faq = FAQ(**faq.dict())
    await new_faq.insert()
    return new_faq


@router.put("/faqs/{faq_id}", response_model=FAQOut)
async def update_faq(
    faq_id: str,
    faq_update: FAQUpdate,
    current_user: User = Depends(get_admin_user)
):
    """Mettre à jour une FAQ (Admin uniquement)"""
    faq = await FAQ.get(faq_id)
    
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ non trouvée")
    
    update_data = faq_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faq, field, value)
    
    faq.updated_at = datetime.utcnow()
    await faq.save()
    
    return faq


@router.delete("/faqs/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: str,
    current_user: User = Depends(get_admin_user)
):
    """Supprimer une FAQ (Admin uniquement)"""
    faq = await FAQ.get(faq_id)
    
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ non trouvée")
    
    await faq.delete()
