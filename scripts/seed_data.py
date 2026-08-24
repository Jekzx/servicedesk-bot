"""Seed initial demo data for Service Desk Bot."""
import os
import sys
import datetime

# Configure UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, init_db
from app.models.user import CorporateUser, CorporateService
from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus
from app.models.log import MessageLog
from app.services.auto_fix import auto_fix_service


def seed():
    print("[*] Initializing database and tables...")
    init_db()
    db = SessionLocal()

    try:
        # 1. Monitored Corporate Services
        auto_fix_service.ensure_default_services(db)
        print("[+] Corporate services catalog seeded.")

        # 2. Corporate Users
        users = [
            CorporateUser(name="Ana Clara Silva", phone="551199887711", email="ana.silva@corp.internal", department="Financeiro", role="Analista Sênior", is_vip=False),
            CorporateUser(name="Rodrigo Santoro", phone="551199887722", email="rodrigo.santoro@corp.internal", department="Operações", role="Gerente de Operações", is_vip=True),
            CorporateUser(name="Mariana Lima", phone="551199887733", email="mariana.lima@corp.internal", department="Comercial", role="Executiva de Vendas", is_vip=False),
            CorporateUser(name="Felipe Castro", phone="551199887744", email="felipe.castro@corp.internal", department="Engenharia de Software", role="Tech Lead", is_vip=True),
        ]
        for u in users:
            if not db.query(CorporateUser).filter(CorporateUser.phone == u.phone).first():
                db.add(u)
        db.commit()
        print("[+] Corporate users seeded.")

        # 3. Demo Tickets
        demo_tickets = [
            {
                "protocol": "SD-20260824-A101",
                "requester_phone": "551199887711",
                "requester_name": "Ana Clara Silva",
                "title": "Solicitação de Autenticação / Reset de Senha AD",
                "description": "Esqueci minha senha do Windows após as férias e meu login bloqueou.",
                "category": TicketCategory.AUTH,
                "priority": TicketPriority.P3,
                "status": TicketStatus.RESOLVED_AUTO,
                "auto_remediated": True,
                "resolution_notes": "Resolvido automaticamente via link seguro de autosserviço MFA.",
            },
            {
                "protocol": "SD-20260824-B202",
                "requester_phone": "551199887722",
                "requester_name": "Rodrigo Santoro",
                "title": "Instabilidade de Rede / Conexão VPN",
                "description": "Não consigo conectar no FortiClient hoje de manhã em home office.",
                "category": TicketCategory.NETWORK,
                "priority": TicketPriority.P2,
                "status": TicketStatus.IN_PROGRESS,
                "auto_remediated": False,
                "resolution_notes": "Analista N2 verificando rota do IP externo do colaborador.",
            },
            {
                "protocol": "SD-20260824-C303",
                "requester_phone": "551199887744",
                "requester_name": "Felipe Castro",
                "title": "Incidente Crítico: Erro 500 no Banco de Dados",
                "description": "Cluster PostgreSQL de Produção apresentando timeout de conexões e erro 500 na API.",
                "category": TicketCategory.DATABASE,
                "priority": TicketPriority.P1,
                "status": TicketStatus.ESCALATED_N2,
                "auto_remediated": False,
                "resolution_notes": "Incidente P1 escalado para time de DBA e DevOps de plantão.",
            },
            {
                "protocol": "SD-20260824-D404",
                "requester_phone": "551199887733",
                "requester_name": "Mariana Lima",
                "title": "Dúvida / Instabilidade no CRM",
                "description": "O CRM corporativo está fora do ar? Não consigo salvar a proposta.",
                "category": TicketCategory.ERP_CRM,
                "priority": TicketPriority.P2,
                "status": TicketStatus.RESOLVED_AUTO,
                "auto_remediated": True,
                "resolution_notes": "Diagnóstico em tempo real retornou CRM 100% operacional.",
            },
        ]

        now = datetime.datetime.now(datetime.timezone.utc)
        for dt in demo_tickets:
            if not db.query(Ticket).filter(Ticket.protocol == dt["protocol"]).first():
                t = Ticket(**dt)
                db.add(t)
                db.flush()
                # Add sample logs
                log_in = MessageLog(
                    ticket_id=t.id,
                    sender_phone=t.requester_phone,
                    sender_name=t.requester_name,
                    direction="INBOUND",
                    message_type="text",
                    content=t.description,
                    timestamp=now - datetime.timedelta(minutes=30)
                )
                log_out = MessageLog(
                    ticket_id=t.id,
                    sender_phone="SERVICE_DESK_BOT",
                    sender_name="Bot N1 Service Desk",
                    direction="OUTBOUND",
                    message_type="text",
                    content=f"Chamado {t.protocol} processado. Status: {t.status.value}",
                    timestamp=now - datetime.timedelta(minutes=29)
                )
                db.add(log_in)
                db.add(log_out)

        db.commit()
        print("[+] Demo tickets and message logs seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
