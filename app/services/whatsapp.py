"""WhatsApp messaging, payload extraction, and corporate template formatting."""
import json
import logging
from typing import Optional, Dict, Any, Tuple
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service to handle Meta Cloud API communication and template formatting."""

    @staticmethod
    def extract_message_data(payload_dict: Dict[str, Any]) -> Tuple[str, str, str, str, Optional[str]]:
        """
        Extract (phone, name, text_content, message_type, media_url) from either
        standard Meta WhatsApp Cloud API format or direct mock format.
        """
        # 1. Direct Mock Format (Simplified)
        if "phone" in payload_dict and "message" in payload_dict:
            phone = str(payload_dict.get("phone", "")).strip()
            name = payload_dict.get("name", "Colaborador")
            text = payload_dict.get("message", "").strip()
            msg_type = payload_dict.get("message_type", "text")
            media_url = payload_dict.get("media_url")
            return phone, name, text, msg_type, media_url

        # 2. Meta WhatsApp Cloud API Format
        try:
            entry = payload_dict.get("entry", [])[0]
            change = entry.get("changes", [])[0]
            value = change.get("value", {})
            
            # Contact name extraction
            contacts = value.get("contacts", [])
            sender_name = contacts[0].get("profile", {}).get("name", "Colaborador") if contacts else "Colaborador"
            
            messages = value.get("messages", [])
            if not messages:
                return "", "", "", "unknown", None

            msg = messages[0]
            phone = msg.get("from", "")
            msg_type = msg.get("type", "text")
            media_url = None
            text_content = ""

            if msg_type == "text":
                text_content = msg.get("text", {}).get("body", "")
            elif msg_type == "image":
                text_content = msg.get("image", {}).get("caption", "[Imagem anexada]")
                media_url = msg.get("image", {}).get("link") or msg.get("image", {}).get("id")
            elif msg_type == "audio":
                text_content = "[Áudio de voz recebido]"
                media_url = msg.get("audio", {}).get("link") or msg.get("audio", {}).get("id")
            elif msg_type == "document":
                text_content = msg.get("document", {}).get("filename", "[Documento anexado]")
                media_url = msg.get("document", {}).get("link")
            elif msg_type == "interactive":
                interactive = msg.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    text_content = interactive.get("button_reply", {}).get("title", "")
                elif interactive.get("type") == "list_reply":
                    text_content = interactive.get("list_reply", {}).get("title", "")

            return phone, sender_name, text_content, msg_type, media_url
        except Exception as exc:
            logger.error(f"Error parsing Meta payload: {exc}")
            return "", "", "", "error", None

    @staticmethod
    async def send_whatsapp_message(
        recipient_phone: str, 
        message_text: str, 
        media_url: Optional[str] = None
    ) -> bool:
        """
        Send message via Meta WhatsApp Cloud API (or logs simulation in dev).
        """
        logger.info(f"[WHATSAPP OUTBOUND -> {recipient_phone}]:\n{message_text}")
        
        # If real Meta credentials are provided, send HTTP request
        if (
            settings.WHATSAPP_API_TOKEN 
            and not settings.WHATSAPP_API_TOKEN.startswith("EAAG...MOCK")
            and settings.WHATSAPP_PHONE_NUMBER_ID
        ):
            url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
                "Content-Type": "application/json",
            }
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient_phone,
                "type": "text",
                "text": {"preview_url": False, "body": message_text},
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(url, headers=headers, json=data)
                    return response.status_code in [200, 201]
            except Exception as e:
                logger.error(f"Failed to send real WhatsApp message: {e}")
                return False

        # In dev/mock mode, successfully simulate sending
        return True

    # ----------------------------------------------------
    # Templates de Resposta Corporativa Elegante
    # ----------------------------------------------------

    @staticmethod
    def template_ticket_created(protocol: str, name: str, category: str, priority: str, title: str) -> str:
        priority_emoji = {
            "P1": "🚨 *CRÍTICO (P1)*",
            "P2": "⚠️ *ALTA (P2)*",
            "P3": "🟡 *MÉDIA (P3)*",
            "P4": "🟢 *BAIXA (P4)*",
        }.get(priority, "🟡 *MÉDIA*")

        return (
            f"🎫 *SERVICE DESK CORPORATIVO*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Olá, *{name}*! Seu chamado foi registrado com sucesso.\n\n"
            f"📋 *Protocolo:* `{protocol}`\n"
            f"📁 *Categoria:* {category}\n"
            f"⚡ *Prioridade:* {priority_emoji}\n"
            f"📝 *Assunto:* {title}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ *SLA de Atendimento:* Nossa equipe N2 já foi notificada e entrará em contato em breve.\n\n"
            f"_Você receberá atualizações automáticas sobre o andamento por este canal._"
        )

    @staticmethod
    def template_critical_incident(protocol: str, name: str, title: str) -> str:
        return (
            f"🚨 *ALERTA DE INCIDENTE CRÍTICO (P1)*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Olá, *{name}*. Detectamos um incidente de alta severidade!\n\n"
            f"📋 *Protocolo:* `{protocol}`\n"
            f"🔥 *Severidade:* *P1 - CRÍTICO (Impacto em Produção)*\n"
            f"📝 *Incidente:* {title}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *Ação Automática:* O time de **Plantão DevOps / Infraestrutura** foi acionado via pager imediato.\n"
            f"Status em tempo real disponível no canal de incidentes."
        )

    @staticmethod
    def template_auto_fix_ad(protocol: str, name: str) -> str:
        return (
            f"🔐 *AUTOATENDIMENTO N1: RESET DE SENHA / AD*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Olá, *{name}*! Identificamos uma solicitação de autenticação/senha.\n\n"
            f"📋 *Protocolo:* `{protocol}`\n"
            f"⚡ *Resolução Imediata N1:*\n"
            f"1️⃣ Acesse o portal de autosserviço: *https://passwords.corp.internal/reset*\n"
            f"2️⃣ Informe sua matrícula corporativa e confirme o token MFA no seu celular.\n"
            f"3️⃣ Caso sua conta esteja bloqueada por tentativas inválidas, ela será desbloqueada em até 3 minutos.\n\n"
            f"✅ *Status:* Chamado resolvido automaticamente via autosserviço.\n"
            f"_Se ainda não conseguir acessar, responda 'Preciso de ajuda humana' para falar com o analista N2._"
        )

    @staticmethod
    def template_auto_fix_vpn(protocol: str, name: str, gateway_status: str) -> str:
        status_txt = "🟢 OPERANTE" if gateway_status == "OPERATIONAL" else "🔴 EM MANUTENÇÃO"
        return (
            f"🌐 *DIAGNÓSTICO N1: CONECTIVIDADE & VPN*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Olá, *{name}*! Realizamos um teste de diagnóstico de rede em tempo real.\n\n"
            f"📋 *Protocolo:* `{protocol}`\n"
            f"📡 *Gateway VPN Corporativo:* {status_txt}\n\n"
            f"🛠️ *Passos para Auto-Recuperação:*\n"
            f"1. Abra o prompt de comando e execute: `ipconfig /flushdns`\n"
            f"2. Desconecte e reconecte seu client VPN (FortiClient / OpenVPN).\n"
            f"3. Verifique se o relógio do seu computador está sincronizado com o horário de Brasília.\n\n"
            f"💡 *Precisa de mais ajuda?* Este chamado permanecerá aberto aguardando sua confirmação."
        )

    @staticmethod
    def template_service_status(protocol: str, name: str, service_name: str, status: str, latency: float, notes: str) -> str:
        status_icon = "🟢 *OPERANTE*" if status == "OPERATIONAL" else ("🟡 *LENTIDÃO / DEGRADADO*" if status == "DEGRADED" else "🔴 *FORA DO AR (INCIDENTE)*")
        return (
            f"🔍 *DIAGNÓSTICO AUTOMÁTICO DE SERVIÇO*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Olá, *{name}*! Realizamos uma checagem em tempo real do sistema solicitado.\n\n"
            f"📋 *Protocolo:* `{protocol}`\n"
            f"🖥️ *Serviço:* {service_name}\n"
            f"📊 *Status Atual:* {status_icon}\n"
            f"⚡ *Latência Medida:* `{latency:.1f} ms`\n"
            f"ℹ️ *Informação:* {notes}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ *Resolução:* Informação de status entregue automaticamente."
        )

    @staticmethod
    def template_status_updated(protocol: str, new_status: str, notes: Optional[str] = None) -> str:
        status_map = {
            "OPEN": "🟡 Aberto (Fila de Atendimento)",
            "IN_PROGRESS": "🔵 Em Atendimento por um Analista N2",
            "RESOLVED_AUTO": "🟢 Resolvido Automaticamente",
            "RESOLVED": "✅ Resolvido com Sucesso",
            "ESCALATED_N2": "🚀 Escalado para Especialistas N2/N3",
        }
        status_label = status_map.get(new_status, new_status)
        notes_section = f"\n📝 *Observações:* {notes}\n" if notes else ""
        return (
            f"🔔 *ATUALIZAÇÃO DE CHAMADO*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Seu chamado protocolo `{protocol}` teve o status alterado.\n\n"
            f"📌 *Novo Status:* {status_label}{notes_section}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Equipe de Sucesso & Service Desk Corporativo."
        )


whatsapp_service = WhatsAppService()
