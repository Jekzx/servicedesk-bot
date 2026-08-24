"""Pydantic schemas for WhatsApp Cloud API & Webhook Mock payloads."""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


# ----------------------------------------------------
# Official Meta WhatsApp Cloud API Webhook Structure
# ----------------------------------------------------

class WhatsAppTextMessage(BaseModel):
    body: str


class WhatsAppMediaMessage(BaseModel):
    id: Optional[str] = None
    mime_type: Optional[str] = None
    sha256: Optional[str] = None
    caption: Optional[str] = None
    link: Optional[str] = None


class WhatsAppInteractiveReply(BaseModel):
    id: str
    title: str


class WhatsAppInteractiveMessage(BaseModel):
    type: str
    button_reply: Optional[WhatsAppInteractiveReply] = None
    list_reply: Optional[WhatsAppInteractiveReply] = None


class WhatsAppIncomingMessage(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    type: str  # text, image, audio, document, interactive
    text: Optional[WhatsAppTextMessage] = None
    image: Optional[WhatsAppMediaMessage] = None
    audio: Optional[WhatsAppMediaMessage] = None
    document: Optional[WhatsAppMediaMessage] = None
    interactive: Optional[WhatsAppInteractiveMessage] = None


class WhatsAppContactProfile(BaseModel):
    name: Optional[str] = "Colaborador"


class WhatsAppContact(BaseModel):
    profile: Optional[WhatsAppContactProfile] = None
    wa_id: str


class WhatsAppValueMetadata(BaseModel):
    display_phone_number: Optional[str] = None
    phone_number_id: Optional[str] = None


class WhatsAppChangeValue(BaseModel):
    messaging_product: Optional[str] = "whatsapp"
    metadata: Optional[WhatsAppValueMetadata] = None
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppIncomingMessage]] = None


class WhatsAppChange(BaseModel):
    value: WhatsAppChangeValue
    field: str = "messages"


class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]


class WhatsAppWebhookPayload(BaseModel):
    """Standard Meta WhatsApp Cloud API Payload."""
    object: Optional[str] = "whatsapp_business_account"
    entry: Optional[List[WhatsAppEntry]] = None


# ----------------------------------------------------
# Simplified / Direct Mock Webhook Payload (For CLI / Web UI)
# ----------------------------------------------------

class DirectMessagePayload(BaseModel):
    """Flexible payload for testing and local simulation."""
    phone: str = Field(..., json_schema_extra={"example": "5511999998888"})
    name: Optional[str] = Field("Colaborador", json_schema_extra={"example": "Ana Silva"})
    message: str = Field(..., json_schema_extra={"example": "Não consigo conectar na VPN da empresa"})
    media_url: Optional[str] = None
    message_type: Optional[str] = "text"


class WebhookResponse(BaseModel):
    status: str = "success"
    protocol: Optional[str] = None
    ticket_id: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    ticket_status: Optional[str] = None
    auto_remediated: bool = False
    reply_message: str
    diagnostics_performed: Optional[Dict[str, Any]] = None
