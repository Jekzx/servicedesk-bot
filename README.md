# 🤖 Service Desk WhatsApp Automation & Diagnostics Bot

<p align="center">
  <a href="https://servicedesk-bot-w8kr.vercel.app" target="_blank">
    <img src="https://img.shields.io/badge/Live%20Demo-servicedesk--bot--w8kr.vercel.app-00E5FF?style=for-the-badge&logo=vercel&logoColor=white" alt="Live Demo Vercel" />
  </a>
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Pytest-100%25%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest" />
</p>

---

## 🌐 Live Preview & Demonstração Online

A aplicação está disponível e rodando em produção na Vercel:

🔗 **[https://servicedesk-bot-w8kr.vercel.app](https://servicedesk-bot-w8kr.vercel.app)**

* 🖥️ **Painel de Chamados & Bot Flutuante**: [servicedesk-bot-w8kr.vercel.app](https://servicedesk-bot-w8kr.vercel.app)
* 📑 **Swagger API Docs (OpenAPI)**: [servicedesk-bot-w8kr.vercel.app/docs](https://servicedesk-bot-w8kr.vercel.app/docs)

---

## 📖 Visão Geral

O **Service Desk WhatsApp Automation & Diagnostics Bot** é uma solução corporativa completa de **Autoatendimento N1**, **Triagem Inteligente de Chamados** e **Diagnóstico Ativo de Infraestrutura** integrada ao **WhatsApp** (Meta Cloud API & Webhook Mock).

A aplicação analisa as mensagens enviadas pelos colaboradores, identifica a categoria do incidente (**Active Directory/Senha**, **VPN/Rede**, **Incidentes Críticos P1**, **ERP/CRM**, **Hardware**), realiza checagens ativas de saúde de servidores em tempo real, executa **auto-remediação N1** sem intervenção humana e gera protocolos únicos com persistência relacional e controle de SLA.

Além da API RESTful e documentação Swagger, o projeto acompanha um **Dashboard Web integrado** em tela cheia com paleta moderna **Titanium Obsidian & Neon Cyber**, **Simulador do WhatsApp Web em tempo real** e um **CLI interativo no terminal** para testes sem necessidade de credenciais pagas da Meta.

---

## 🏛️ Arquitetura do Sistema

```mermaid
flowchart TD
    User([👤 Colaborador / WhatsApp]) -->|Mensagem ou Áudio| Webhook[📡 POST /api/webhook]
    MetaAPI([☁️ Meta WhatsApp Cloud API]) -.->|Webhook Event| Webhook
    
    subgraph FastAPI Core
        Webhook --> Triage[🧠 Triage Engine]
        
        Triage -->|Regra AD / Senha| AutoFix1[🔐 Autosserviço N1 / MFA Reset]
        Triage -->|Regra VPN / Rede| AutoFix2[🌐 Diagnóstico de Rede & DNS]
        Triage -->|Regra ERP / CRM| AutoFix3[📊 Healthcheck URL em Tempo Real]
        Triage -->|Erro 500 / Banco Fora| CritP1[🚨 Incidente P1 - Escala Plantão]
        Triage -->|Chamado Geral| TicketCreate[🎫 Abertura de Ticket P3/P4]
        
        AutoFix1 --> DB[(💾 PostgreSQL / SQLite)]
        AutoFix2 --> DB
        AutoFix3 --> DB
        CritP1 --> DB
        TicketCreate --> DB
    end

    DB --> Dashboard[🖥️ Painel Web Service Desk]
    DB --> REST[🔌 RESTful API /api/tickets]
    DB -->|Notificação WhatsApp| Reply[💬 Resposta WhatsApp / Template]
    Reply --> User
```

---

## ✨ Funcionalidades Principais

* **📡 Webhook WhatsApp Multi-formato**: Suporte completo ao fluxo oficial da **Meta Cloud API** (verificação `GET hub.challenge` e `POST messages`) e payloads diretos para simulação.
* **🧠 Motor de Triagem Inteligente (`triage_engine.py`)**:
  * **Active Directory & Senhas**: Detecção de bloqueios de conta com instruções imediatas de reset via MFA (`RESOLVED_AUTO`).
  * **Rede & VPN**: Diagnóstico de conectividade em tempo real com orientações de DNS e adaptor de rede.
  * **Incidentes Críticos P1**: Identificação de termos de alta severidade (*"banco fora"*, *"erro 500"*, *"produção parada"*), escalando imediatamente para o time N2/DevOps com protocolo de emergência.
  * **Sistemas Corporativos**: Consulta de disponibilidade em tempo real de CRM, ERP SAP, VPN Gateway e Cluster de Banco de Dados.
* **🛠️ Diagnóstico & Auto-Remediação N1 (`auto_fix.py`)**: Healthchecks assíncronos que respondem ao usuário se o sistema está operante ou em janela de manutenção antes da abertura de tickets manuais.
* **📊 Painel Web & Simulador WhatsApp Web**: Interface visual moderna Dark Mode com estatísticas SLA, gestão de chamados em tela cheia e widget flutuante do WhatsApp Web.
* **💻 CLI Interativo de Terminal (`scripts/simulate_whatsapp.py`)**: Menu interativo com cenários pré-configurados para testes rápidos de ponta a ponta.
* **🧪 Testes Automatizados com Pytest**: Cobertura completa de testes unitários e de integração para webhooks, motor de triagem, CRUD de tickets e diagnósticos.

---

## 📂 Estrutura do Projeto

```plaintext
servicedesk-bot/
├── api/
│   └── index.py                  # Ponto de entrada Serverless da Vercel
├── app/
│   ├── core/
│   │   ├── config.py             # Configurações Pydantic Settings e .env
│   │   └── database.py           # Conexão SQLAlchemy & SessionLocal (PostgreSQL / SQLite)
│   ├── models/
│   │   ├── base.py               # DeclarativeBase e mixins de UUID e timestamps
│   │   ├── ticket.py             # Modelo Ticket (protocolo, categoria, prioridade P1-P4, status)
│   │   ├── log.py                # Modelo MessageLog (histórico de mensagens e payloads)
│   │   └── user.py               # Modelos CorporateUser e CorporateService
│   ├── schemas/
│   │   ├── webhook.py            # Schemas Pydantic para payload Meta WhatsApp & Mock
│   │   ├── ticket.py             # Schemas de criação, filtros, estatísticas e atualização
│   │   └── health.py             # Schemas de monitoramento de serviços de infraestrutura
│   ├── services/
│   │   ├── whatsapp.py           # Envio, recepção e templates corporativos formatados
│   │   ├── triage_engine.py      # Motor de triagem inteligente e cálculo de SLA
│   │   └── auto_fix.py           # Diagnósticos em tempo real e auto-remediação N1
│   ├── routers/
│   │   ├── webhook.py            # Endpoints GET e POST /api/webhook
│   │   ├── tickets.py            # CRUD RESTful e atualização de status com notificação
│   │   ├── health.py             # Healthcheck e diagnóstico sob demanda
│   │   └── dashboard.py          # Métricas analíticas e estatísticas em tempo real
│   ├── static/
│   │   ├── style.css             # Design System Titanium Obsidian & Neon Cyber
│   │   └── app.js                # Lógica frontend do Dashboard e Bot WhatsApp
│   ├── templates/
│   │   └── index.html            # Interface Web integrada
│   ├── embedded_assets.py        # Assets embarcados para runtime serverless
│   └── main.py                   # Ponto de entrada FastAPI e middlewares
├── scripts/
│   ├── simulate_whatsapp.py      # CLI interativo no terminal
│   ├── seed_data.py              # Povoamento inicial de banco de dados
│   └── build_embedded_assets.py  # Script de build para empacotamento de assets
├── tests/
│   ├── conftest.py               # Fixtures do Pytest e banco SQLite in-memory
│   ├── test_webhook.py           # Testes do webhook da Meta Cloud API
│   ├── test_triage.py            # Testes do motor de triagem e regras de negócio
│   ├── test_tickets.py           # Testes do CRUD e filtros de tickets
│   └── test_health.py            # Testes dos endpoints de monitoramento de saúde
├── main.py                       # Entrypoint na raiz para preset FastAPI da Vercel
├── vercel.json                   # Configuração de rewrites serverless da Vercel
├── Dockerfile                    # Dockerfile multi-stage otimizado
├── docker-compose.yml            # Orquestração FastAPI + PostgreSQL 16
├── requirements.txt              # Dependências do projeto
└── README.md                     # Documentação completa
```

---

## 🚀 Como Executar Localmente

### 1. Clonar o Repositório e Criar Ambiente Virtual

```bash
git clone https://github.com/Jekzx/servicedesk-bot.git
cd servicedesk-bot

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
.\venv\Scripts\activate
# No Linux/macOS:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo `.env.example` para `.env`:

```bash
cp .env.example .env
```

### 3. Povoar o Banco de Dados com Dados de Demonstração

```bash
python scripts/seed_data.py
```

### 4. Iniciar o Servidor de Desenvolvimento

```bash
uvicorn main:app --reload --port 8000
```

Acesse:
* 🖥️ **Painel Web**: [http://localhost:8000](http://localhost:8000)
* 📑 **Documentação Swagger (OpenAPI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Executando com Docker Compose

Para subir a aplicação completa com **FastAPI + PostgreSQL 16**:

```bash
# Construir e iniciar os containers
docker compose up -d --build

# Visualizar logs
docker compose logs -f api
```

---

## 🧪 Testes Automatizados

Para rodar toda a suíte de testes com **Pytest**:

```bash
pytest tests/ -v
```

Saída esperada:
```plaintext
collected 15 items

tests/test_health.py::test_api_basic_health PASSED                       [  6%]
tests/test_health.py::test_monitored_services_health PASSED              [ 13%]
tests/test_health.py::test_run_on_demand_diagnostic PASSED               [ 20%]
tests/test_tickets.py::test_create_and_list_tickets PASSED               [ 26%]
tests/test_tickets.py::test_update_ticket_status PASSED                  [ 33%]
tests/test_triage.py::test_classify_critical_database_incident PASSED    [ 40%]
tests/test_triage.py::test_classify_auth_password_reset PASSED           [ 46%]
tests/test_triage.py::test_classify_vpn_network PASSED                   [ 53%]
tests/test_triage.py::test_classify_crm_service PASSED                   [ 60%]
tests/test_triage.py::test_classify_hardware_issue PASSED                [ 66%]
tests/test_triage.py::test_classify_general_fallback PASSED              [ 73%]
tests/test_webhook.py::test_webhook_get_verification_success PASSED      [ 80%]
tests/test_webhook.py::test_webhook_get_verification_invalid_token PASSED [ 86%]
tests/test_webhook.py::test_webhook_post_direct_mock PASSED              [ 93%]
tests/test_webhook.py::test_webhook_post_meta_cloud_api_format PASSED    [100%]

======================= 15 passed in 0.85s =======================
```

---

## 📱 Simulador CLI no Terminal

Você pode simular conversas do WhatsApp diretamente no terminal sem custos:

```bash
python scripts/simulate_whatsapp.py
```

Menu interativo:
```plaintext
====================================================================
 🤖 SERVICE DESK WHATSAPP BOT - SIMULADOR INTERATIVO CLI
====================================================================
 Escolha um cenário para simular:
 [1] 🔐 Esqueci minha senha do AD / Usuário bloqueado (Autoatendimento N1)
 [2] 🌐 Não consigo conectar na VPN da empresa (Diagnóstico de Rede N1)
 [3] 🚨 Erro 500 no Banco de Dados / Produção parada! (Incidente Crítico P1)
 [4] 📊 O CRM corporativo está fora do ar? (Diagnóstico de Serviço em Tempo Real)
 [5] 🖥️ Meu segundo monitor não dá sinal de vídeo (Chamado Geral de Hardware)
 [6] ✍️ Digitar mensagem personalizada livre
 [7] 📋 Consultar últimos tickets abertos no banco
 [8] 🩺 Executar diagnóstico geral de servidores corporativos
 [0] 🚪 Sair
```

---

## 📡 Endpoints da API RESTful

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/webhook` | Verificação do token de webhook padrão da Meta (`hub.challenge`). |
| `POST` | `/api/webhook` | Recepção de mensagens do WhatsApp e processamento no Motor de Triagem. |
| `GET` | `/api/tickets` | Listagem de chamados com filtros (status, prioridade, categoria, busca). |
| `GET` | `/api/tickets/{id}` | Detalhes do chamado e histórico completo de mensagens e logs. |
| `POST` | `/api/tickets` | Abertura manual de chamado interno. |
| `PATCH` | `/api/tickets/{id}/status` | Atualização de status com disparo de notificação ao WhatsApp. |
| `DELETE` | `/api/tickets/{id}` | Exclusão de chamado. |
| `GET` | `/api/health` | Healthcheck básico da API. |
| `GET` | `/api/health/services` | Status em tempo real de todos os sistemas corporativos monitorados. |
| `POST` | `/api/health/diagnostics` | Diagnóstico ativo sob demanda para um serviço específico. |
| `GET` | `/api/dashboard/stats` | Métricas de SLA, taxa de auto-resolução N1 e gráficos. |

---

## 🌐 Deploy em Produção

### 🔺 Deploy na Vercel (Preview & Serverless)
O projeto já está configurado com `vercel.json` e `api/index.py`:

🔗 **Preview ao vivo**: [https://servicedesk-bot-w8kr.vercel.app](https://servicedesk-bot-w8kr.vercel.app)

1. Importe o repositório no dashboard da [Vercel](https://vercel.com).
2. O framework preset será detectado automaticamente.
3. Clique em **Deploy** — a aplicação rodará com auto-seeding em SQLite temporário ou PostgreSQL configurado em `DATABASE_URL`.

---

### 🚀 Deploy no Render / Railway / Fly.io
1. Conecte este repositório no [Render](https://render.com) ou [Railway](https://railway.app).
2. Configure o **Start Command**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Configure a URL do webhook no painel do **Meta for Developers**:
   * **Callback URL**: `https://servicedesk-bot-w8kr.vercel.app/api/webhook` (ou do seu servidor)
   * **Verify Token**: O mesmo valor definido em `WHATSAPP_VERIFY_TOKEN`.

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte `LICENSE` para mais informações.
