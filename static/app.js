/**
 * Service Desk WhatsApp Automation & Diagnostics - Interactive Frontend
 */

let currentSelectedTicketId = null;

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initFilters();
    initChatSimulator();
    initModal();
    initFloatingBotWidget();
    
    // Initial data load
    loadDashboardData();
    loadServicesHealth();

    // Auto-refresh periodically every 30 seconds
    setInterval(() => {
        loadDashboardData(false);
        loadServicesHealth(false);
    }, 30000);

    document.getElementById("refreshDataBtn").addEventListener("click", () => {
        loadDashboardData(true);
        loadServicesHealth(true);
        showToast("Dados atualizados com sucesso!");
    });

    document.getElementById("runAllDiagnosticsBtn").addEventListener("click", () => {
        runFullDiagnostics();
    });
});

// ==========================================
// 1. TABS MANAGEMENT
// ==========================================
function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
            
            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            document.getElementById(targetId).classList.add("active");
        });
    });
}

// ==========================================
// 2. DASHBOARD DATA & TICKETS TABLE
// ==========================================
async function loadDashboardData(showFeedback = false) {
    try {
        // Fetch stats
        const statsRes = await fetch("/api/dashboard/stats");
        if (statsRes.ok) {
            const stats = await statsRes.json();
            renderKPIs(stats);
        }

        // Fetch tickets with current filters
        await fetchAndRenderTickets();

    } catch (err) {
        console.error("Error loading dashboard data:", err);
    }
}

function renderKPIs(stats) {
    document.getElementById("kpiTotalTickets").textContent = stats.total_tickets || 0;
    document.getElementById("kpiAutoResolved").innerHTML = `${stats.resolved_auto_tickets || 0} <span class="metric-sub">(${stats.auto_remediation_rate || 0}%)</span>`;
    document.getElementById("kpiOpenTickets").textContent = stats.open_tickets || 0;
    document.getElementById("kpiCriticalP1").textContent = stats.critical_p1_tickets || 0;
}

async function fetchAndRenderTickets() {
    const search = document.getElementById("searchInput").value.trim();
    const status = document.getElementById("statusFilter").value;
    const priority = document.getElementById("priorityFilter").value;
    const category = document.getElementById("categoryFilter").value;

    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (status) params.append("status", status);
    if (priority) params.append("priority", priority);
    if (category) params.append("category", category);
    params.append("page", "1");
    params.append("page_size", "50");

    const tbody = document.getElementById("ticketsTableBody");

    try {
        const res = await fetch(`/api/tickets?${params.toString()}`);
        if (!res.ok) throw new Error("Failed to fetch tickets");
        const data = await res.json();
        
        if (!data.items || data.items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="loading-td">Nenhum chamado encontrado com os filtros selecionados.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.items.map(ticket => `
            <tr>
                <td><strong class="font-mono text-primary">${ticket.protocol}</strong></td>
                <td>
                    <div style="font-weight:600;">${ticket.requester_name}</div>
                    <div style="font-size:0.725rem; color:var(--text-muted);">${ticket.requester_phone}</div>
                </td>
                <td><span class="badge" style="background:rgba(255,255,255,0.06);">${formatCategory(ticket.category)}</span></td>
                <td>${getPriorityBadge(ticket.priority)}</td>
                <td>${getStatusBadge(ticket.status)}</td>
                <td style="font-size:0.75rem; color:var(--text-secondary);">${formatDate(ticket.created_at)}</td>
                <td style="text-align: center;">
                    <button class="action-icon-btn" onclick="openTicketModal('${ticket.id}')">
                        Ver & Gerenciar
                    </button>
                </td>
            </tr>
        `).join("");

    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="loading-td text-red">Erro ao carregar chamados.</td></tr>`;
    }
}

function initFilters() {
    const inputs = ["searchInput", "statusFilter", "priorityFilter", "categoryFilter"];
    inputs.forEach(id => {
        document.getElementById(id).addEventListener("input", () => {
            fetchAndRenderTickets();
        });
    });
}

function getPriorityBadge(priority) {
    const map = {
        "P1": `<span class="badge badge-p1">🚨 P1 - Crítico</span>`,
        "P2": `<span class="badge badge-p2">⚠️ P2 - Alto</span>`,
        "P3": `<span class="badge badge-p3">🟡 P3 - Médio</span>`,
        "P4": `<span class="badge badge-p4">🟢 P4 - Baixo</span>`
    };
    return map[priority] || `<span class="badge">${priority}</span>`;
}

function getStatusBadge(status) {
    const map = {
        "OPEN": `<span class="status-badge status-open">🟡 Aberto</span>`,
        "IN_PROGRESS": `<span class="status-badge status-progress">🔵 Em Andamento</span>`,
        "RESOLVED_AUTO": `<span class="status-badge status-resolved-auto">⚡ Auto-Resolvido</span>`,
        "RESOLVED": `<span class="status-badge status-resolved">✅ Resolvido</span>`,
        "ESCALATED_N2": `<span class="status-badge status-escalated">🚀 Escalado N2</span>`
    };
    return map[status] || `<span class="status-badge">${status}</span>`;
}

function formatCategory(cat) {
    const map = {
        "AUTH": "Active Directory / Senha",
        "NETWORK": "Rede & VPN",
        "DATABASE": "Banco de Dados",
        "ERP_CRM": "ERP & CRM",
        "HARDWARE": "Hardware",
        "OTHER": "Geral"
    };
    return map[cat] || cat;
}

function formatDate(isoStr) {
    if (!isoStr) return "-";
    const d = new Date(isoStr);
    return d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

// ==========================================
// 3. INFRASTRUCTURE HEALTH MONITOR
// ==========================================
async function loadServicesHealth(showNotification = false) {
    const container = document.getElementById("servicesGridContainer");
    try {
        const res = await fetch("/api/health/services");
        if (!res.ok) return;
        const data = await res.json();

        // Update top global status
        const globalStatusBadge = document.getElementById("systemGlobalStatus");
        const globalStatusText = document.getElementById("systemStatusText");
        if (data.outage_count > 0) {
            globalStatusBadge.style.borderColor = "rgba(239, 68, 68, 0.4)";
            globalStatusBadge.style.color = "#F87171";
            globalStatusText.textContent = `${data.outage_count} Serviço(s) com Incidente`;
        } else {
            globalStatusBadge.style.borderColor = "rgba(16, 185, 129, 0.3)";
            globalStatusBadge.style.color = "#34D399";
            globalStatusText.textContent = "Sistemas 100% Operacionais";
        }

        container.innerHTML = data.services.map(s => {
            const isOp = s.status === "OPERATIONAL";
            const statusClass = isOp ? "status-resolved-auto" : "badge-p1";
            const statusLabel = isOp ? "🟢 Operacional" : "🔴 Fora do Ar";
            return `
                <div class="service-card">
                    <div class="service-top">
                        <span class="service-name">${s.name}</span>
                        <span class="status-badge ${statusClass}">${statusLabel}</span>
                    </div>
                    <p class="service-desc">${s.description || s.endpoint_url}</p>
                    <div class="service-meta">
                        <span>Latência: <strong class="service-latency">${s.latency_ms} ms</strong></span>
                        <button class="action-icon-btn" onclick="testSingleService('${s.service_key}')">Testar</button>
                    </div>
                </div>
            `;
        }).join("");

    } catch (err) {
        console.error("Error loading services health:", err);
    }
}

async function testSingleService(serviceKey) {
    try {
        showToast(`Testando ${serviceKey.toUpperCase()}...`);
        const res = await fetch("/api/health/diagnostics", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ target: serviceKey })
        });
        if (res.ok) {
            const data = await res.json();
            showToast(`${data.target.toUpperCase()}: ${data.message}`);
            loadServicesHealth();
        }
    } catch (e) {
        showToast("Erro ao testar serviço.", "error");
    }
}

async function runFullDiagnostics() {
    showToast("Executando diagnóstico completo de infraestrutura...");
    await loadServicesHealth();
    showToast("Diagnóstico finalizado!");
}

// ==========================================
// 4. FLOATING BOT WIDGET INTERACTION
// ==========================================
function initFloatingBotWidget() {
    const fab = document.getElementById("floatingBotFab");
    const widget = document.getElementById("whatsappWidget");
    const closeBtn = document.getElementById("closeBotWidgetBtn");
    const navBtn = document.getElementById("openBotNavBtn");

    function openWidget() {
        widget.classList.add("open");
        const chatInput = document.getElementById("chatInput");
        setTimeout(() => chatInput.focus(), 200);
    }

    function closeWidget() {
        widget.classList.remove("open");
    }

    function toggleWidget() {
        if (widget.classList.contains("open")) {
            closeWidget();
        } else {
            openWidget();
        }
    }

    if (fab) fab.addEventListener("click", toggleWidget);
    if (navBtn) navBtn.addEventListener("click", openWidget);
    if (closeBtn) closeBtn.addEventListener("click", closeWidget);
}

// ==========================================
// 5. WHATSAPP WEB SIMULATOR
// ==========================================
function initChatSimulator() {
    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");
    const clearBtn = document.getElementById("clearChatBtn");

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;

        const name = document.getElementById("simUserName").value.trim() || "Colaborador";
        const phone = document.getElementById("simUserPhone").value.trim() || "551199887766";

        appendMessage(text, "outgoing", name);
        chatInput.value = "";

        // Show typing indicator
        const typingId = showTypingIndicator();

        try {
            const payload = {
                phone: phone,
                name: name,
                message: text,
                message_type: "text"
            };

            const res = await fetch("/api/webhook", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            removeTypingIndicator(typingId);

            if (res.ok) {
                const data = await res.json();
                appendMessage(data.reply_message, "incoming", "Bot N1 Service Desk");
                // Refresh full tickets table & KPIs in background
                loadDashboardData();
            } else {
                appendMessage("❌ Erro ao comunicar com a API do Service Desk.", "incoming");
            }
        } catch (err) {
            removeTypingIndicator(typingId);
            appendMessage("❌ Falha de rede ao enviar mensagem.", "incoming");
        }
    });

    // Preset chips
    document.querySelectorAll(".quick-tag").forEach(tag => {
        tag.addEventListener("click", () => {
            const msg = tag.getAttribute("data-msg");
            chatInput.value = msg;
            chatForm.dispatchEvent(new Event("submit"));
        });
    });

    clearBtn.addEventListener("click", () => {
        document.getElementById("chatMessages").innerHTML = `
            <div class="wa-msg-bubble incoming">
                <div class="wa-msg-content">
                    👋 Chat limpo. Digite uma nova mensagem para iniciar atendimento.
                </div>
                <span class="wa-msg-time">Agora</span>
            </div>
        `;
    });
}

function appendMessage(text, direction, sender = "") {
    const chatContainer = document.getElementById("chatMessages");
    const bubble = document.createElement("div");
    bubble.className = `wa-msg-bubble ${direction}`;

    const timeStr = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    
    // Format bold, markdown and code in message
    let formattedText = text
        .replace(/\n/g, "<br>")
        .replace(/\*(.*?)\*/g, "<b>$1</b>")
        .replace(/`(.*?)`/g, "<code style='background:rgba(0,0,0,0.3);padding:2px 4px;border-radius:3px;'>$1</code>")
        .replace(/_(.*?)_/g, "<i>$1</i>");

    bubble.innerHTML = `
        <div class="wa-msg-content">${formattedText}</div>
        <span class="wa-msg-time">${timeStr}</span>
    `;

    chatContainer.appendChild(bubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTypingIndicator() {
    const chatContainer = document.getElementById("chatMessages");
    const id = "typing-" + Date.now();
    const bubble = document.createElement("div");
    bubble.id = id;
    bubble.className = "wa-msg-bubble incoming";
    bubble.innerHTML = `<span style="font-style:italic;color:var(--wa-text-muted);">digitando...</span>`;
    chatContainer.appendChild(bubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// ==========================================
// 6. TICKET DETAILS MODAL & STATUS UPDATE
// ==========================================
function initModal() {
    const modal = document.getElementById("ticketModal");
    const closeBtn = document.getElementById("closeModalBtn");
    const statusForm = document.getElementById("updateStatusForm");

    closeBtn.addEventListener("click", () => {
        modal.classList.remove("active");
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.classList.remove("active");
    });

    statusForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!currentSelectedTicketId) return;

        const newStatus = document.getElementById("newStatusSelect").value;
        const notify = document.getElementById("notifyRequesterCheckbox").checked;
        const notes = document.getElementById("resolutionNotesInput").value.trim();

        try {
            const res = await fetch(`/api/tickets/${currentSelectedTicketId}/status`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    status: newStatus,
                    resolution_notes: notes || null,
                    notify_requester: notify
                })
            });

            if (res.ok) {
                showToast("Status do chamado atualizado com sucesso!");
                modal.classList.remove("active");
                loadDashboardData();
            } else {
                showToast("Erro ao atualizar chamado.", "error");
            }
        } catch (err) {
            showToast("Erro de conexão.", "error");
        }
    });
}

async function openTicketModal(ticketId) {
    currentSelectedTicketId = ticketId;
    const modal = document.getElementById("ticketModal");

    try {
        const res = await fetch(`/api/tickets/${ticketId}`);
        if (!res.ok) throw new Error("Ticket not found");
        const ticket = await res.json();

        document.getElementById("modalTicketProtocol").textContent = ticket.protocol;
        document.getElementById("modalTicketTitle").textContent = ticket.title;
        document.getElementById("modalRequesterName").textContent = ticket.requester_name;
        document.getElementById("modalRequesterPhone").textContent = ticket.requester_phone;
        document.getElementById("modalDescription").textContent = ticket.description;
        document.getElementById("newStatusSelect").value = ticket.status;
        document.getElementById("resolutionNotesInput").value = ticket.resolution_notes || "";

        // Badges
        document.getElementById("modalCategoryBadge").textContent = formatCategory(ticket.category);
        document.getElementById("modalPriorityBadge").innerHTML = getPriorityBadge(ticket.priority);

        // Logs
        const logsList = document.getElementById("modalLogsList");
        if (ticket.messages && ticket.messages.length > 0) {
            logsList.innerHTML = ticket.messages.map(m => `
                <div class="log-item ${m.direction.toLowerCase()}">
                    <div class="log-header">
                        <strong>${m.sender_name || m.sender_phone} (${m.direction})</strong>
                        <span>${formatDate(m.timestamp)}</span>
                    </div>
                    <div>${m.content || "[Mídia/Payload]"}</div>
                </div>
            `).join("");
        } else {
            logsList.innerHTML = `<div style="color:var(--text-muted);font-size:0.8rem;">Nenhuma mensagem registrada para este chamado.</div>`;
        }

        modal.classList.add("active");

    } catch (err) {
        showToast("Falha ao abrir detalhes do chamado.", "error");
    }
}

// ==========================================
// 7. TOAST NOTIFICATIONS
// ==========================================
function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `<span>${type === "error" ? "❌" : "🔔"}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}
