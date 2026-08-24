"""Unit tests for Triage Engine intent classification and prioritization."""
from app.services.triage_engine import triage_engine
from app.models.ticket import TicketCategory, TicketPriority


def test_classify_critical_database_incident():
    cat, prio, title, is_critical = triage_engine.classify_intent("ALERTA: Banco fora do ar e erro 500 no sistema!")
    assert cat == TicketCategory.DATABASE
    assert prio == TicketPriority.P1
    assert is_critical is True


def test_classify_auth_password_reset():
    cat, prio, title, is_critical = triage_engine.classify_intent("Preciso trocar senha do Active Directory pois bloqueou meu login.")
    assert cat == TicketCategory.AUTH
    assert prio == TicketPriority.P3
    assert is_critical is False


def test_classify_vpn_network():
    cat, prio, title, is_critical = triage_engine.classify_intent("Problemas com a conexao VPN FortiClient em home office")
    assert cat == TicketCategory.NETWORK
    assert prio == TicketPriority.P2
    assert is_critical is False


def test_classify_crm_service():
    cat, prio, title, is_critical = triage_engine.classify_intent("O CRM corporativo está fora do ar?")
    assert cat == TicketCategory.ERP_CRM
    assert prio == TicketPriority.P2
    assert is_critical is False


def test_classify_hardware_issue():
    cat, prio, title, is_critical = triage_engine.classify_intent("Meu mouse e teclado pararam de funcionar na docking station")
    assert cat == TicketCategory.HARDWARE
    assert prio == TicketPriority.P3
    assert is_critical is False


def test_classify_general_fallback():
    cat, prio, title, is_critical = triage_engine.classify_intent("Gostaria de tirar uma duvida sobre a politica de reembolso de TI")
    assert cat == TicketCategory.OTHER
    assert prio == TicketPriority.P4
    assert is_critical is False
