"""MessageLog model for tracking WhatsApp conversations and raw webhook payloads."""
import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import generate_uuid


class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True, index=True)
    sender_phone = Column(String(30), nullable=False, index=True)
    sender_name = Column(String(100), default="User", nullable=True)
    direction = Column(String(10), default="INBOUND", nullable=False)  # INBOUND or OUTBOUND
    message_type = Column(String(20), default="text", nullable=False)  # text, image, audio, document, interactive
    content = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    payload_raw = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    # Relationship
    ticket = relationship("Ticket", back_populates="messages")

    def __repr__(self) -> str:
        return f"<MessageLog {self.direction} from {self.sender_phone}: {self.message_type}>"
