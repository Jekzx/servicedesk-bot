"""RESTful CRUD and Management router for Service Desk Tickets."""
import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.core.database import get_db
from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus
from app.models.log import MessageLog
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketUpdateStatus,
    TicketResponse,
    TicketListResponse,
)
from app.services.whatsapp import whatsapp_service

router = APIRouter(prefix="/api/tickets", tags=["Service Desk Tickets"])


@router.get("", response_model=TicketListResponse, summary="List Tickets with Filters and Pagination")
def list_tickets(
    status: Optional[TicketStatus] = Query(None, description="Filtrar por status do chamado"),
    priority: Optional[TicketPriority] = Query(None, description="Filtrar por prioridade"),
    category: Optional[TicketCategory] = Query(None, description="Filtrar por categoria"),
    requester_phone: Optional[str] = Query(None, description="Filtrar por telefone"),
    search: Optional[str] = Query(None, description="Busca textual em título, descrição, protocolo e nome"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db)
):
    """Retrieve list of tickets with rich filtering, search and pagination."""
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if requester_phone:
        query = query.filter(Ticket.requester_phone.ilike(f"%{requester_phone}%"))
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Ticket.protocol.ilike(search_pattern),
                Ticket.title.ilike(search_pattern),
                Ticket.description.ilike(search_pattern),
                Ticket.requester_name.ilike(search_pattern),
            )
        )

    total = query.count()
    items = query.order_by(desc(Ticket.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return TicketListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{ticket_id}", response_model=TicketResponse, summary="Get Ticket Details and Conversation History")
def get_ticket_by_id(
    ticket_id: str = Path(..., description="UUID ou Protocolo do chamado"),
    db: Session = Depends(get_db)
):
    """Get single ticket with full message history."""
    ticket = db.query(Ticket).filter(
        or_(Ticket.id == ticket_id, Ticket.protocol == ticket_id)
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' não encontrado."
        )

    return ticket


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED, summary="Create Ticket Manually")
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db)
):
    """Create a ticket manually from internal panel."""
    from app.services.triage_engine import triage_engine
    protocol = triage_engine.generate_protocol()

    ticket = Ticket(
        protocol=protocol,
        requester_phone=payload.requester_phone,
        requester_name=payload.requester_name or "Colaborador",
        title=payload.title,
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
        status=payload.status,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse, summary="Update Ticket Status and Notify WhatsApp")
async def update_ticket_status(
    ticket_id: str = Path(..., description="ID ou Protocolo do chamado"),
    payload: TicketUpdateStatus = ...,
    db: Session = Depends(get_db)
):
    """
    Update ticket status and resolution notes.
    Automatically sends an update notification to the requester's WhatsApp.
    """
    ticket = db.query(Ticket).filter(
        or_(Ticket.id == ticket_id, Ticket.protocol == ticket_id)
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' não encontrado."
        )

    old_status = ticket.status
    ticket.status = payload.status
    if payload.resolution_notes:
        ticket.resolution_notes = payload.resolution_notes
    ticket.updated_at = datetime.datetime.utcnow()

    # Log status change in MessageLog
    status_msg = f"Status alterado de '{old_status.value}' para '{payload.status.value}'."
    if payload.resolution_notes:
        status_msg += f" Resolução: {payload.resolution_notes}"

    log_entry = MessageLog(
        ticket_id=ticket.id,
        sender_phone="SERVICE_DESK_SYSTEM",
        sender_name="Painel Service Desk",
        direction="OUTBOUND",
        message_type="status_change",
        content=status_msg,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(ticket)

    # WhatsApp Notification to requester
    if payload.notify_requester and ticket.requester_phone:
        notification_text = whatsapp_service.template_status_updated(
            protocol=ticket.protocol,
            new_status=ticket.status.value,
            notes=payload.resolution_notes
        )
        await whatsapp_service.send_whatsapp_message(
            recipient_phone=ticket.requester_phone,
            message_text=notification_text
        )

    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Ticket")
def delete_ticket(
    ticket_id: str = Path(..., description="ID ou Protocolo do chamado"),
    db: Session = Depends(get_db)
):
    """Delete a ticket and associated message logs."""
    ticket = db.query(Ticket).filter(
        or_(Ticket.id == ticket_id, Ticket.protocol == ticket_id)
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' não encontrado."
        )

    db.delete(ticket)
    db.commit()
    return None
