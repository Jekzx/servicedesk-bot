#!/usr/bin/env python3
"""Interactive CLI for testing and simulating WhatsApp conversations with Service Desk Bot."""
import os
import sys
import time
import httpx

# Configure UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

API_BASE_URL = "http://localhost:8000"
WEBHOOK_URL = f"{API_BASE_URL}/api/webhook"


def print_banner():
    print("=" * 68)
    print(" [*] SERVICE DESK WHATSAPP BOT - SIMULADOR INTERATIVO CLI")
    print("=" * 68)
    print(" Permite testar o fluxo de ponta a ponta sem custos de Meta API.")
    print(" Certifique-se de que a API FastAPI está em execução na porta 8000.")
    print("-" * 68)


def send_simulated_message(phone: str, name: str, message_text: str):
    """Send payload to /api/webhook and print response."""
    payload = {
        "phone": phone,
        "name": name,
        "message": message_text,
        "message_type": "text"
    }

    print(f"\n[>] [Enviando WhatsApp de '{name}' ({phone})]:")
    print(f"    \"{message_text}\"")
    print("[*] Aguardando processamento do Motor de Triagem...")

    try:
        start = time.time()
        with httpx.Client(timeout=10.0) as client:
            response = client.post(WEBHOOK_URL, json=payload)
            elapsed = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()
            print("\n" + "─" * 68)
            print("[<] [RESPOSTA DO BOT N1 RECEBIDA]:")
            print("─" * 68)
            print(data.get("reply_message", ""))
            print("─" * 68)
            print(f"[*] Protocolo: {data.get('protocol')} | Categoria: {data.get('category')} | Prioridade: {data.get('priority')} | Status: {data.get('ticket_status')} | Auto-Remediado: {data.get('auto_remediated')} | Tempo: {elapsed:.1f}ms")
            print("─" * 68)
        else:
            print(f"[!] Erro na requisição: HTTP {response.status_code} - {response.text}")
    except httpx.ConnectError:
        print(f"[!] Falha de conexão: Não foi possível alcançar {WEBHOOK_URL}.")
        print("[*] Dica: Inicie o servidor FastAPI executando: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"[!] Erro inesperado: {e}")


def list_recent_tickets():
    """Fetch and print recent tickets from /api/tickets."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{API_BASE_URL}/api/tickets?page=1&page_size=10")
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                print("\n[+] LISTA DE TICKETS RECENTES NO SISTEMA:")
                print(f"Total registrados: {data.get('total')}")
                print(f"{'PROTOCOLO':<20} | {'SOLICITANTE':<15} | {'CATEGORIA':<12} | {'PRIO':<6} | {'STATUS':<15}")
                print("─" * 78)
                for t in items:
                    print(f"{t.get('protocol'):<20} | {t.get('requester_name', '')[:14]:<15} | {t.get('category'):<12} | {t.get('priority'):<6} | {t.get('status'):<15}")
            else:
                print(f"[!] Erro ao listar: {resp.text}")
    except Exception as e:
        print(f"[!] Erro de conexão: {e}")


def check_infrastructure_status():
    """Fetch infrastructure status from /api/health/services."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{API_BASE_URL}/api/health/services")
            if resp.status_code == 200:
                data = resp.json()
                print(f"\n[+] DIAGNÓSTICO DE INFRAESTRUTURA: {data.get('system_status')}")
                print(f"{'SERVIÇO':<35} | {'STATUS':<15} | {'LATÊNCIA':<10}")
                print("─" * 68)
                for s in data.get("services", []):
                    status_str = s.get("status")
                    print(f"{s.get('name')[:34]:<35} | {status_str:<15} | {s.get('latency_ms'):.1f} ms")
            else:
                print(f"[!] Erro ao consultar saúde: {resp.text}")
    except Exception as e:
        print(f"[!] Erro de conexão: {e}")


def main_menu():
    default_phone = "551199887766"
    default_name = "Carlos Eduardo"

    while True:
        print_banner()
        print(" Escolha um cenário para simular:")
        print(" [1] Reset AD / Senha bloqueada (Autoatendimento N1)")
        print(" [2] Problema na VPN corporativa (Diagnóstico de Rede N1)")
        print(" [3] Erro 500 no Banco de Dados (Incidente Crítico P1)")
        print(" [4] Status do CRM corporativo (Diagnóstico de Serviço em Tempo Real)")
        print(" [5] Defeito no monitor (Chamado Geral de Hardware)")
        print(" [6] Digitar mensagem personalizada livre")
        print(" [7] Consultar últimos tickets abertos no banco")
        print(" [8] Executar diagnóstico geral de servidores corporativos")
        print(" [0] Sair")
        print("-" * 68)

        choice = input(">> Digite sua opção (0-8): ").strip()

        if choice == "1":
            send_simulated_message(
                phone=default_phone,
                name=default_name,
                message_text="Olá, meu usuário está bloqueado no Active Directory e preciso redefinir minha senha urgente."
            )
        elif choice == "2":
            send_simulated_message(
                phone=default_phone,
                name=default_name,
                message_text="Estou tentando conectar na VPN pelo FortiClient de casa mas está dando falha de handshake e sem conexão."
            )
        elif choice == "3":
            send_simulated_message(
                phone="5511988880000",
                name="Diretor de Operações",
                message_text="ALERTA! Erro 500 no Banco de Dados principal e sistema travado, todos os usuários sem acesso!"
            )
        elif choice == "4":
            send_simulated_message(
                phone=default_phone,
                name=default_name,
                message_text="Boa tarde! O CRM está fora do ar ou é só no meu computador?"
            )
        elif choice == "5":
            send_simulated_message(
                phone=default_phone,
                name=default_name,
                message_text="Bom dia, meu monitor secundário Dell não está ligando, o cabo HDMI parece estar com mau contato."
            )
        elif choice == "6":
            name = input("Seu nome (Enter para 'Colaborador'): ").strip() or "Colaborador"
            phone = input("Seu telefone (Enter para '5511999998888'): ").strip() or "5511999998888"
            msg = input("Mensagem para o Service Desk: ").strip()
            if msg:
                send_simulated_message(phone=phone, name=name, message_text=msg)
        elif choice == "7":
            list_recent_tickets()
        elif choice == "8":
            check_infrastructure_status()
        elif choice == "0":
            print("\nEncerrando simulador. Até logo!")
            sys.exit(0)
        else:
            print("\nOpção inválida. Escolha entre 0 e 8.")

        input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main_menu()
