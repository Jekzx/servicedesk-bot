"""WhatsApp Webhook verification and message receiver router."""
import json
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Request, Response, status, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.webhook import WebhookResponse
from app.services.whatsapp import whatsapp_service
from app.services.triage_engine import triage_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhook", tags=["WhatsApp Webhook"])


@router.get("", summary="Meta WhatsApp Webhook Verification Challenge")
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """
    Verification endpoint required by Meta WhatsApp Cloud API.
    Validates hub.verify_token and echoes back hub.challenge as plain text.
    """
    logger.info(f"Webhook GET verification received: mode={hub_mode}, token={hub_verify_token}")

    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verification challenge successful!")
        return Response(content=hub_challenge or "", media_type="text/plain")

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch or invalid mode"
    )


@router.post("", response_model=WebhookResponse, summary="Receive WhatsApp Webhook Message")
async def receive_webhook_message(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Processes incoming WhatsApp messages from both official Meta Cloud API payloads
    and direct mock simulator payloads.
    """
    try:
        body_bytes = await request.body()
        payload_raw = body_bytes.decode("utf-8")
        payload_dict = json.loads(payload_raw) if payload_raw else {}
    except Exception as e:
        logger.error(f"Failed to parse webhook JSON body: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    # Extract normalized data
    phone, name, text_content, msg_type, media_url = whatsapp_service.extract_message_data(payload_dict)

    if not phone or not text_content:
        # Might be a status update payload from Meta (delivered, read, etc.)
        return WebhookResponse(
            status="ignored",
            reply_message="Evento de status ou payload sem mensagem de texto processável recebido.",
        )

    # Process through Intelligent Triage Engine
    result = await triage_engine.process_incoming_message(
        db=db,
        sender_phone=phone,
        sender_name=name,
        message_text=text_content,
        message_type=msg_type,
        media_url=media_url,
        payload_raw=payload_raw,
    )

    return WebhookResponse(**result)
