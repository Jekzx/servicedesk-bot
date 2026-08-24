Arquitetura do Projeto: Service Desk WhatsApp Automation & Diagnostics Bot
Plaintext
servicedesk-bot/
├── app/
│   ├── core/
│   │   ├── config.py             # Variáveis de ambiente (.env) e Settings
│   │   └── database.py           # Conexão SQLAlchemy & SessionLocal
│   ├── models/
│   │   ├── ticket.py             # Entidade Ticket (id, user_phone, category, priority, status)
│   │   ├── log.py                # Histórico de mensagens recebidas e respostas
│   │   └── user.py               # Usuários corporativos e departamentos
│   ├── schemas/
│   │   ├── webhook.py            # Validação do payload do WhatsApp (Pydantic)
│   │   └── ticket.py             # Schemas de criação e atualização de chamados
│   ├── services/
│   │   ├── whatsapp.py           # Envio/recebimento de mensagens e mídias
│   │   ├── triage_engine.py      # Classificação de intenção (VPN, Active Directory, Erro 500, Banco)
│   │   └── auto_fix.py           # Scripts de diagnóstico e auto-remediação de chamados N1
│   ├── routers/
│   │   ├── webhook.py            # POST/GET /api/webhook (Meta API / Twilio)
│   │   ├── tickets.py            # CRUD RESTful para painel interno
│   │   └── health.py             # Healthcheck de serviços monitorados
│   ├── main.py                   # Ponto de entrada FastAPI
├── scripts/
│   └── simulate_whatsapp.py      # CLI interativo para testar o bot sem precisar de conta paga na Meta
├── tests/
│   ├── test_webhook.py           # Testes unitários de recepção de payload
│   └── test_triage.py            # Validação das regras de classificação
├── Dockerfile
├── docker-compose.yml
└── README.md
Roadmap de Desenvolvimento (Passo a Passo)
Fase 1: Setup do Ambiente & Banco com SQLAlchemy
Inicialize o projeto Python com gerenciador de pacotes (Poetry ou pip):

Bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic pydantic-settings python-dotenv pytest httpx
Configure o docker-compose.yml para rodar PostgreSQL 16.

Modele o banco relacional:

Ticket: id (UUID), protocolo, requester_phone, title, description, category (NETWORK, AUTH, DATABASE, HARDWARE), priority (P1 a P4), status (OPEN, RESOLVED, ESCALATED_N2), created_at.

MessageLog: id, ticket_id, sender, payload_raw, media_url, timestamp.

Fase 2: Endpoint de Webhook (WhatsApp API & Mock Receiver)
GET /api/webhook: Verificação de token de webhook padrão da Meta (hub.mode, hub.verify_token, hub.challenge).

POST /api/webhook:

Recepção de mensagens de texto, áudios e capturas de tela enviadas pelo usuário.

Extração do número de telefone e texto via schema Pydantic.

Crie o script scripts/simulate_whatsapp.py que envia requisições POST simuladas para a API local, permitindo testar o fluxo de ponta a ponta sem custos.

Fase 3: Motor de Triagem & Autoatendimento N1
Desenvolva o triage_engine.py para processar a intenção do chamado:

Problemas de Senha/AD: Identifica palavras-chave ("bloqueado", "trocar senha", "login") e responde com instruções padronizadas ou link de reset.

Falhas de Conexão/VPN: Testa conectividade e orienta verificação de DNS/adaptador de rede.

Incidentes Críticos: Se o chamado contiver termos como "banco fora", "erro 500" ou "sistema travado", categoriza automaticamente como P1, gera protocolo no banco e simula alerta para a equipe de plantão.

Fase 4: Auto-Remediação & Checagem de Servidores
Implemente o serviço auto_fix.py:

Função que executa pings e requisições de status em URLs corporativas pré-cadastradas.

Se um usuário pergunta "O CRM está fora do ar?", o bot checa a URL em tempo real e responde se o serviço está operante ou em manutenção antes de abrir um ticket manual.

Fase 5: API REST Interna & Documentação Swagger
GET /api/tickets: Listagem com filtros por status (OPEN, RESOLVED), data e prioridade para consumo do time de suporte.

PATCH /api/tickets/{id}/status: Atualização manual de status com envio de mensagem automática de aviso ao WhatsApp do solicitante.

Valide a documentação automática gerada no Swagger UI (http://localhost:8000/docs).

Fase 6: Testes Automatizados & Deploy
Escreva testes unitários com Pytest e HTTPX testando o webhook, a classificação de palavras-chave e a persistência no PostgreSQL.

Crie o Dockerfile para execução do servidor Uvicorn.

Suba a aplicação no Render, Railway ou Fly.io e insira o link de demonstração no README.

Prompts para Usar no Antigravity
Prompt 1 (Setup Inicial, Modelos e Conexão):

"Crie a estrutura base de uma API FastAPI em Python com SQLAlchemy e Pydantic para um bot de Service Desk. Configure a conexão com PostgreSQL via Docker Compose e crie os modelos 'Ticket' e 'MessageLog' com campos de protocolo, telefone, categoria (enum), prioridade P1-P4 e status."

Prompt 2 (Webhook e Motor de Triagem):

"Implemente o endpoint POST /api/webhook para receber payloads de mensagens do WhatsApp. Crie um serviço 'triage_engine.py' que analisa a mensagem do usuário, classifica a categoria do problema (Rede, Active Directory, Banco de Dados), gera um ticket no banco e retorna uma resposta automática adequada com número de protocolo."

Prompt 3 (Script de Simulação e Healthcheck):

"Crie um script em Python 'simulate_whatsapp.py' com menu interativo no terminal para enviar mensagens simuladas ao endpoint /api/webhook. Adicione também um endpoint de diagnóstico em FastAPI que verifica o status de servidores externos e responde ao bot se a aplicação está online."