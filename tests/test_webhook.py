"""Tests for WhatsApp Webhook Verification and Message Handling."""
from app.core.config import settings


def test_webhook_get_verification_success(client):
    """Test successful Meta Webhook challenge verification."""
    response = client.get(
        "/api/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": settings.WHATSAPP_VERIFY_TOKEN,
            "hub.challenge": "1158201444",
        }
    )
    assert response.status_code == 200
    assert response.text == "1158201444"


def test_webhook_get_verification_invalid_token(client):
    """Test rejection with invalid verify token."""
    response = client.get(
        "/api/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "WRONG_TOKEN",
            "hub.challenge": "1158201444",
        }
    )
    assert response.status_code == 403


def test_webhook_post_direct_mock(client):
    """Test receiving message via direct mock payload."""
    payload = {
        "phone": "5511999998888",
        "name": "Maria Silva",
        "message": "Esqueci minha senha do Windows e estou bloqueada",
        "message_type": "text"
    }
    response = client.post("/api/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["protocol"].startswith("SD-")
    assert data["category"] == "AUTH"
    assert data["auto_remediated"] is True
    assert "https://passwords.corp.internal/reset" in data["reply_message"]


def test_webhook_post_meta_cloud_api_format(client):
    """Test receiving message in official Meta Cloud API JSON format."""
    meta_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "1555023", "phone_number_id": "10987654321"},
                            "contacts": [{"profile": {"name": "Carlos Tech"}, "wa_id": "5511988887777"}],
                            "messages": [
                                {
                                    "from": "5511988887777",
                                    "id": "wamid.HBgL...",
                                    "timestamp": "1710000000",
                                    "text": {"body": "Não consigo conectar na VPN pelo FortiClient"},
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    response = client.post("/api/webhook", json=meta_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["category"] == "NETWORK"
    assert "DIAGNÓSTICO N1" in data["reply_message"]
