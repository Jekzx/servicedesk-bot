"""Pydantic schemas for Service Desk Tickets and Logs."""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict
from app.models.ticket import TicketCategory, TicketPriority, TicketStatus


class MessageLogBase(BaseModel):
    sender_phone: str
    sender_name: Optional[str] = "User"
    direction: str = "INBOUND"
    message_type: str = "text"
    content: Optional[str] = None
    media_url: Optional[str] = None
    timestamp: datetime


class MessageLogResponse(MessageLogBase):
    id: str
    ticket_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TicketBase(BaseModel):
    requester_phone: str
    requester_name: Optional[str] = "Colaborador"
    title: str
    description: str
    category: TicketCategory = TicketCategory.OTHER
    priority: TicketPriority = TicketPriority.P3
    status: TicketStatus = TicketStatus.OPEN


class TicketCreate(TicketBase):
    pass


class TicketUpdateStatus(BaseModel):
    status: TicketStatus
    resolution_notes: Optional[str] = None
    notify_requester: bool = True


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    resolution_notes: Optional[str] = None


class TicketResponse(TicketBase):
    id: str
    protocol: str
    auto_remediated: bool
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageLogResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class TicketListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TicketResponse]


class TicketStatsResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_auto_tickets: int
    resolved_manual_tickets: int
    escalated_n2_tickets: int
    critical_p1_tickets: int
    auto_remediation_rate: float
    by_category: Dict[str, int]
    by_priority: Dict[str, int]
