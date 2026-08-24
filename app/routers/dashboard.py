"""Dashboard analytics and Service Desk metrics router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus
from app.schemas.ticket import TicketStatsResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard & Analytics"])


@router.get("/stats", response_model=TicketStatsResponse, summary="Get Service Desk SLA and Ticket Metrics")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Computes real-time statistics, SLA compliance and category distributions."""
    total = db.query(Ticket).count()
    open_count = db.query(Ticket).filter(Ticket.status == TicketStatus.OPEN).count()
    in_prog_count = db.query(Ticket).filter(Ticket.status == TicketStatus.IN_PROGRESS).count()
    auto_resolved = db.query(Ticket).filter(Ticket.status == TicketStatus.RESOLVED_AUTO).count()
    manual_resolved = db.query(Ticket).filter(Ticket.status == TicketStatus.RESOLVED).count()
    escalated = db.query(Ticket).filter(Ticket.status == TicketStatus.ESCALATED_N2).count()
    p1_critical = db.query(Ticket).filter(Ticket.priority == TicketPriority.P1).count()

    auto_rate = round((auto_resolved / total * 100.0), 1) if total > 0 else 0.0

    # Category counts
    by_category = {}
    for cat in TicketCategory:
        c_count = db.query(Ticket).filter(Ticket.category == cat).count()
        by_category[cat.value] = c_count

    # Priority counts
    by_priority = {}
    for prio in TicketPriority:
        p_count = db.query(Ticket).filter(Ticket.priority == prio).count()
        by_priority[prio.value] = p_count

    return TicketStatsResponse(
        total_tickets=total,
        open_tickets=open_count,
        in_progress_tickets=in_prog_count,
        resolved_auto_tickets=auto_resolved,
        resolved_manual_tickets=manual_resolved,
        escalated_n2_tickets=escalated,
        critical_p1_tickets=p1_critical,
        auto_remediation_rate=auto_rate,
        by_category=by_category,
        by_priority=by_priority,
    )
