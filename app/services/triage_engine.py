"""Intelligent Triage Engine, Intent Classification, and SLA Priority Assignment."""
import datetime
import random
import re
import string
from typing import Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus
from app.models.log import MessageLog
from app.services.whatsapp import whatsapp_service
from app.services.auto_fix import auto_fix_service


class TriageEngine:
    """Classifies user messages, assigns priority, and handles automated resolution."""

    @staticmethod
    def generate_protocol() -> str:
        """Generate human-readable unique protocol: SD-YYYYMMDD-XXXX."""
        date_part = datetime.datetime.utcnow().strftime("%Y%m%d")
        random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"SD-{date_part}-{random_part}"

    @staticmethod
    def classify_intent(message_text: str) -> Tuple[TicketCategory, TicketPriority, str, bool]:
        """
        Analyze message text and return:
        (category, priority, issue_title, is_critical_p1)
        """
        text = message_text.lower().strip()

        # 1. Critical Incidents (P1)
        critical_keywords = [
            "banco fora", "erro 500", "500 internal server error", "banco caiu",
            "sistema travado", "producao parada", "produção parada", "servidor caiu",
            "database down", "cluster fora", "todos os usuarios sem acesso", "parada geral"
        ]
        for kw in critical_keywords:
            if kw in text:
                return TicketCategory.DATABASE, TicketPriority.P1, f"Incidente Crítico: {kw.title()}", True

        # 2. Authentication / Active Directory / Passwords (Auto-Remediation N1)
        auth_keywords = [
            "senha", "password", "bloqueado", "bloqueada", "desbloquear", "active directory",
            "trocar senha", "redefinir senha", "esqueci minha senha", "mfa", "login",
            "usuario bloqueado", "acesso negado", "credenciais"
        ]
        for kw in auth_keywords:
            if kw in text:
                return TicketCategory.AUTH, TicketPriority.P3, "Solicitação de Autenticação / Reset de Senha AD", False

        # 3. Network / VPN / Connectivity
        network_keywords = [
            "vpn", "conexao", "conexão", "wifi", "wi-fi", "internet", "dns",
            "forticlient", "openvpn", "sem rede", "cabo de rede", "gateway",
            "lentidao na rede", "lentidão na rede"
        ]
        for kw in network_keywords:
            if kw in text:
                return TicketCategory.NETWORK, TicketPriority.P2, "Instabilidade de Rede / Conexão VPN", False

        # 4. Corporate Applications (ERP / CRM)
        erp_keywords = ["crm", "sap", "totvs", "salesforce", "hubspot", "portal do colaborador", "sistema financeiro"]
        for kw in erp_keywords:
            if kw in text:
                return TicketCategory.ERP_CRM, TicketPriority.P2, f"Dúvida / Instabilidade no {kw.upper()}", False

        # 5. Hardware & Peripherals
        hardware_keywords = [
            "mouse", "teclado", "monitor", "notebook", "impressora", "tela azul",
            "fone", "headset", "hd", "carregador", "bateria", "nao liga", "não liga"
        ]
        for kw in hardware_keywords:
            if kw in text:
                return TicketCategory.HARDWARE, TicketPriority.P3, "Manutenção de Hardware / Periférico", False

        # 6. Default Fallback
        return TicketCategory.OTHER, TicketPriority.P4, "Solicitação Geral de Suporte N1", False

    @classmethod
    async def process_incoming_message(
        cls,
        db: Session,
        sender_phone: str,
        sender_name: str,
        message_text: str,
        message_type: str = "text",
        media_url: Optional[str] = None,
        payload_raw: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full orchestration of an incoming WhatsApp message:
        - Triage classification
        - Active healthchecks
        - Ticket creation / resolution
        - MessageLog persistence
        - Reply formatting and delivery
        """
        protocol = cls.generate_protocol()
        category, priority, title, is_critical = cls.classify_intent(message_text)

        status = TicketStatus.OPEN
        auto_remediated = False
        reply_message = ""
        resolution_notes = None
        diagnostics_data: Dict[str, Any] = {}

        # ----------------------------------------------------
        # Automated N1 Triage & Resolution Logic
        # ----------------------------------------------------

        # Scenario A: Critical P1 Incident
        if is_critical:
            status = TicketStatus.ESCALATED_N2
            reply_message = whatsapp_service.template_critical_incident(protocol, sender_name, title)
            resolution_notes = "Incidente de alta severidade P1 detectado pelo motor de triagem. Plantão acionado."

        # Scenario B: Authentication / Active Directory (Auto-Fix N1)
        elif category == TicketCategory.AUTH:
            status = TicketStatus.RESOLVED_AUTO
            auto_remediated = True
            reply_message = whatsapp_service.template_auto_fix_ad(protocol, sender_name)
            resolution_notes = "Resolvido automaticamente via instruções de Autosserviço de Reset AD e MFA."

        # Scenario C: Network / VPN Connectivity (Auto-Diagnostic N1)
        elif category == TicketCategory.NETWORK:
            vpn_diag = await auto_fix_service.run_diagnostics_for_key("vpn", db)
            diagnostics_data = vpn_diag
            status = TicketStatus.OPEN
            reply_message = whatsapp_service.template_auto_fix_vpn(
                protocol, sender_name, vpn_diag.get("status", "OPERATIONAL")
            )
            resolution_notes = f"Diagnóstico de VPN executado (Status: {vpn_diag.get('status')}). Instruções de rede enviadas."

        # Scenario D: Service Health Check (e.g. "O CRM está fora?", "Status do SAP?")
        elif category == TicketCategory.ERP_CRM:
            # Check which service was referenced
            svc_key = "sap" if "sap" in message_text.lower() else "crm"
            svc_diag = await auto_fix_service.run_diagnostics_for_key(svc_key, db)
            diagnostics_data = svc_diag
            status = TicketStatus.RESOLVED_AUTO
            auto_remediated = True
            reply_message = whatsapp_service.template_service_status(
                protocol,
                sender_name,
                svc_diag.get("name", "Sistema Corporativo"),
                svc_diag.get("status", "OPERATIONAL"),
                svc_diag.get("latency_ms", 15.0),
                svc_diag.get("message", "Operação normal.")
            )
            resolution_notes = f"Status em tempo real verificado e entregue ao usuário ({svc_diag.get('name')})."

        # Scenario E: Standard Tickets (Hardware, General Support)
        else:
            status = TicketStatus.OPEN
            reply_message = whatsapp_service.template_ticket_created(
                protocol, sender_name, category.value, priority.value, title
            )

        # ----------------------------------------------------
        # Database Persistence
        # ----------------------------------------------------
        ticket = Ticket(
            protocol=protocol,
            requester_phone=sender_phone,
            requester_name=sender_name,
            title=title,
            description=message_text,
            category=category,
            priority=priority,
            status=status,
            auto_remediated=auto_remediated,
            resolution_notes=resolution_notes,
        )
        db.add(ticket)
        db.flush()  # Generate ticket.id

        # Inbound Message Log
        inbound_log = MessageLog(
            ticket_id=ticket.id,
            sender_phone=sender_phone,
            sender_name=sender_name,
            direction="INBOUND",
            message_type=message_type,
            content=message_text,
            media_url=media_url,
            payload_raw=payload_raw,
        )
        db.add(inbound_log)

        # Outbound Message Log (Bot Response)
        outbound_log = MessageLog(
            ticket_id=ticket.id,
            sender_phone="SERVICE_DESK_BOT",
            sender_name="Bot N1 Service Desk",
            direction="OUTBOUND",
            message_type="text",
            content=reply_message,
            payload_raw=None,
        )
        db.add(outbound_log)

        db.commit()
        db.refresh(ticket)

        # ----------------------------------------------------
        # WhatsApp Delivery (Real API or Mock Logger)
        # ----------------------------------------------------
        await whatsapp_service.send_whatsapp_message(sender_phone, reply_message)

        return {
            "status": "success",
            "protocol": protocol,
            "ticket_id": ticket.id,
            "category": category.value,
            "priority": priority.value,
            "ticket_status": status.value,
            "auto_remediated": auto_remediated,
            "reply_message": reply_message,
            "diagnostics_performed": diagnostics_data if diagnostics_data else None,
        }


triage_engine = TriageEngine()
