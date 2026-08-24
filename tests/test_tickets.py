"""Unit and integration tests for Tickets CRUD and Status updates."""
from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus


def test_create_and_list_tickets(client):
    """Test manual ticket creation and retrieval with filters."""
    # 1. Create ticket manually
    create_payload = {
        "requester_phone": "5511988881234",
        "requester_name": "Juliana Lima",
        "title": "Solicitação de acesso à pasta da Rede",
        "description": "Preciso de permissão de leitura na pasta Compartilhada/Financeiro.",
        "category": "NETWORK",
        "priority": "P3",
        "status": "OPEN",
    }
    create_resp = client.post("/api/tickets", json=create_payload)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["protocol"].startswith("SD-")
    assert created_data["title"] == create_payload["title"]

    ticket_id = created_data["id"]

    # 2. List tickets with status filter
    list_resp = client.get("/api/tickets?status=OPEN")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    assert any(t["id"] == ticket_id for t in list_data["items"])

    # 3. Get ticket detail
    get_resp = client.get(f"/api/tickets/{ticket_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == ticket_id


def test_update_ticket_status(client):
    """Test updating ticket status and adding resolution notes."""
    # Create a ticket first via webhook
    msg_payload = {
        "phone": "5511999991111",
        "name": "Roberto Justos",
        "message": "Teclado com defeito na tecla espaço",
        "message_type": "text"
    }
    hook_resp = client.post("/api/webhook", json=msg_payload)
    assert hook_resp.status_code == 200
    t_id = hook_resp.json()["ticket_id"]

    # Update status to RESOLVED
    patch_payload = {
        "status": "RESOLVED",
        "resolution_notes": "Teclado substituído por novo modelo Dell USB no andar 3.",
        "notify_requester": False
    }
    patch_resp = client.patch(f"/api/tickets/{t_id}/status", json=patch_payload)
    assert patch_resp.status_code == 200
    updated_data = patch_resp.json()
    assert updated_data["status"] == "RESOLVED"
    assert updated_data["resolution_notes"] == patch_payload["resolution_notes"]
