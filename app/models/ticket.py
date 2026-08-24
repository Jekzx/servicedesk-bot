"""Ticket model and Enums for Service Desk."""
import enum
from sqlalchemy import Column, String, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class TicketCategory(str, enum.Enum):
    NETWORK = "NETWORK"                 # VPN, Wi-Fi, Conexão, DNS
    AUTH = "AUTH"                       # Active Directory, Senha, Login, Bloqueio
    DATABASE = "DATABASE"               # Banco de dados, queries, timeouts
    HARDWARE = "HARDWARE"               # Monitor, Teclado, Impressora, Notebook
    ERP_CRM = "ERP_CRM"                 # CRM, SAP, Totvs, Portal interno
    OTHER = "OTHER"                     # Outros chamados gerais


class TicketPriority(str, enum.Enum):
    P1 = "P1"  # Crítico: Sistema fora do ar, impacto em massa
    P2 = "P2"  # Alto: Bloqueio de operação de usuário chave ou departamento
    P3 = "P3"  # Médio: Degradação ou problema com contorno
    P4 = "P4"  # Baixo: Dúvida, solicitação simples, melhoria


class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"                       # Aberto aguardando análise
    IN_PROGRESS = "IN_PROGRESS"         # Em atendimento pelo time N2/N3
    RESOLVED_AUTO = "RESOLVED_AUTO"     # Auto-resolvido pelo Bot N1
    RESOLVED = "RESOLVED"               # Resolvido por analista
    ESCALATED_N2 = "ESCALATED_N2"       # Escalado para suporte avançado N2/N3


class Ticket(Base, TimestampMixin):
    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    protocol = Column(String(30), unique=True, index=True, nullable=False)
    requester_phone = Column(String(30), index=True, nullable=False)
    requester_name = Column(String(100), default="Colaborador", nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    category = Column(
        Enum(TicketCategory, name="ticket_category_enum", native_enum=False),
        default=TicketCategory.OTHER,
        nullable=False,
        index=True
    )
    priority = Column(
        Enum(TicketPriority, name="ticket_priority_enum", native_enum=False),
        default=TicketPriority.P3,
        nullable=False,
        index=True
    )
    status = Column(
        Enum(TicketStatus, name="ticket_status_enum", native_enum=False),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True
    )

    auto_remediated = Column(Boolean, default=False, nullable=False)
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    messages = relationship("MessageLog", back_populates="ticket", cascade="all, delete-orphan", order_by="MessageLog.timestamp")

    def __repr__(self) -> str:
        return f"<Ticket {self.protocol} [{self.category}] - {self.priority} - {self.status}>"
