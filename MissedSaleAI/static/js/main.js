/**
 * MissedSale AI - Client Side Controller & Interactive Agent Loop
 * Powers Chart.js analytics, dynamic stepper animations, and async agent execution.
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Initialize Dashboard Charts if chart canvases exist
    initCharts();

    // 2. Setup Auto-dismissing Alerts
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

/**
 * Initializes Chart.js graphs on Dashboard and Analytics pages.
 */
function initCharts() {
    // 1. Lost Sales vs Recovered Revenue Trend Chart
    const trendCanvas = document.getElementById("salesTrendChart");
    if (trendCanvas && window.chartsData) {
        const ctx = trendCanvas.getContext("2d");
        new Chart(ctx, {
            type: "line",
            data: {
                labels: window.chartsData.time_labels,
                datasets: [
                    {
                        label: "Lost Sales Detected",
                        data: window.chartsData.lost_sales_trend,
                        borderColor: "#ef4444",
                        backgroundColor: "rgba(239, 68, 68, 0.1)",
                        tension: 0.35,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: "#ef4444"
                    },
                    {
                        label: "Recovered Revenue ($)",
                        data: window.chartsData.recovered_revenue_trend,
                        borderColor: "#10b981",
                        backgroundColor: "rgba(16, 185, 129, 0.1)",
                        tension: 0.35,
                        fill: true,
                        yAxisID: "y1",
                        pointRadius: 4,
                        pointBackgroundColor: "#10b981"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: "#94a3b8", font: { family: "Inter", size: 12 } }
                    },
                    tooltip: {
                        mode: "index",
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#64748b" }
                    },
                    y: {
                        type: "linear",
                        display: true,
                        position: "left",
                        title: { display: true, text: "Lost Sales Count", color: "#64748b" },
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#64748b", stepSize: 1 }
                    },
                    y1: {
                        type: "linear",
                        display: true,
                        position: "right",
                        title: { display: true, text: "Recovered ($)", color: "#10b981" },
                        grid: { drawOnChartArea: false },
                        ticks: { color: "#10b981" }
                    }
                }
            }
        });
    }

    // 2. Priority Distribution Doughnut Chart
    const priorityCanvas = document.getElementById("priorityDoughnutChart");
    if (priorityCanvas && window.chartsData) {
        const ctx = priorityCanvas.getContext("2d");
        new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: window.chartsData.priority_distribution.labels,
                datasets: [{
                    data: window.chartsData.priority_distribution.values,
                    backgroundColor: [
                        "rgba(239, 68, 68, 0.8)",
                        "rgba(245, 158, 11, 0.8)",
                        "rgba(148, 163, 184, 0.8)"
                    ],
                    borderColor: "#131b2e",
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#94a3b8", padding: 16 }
                    }
                }
            }
        });
    }

    // 3. Pipeline Status Bar Chart
    const statusCanvas = document.getElementById("pipelineStatusBarChart");
    if (statusCanvas && window.chartsData) {
        const ctx = statusCanvas.getContext("2d");
        new Chart(ctx, {
            type: "bar",
            data: {
                labels: window.chartsData.status_distribution.labels,
                datasets: [{
                    label: "Opportunities",
                    data: window.chartsData.status_distribution.values,
                    backgroundColor: "#6366f1",
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: "#64748b" }
                    },
                    y: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#64748b", stepSize: 1 }
                    }
                }
            }
        });
    }
}

/**
 * Runs the autonomous agent for a specific customer.
 * Animates the 7-step visual stepper:
 * OBSERVING -> ANALYZING -> PREDICTING -> DECIDING -> ACTING -> MONITORING -> COMPLETED
 */
async function runAgentForCustomer(customerId) {
    const btn = document.getElementById(`runAgentBtn-${customerId}`) || document.getElementById("globalRunAgentBtn");
    const stepperContainer = document.getElementById("agentStepperContainer");
    const executionLogs = document.getElementById("executionLogsContainer");
    const statusText = document.getElementById("agentLiveStatusText");

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Agent Running...`;
    }

    if (stepperContainer) {
        stepperContainer.classList.remove("d-none");
    }
    if (executionLogs) {
        executionLogs.innerHTML = `<div class="p-3 text-muted"><span class="spinner-border spinner-border-sm me-2 text-primary"></span>Initiating autonomous perception cycle...</div>`;
    }

    const steps = ["step-observe", "step-analyze", "step-predict", "step-decide", "step-act", "step-monitor", "step-adapt"];

    function setStep(stepIndex) {
        steps.forEach((s, idx) => {
            const el = document.getElementById(s);
            if (el) {
                if (idx < stepIndex) {
                    el.className = "step-item completed";
                } else if (idx === stepIndex) {
                    el.className = "step-item active";
                } else {
                    el.className = "step-item";
                }
            }
        });
    }

    try {
        setStep(0);
        if (statusText) statusText.innerText = "Observing customer browsing and shopping cart activity...";
        await sleep(600);

        setStep(1);
        if (statusText) statusText.innerText = "Extracting session features and calculating customer lifetime value...";
        await sleep(600);

        setStep(2);
        if (statusText) statusText.innerText = "Querying Random Forest & Logistic Regression ML models...";

        // Execute API call
        const response = await fetch(`/api/agent/run/${customerId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
        const result = await response.json();

        setStep(3);
        if (statusText) statusText.innerText = "Synthesizing multi-factor signals & formulating autonomous decision...";
        await sleep(700);

        setStep(4);
        if (statusText) statusText.innerText = "Executing tools (CRM Opportunity / Resend Email Dispatch)...";
        await sleep(700);

        setStep(5);
        if (statusText) statusText.innerText = "Monitoring communication outcome and order verification...";
        await sleep(600);

        setStep(6);
        if (statusText) statusText.innerText = "Adapting strategy and recording actions to persistent memory...";
        await sleep(500);

        // Mark all completed
        steps.forEach(s => {
            const el = document.getElementById(s);
            if (el) el.className = "step-item completed";
        });

        if (statusText) statusText.innerText = `Autonomous cycle completed: ${result.recommended_action} (${result.priority} Priority)`;

        // Render full trace
        if (executionLogs && result.trace) {
            let html = `<div class="card bg-card border-0 mb-3"><div class="card-body p-3">`;
            html += `<div class="d-flex align-items-center justify-content-between mb-3 border-bottom pb-2">
                        <span class="badge ${result.priority === 'HIGH' ? 'badge-priority-high' : (result.priority === 'MEDIUM' ? 'badge-priority-medium' : 'badge-priority-low')}">${result.priority} PRIORITY</span>
                        <strong class="text-white">${result.recommended_action}</strong>
                     </div>`;
            html += `<div class="mb-3 text-light" style="font-size: 13px; line-height: 1.6;"><i class="fas fa-brain text-primary me-2"></i><strong>Agent Reasoning:</strong> ${result.reasoning}</div>`;
            html += `<h6 class="text-muted text-uppercase font-mono mb-2" style="font-size: 11px;">Autonomous Execution Trace</h6>`;
            html += `<ul class="list-unstyled mb-0">`;
            result.trace.forEach(t => {
                html += `<li class="d-flex align-items-start gap-2 mb-2 p-2 rounded" style="background: rgba(255,255,255,0.02); border-left: 3px solid var(--primary);">
                            <span class="badge bg-primary text-white font-mono" style="font-size: 10px;">${t.step}</span>
                            <div class="flex-grow-1">
                                <div class="text-white font-weight-bold" style="font-size: 12px;">${t.title}</div>
                                <div class="text-muted" style="font-size: 12px;">${t.detail}</div>
                            </div>
                            <span class="text-muted font-mono" style="font-size: 10px;">${t.timestamp}</span>
                         </li>`;
            });
            html += `</ul></div></div>`;
            executionLogs.innerHTML = html;
        }

        // Show Success Toast
        showToast("Autonomous Agent Cycle Finished", `Successfully processed Customer #${customerId}. Action: ${result.recommended_action}`);

    } catch (err) {
        console.error("Agent execution error:", err);
        if (statusText) statusText.innerText = "Error executing agent cycle. Check console.";
        if (executionLogs) executionLogs.innerHTML = `<div class="alert alert-danger p-2 m-2">Execution error: ${err.message}</div>`;
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="fas fa-play me-1"></i> Run Agent`;
        }
    }
}

/**
 * Runs batch cycle for multiple opportunities.
 */
async function runBatchAgent(limit = 5) {
    const btn = document.getElementById("batchAgentBtn");
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Running Batch...`;
    }

    try {
        const resp = await fetch("/api/agent/run-batch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ limit: limit })
        });
        const data = await resp.json();
        showToast("Batch Cycle Complete", `Processed ${data.processed_count} pending opportunities autonomously.`);
        setTimeout(() => window.location.reload(), 1200);
    } catch (err) {
        alert("Batch error: " + err.message);
    } finally {
        if (btn) btn.disabled = false;
    }
}

/**
 * Quick Opportunity Action (Send Email, Mark Recovered, Close)
 */
async function triggerOpportunityAction(oppId, actionType, amount = null) {
    try {
        const payload = { action_type: actionType };
        if (amount) payload.amount = amount;

        const resp = await fetch(`/api/opportunities/${oppId}/action`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (data.success) {
            showToast("Opportunity Updated", data.message);
            setTimeout(() => window.location.reload(), 800);
        } else {
            alert(data.error || data.message || "Action failed");
        }
    } catch (e) {
        alert("Action error: " + e.message);
    }
}

// -------------------------------------------------------------
// Real Resend Email Compose, Edit & Dispatch Controller (Sections 6, 7, 8, 12)
// -------------------------------------------------------------
window.sendEmailModalState = {
    mode: 'preview', // 'preview' or 'edit'
    to: '',
    customer_name: 'Valued Customer',
    product_name: 'Premium Laptop',
    product_price: '75,000',
    subject: '',
    message: '',
    opportunity_id: null,
    customer_id: null,
    is_user_edited: false
};
window.crmCustomersCache = null;

// Backwards compatibility alias
window.currentEmailContext = window.sendEmailModalState;

function openTestEmailModal() {
    openSendEmailModal({ to: 'friend@gmail.com' });
}

function submitTestEmailForPreview() {
    openSendEmailModal();
}

function openOpportunityEmailPreview(oppId, email, name, product, price, custId) {
    openSendEmailModal({
        opportunity_id: oppId,
        to: email,
        customer_name: name,
        product_name: product,
        product_price: price,
        customer_id: custId
    });
}

async function openSendEmailModal(params = {}) {
    const state = window.sendEmailModalState;
    state.opportunity_id = params.opportunity_id || null;
    state.customer_id = params.customer_id || null;
    state.to = (params.to || params.email || '').trim();
    state.customer_name = params.customer_name || params.name || 'Valued Customer';
    state.product_name = params.product_name || params.product || 'Premium Laptop';
    state.product_price = params.product_price != null ? String(params.product_price) : '75,000';
    state.is_user_edited = false;

    // Reset Result Box
    const resultBox = document.getElementById('sendResultBox');
    if (resultBox) {
        resultBox.className = 'd-none mt-3';
        resultBox.innerHTML = '';
    }

    // Reset Send Button
    const sendBtn = document.getElementById('sendRealEmailBtn');
    if (sendBtn) {
        sendBtn.disabled = false;
        sendBtn.className = 'btn btn-primary-saas px-4';
        sendBtn.innerHTML = '<i class="fas fa-paper-plane me-1"></i> Send Real Email';
    }

    // Populate Hero Customer Email field (Enter e-mail of customer)
    const emailInput = document.getElementById('modalCustomerEmail');
    if (emailInput) {
        emailInput.value = state.to;
    }
    const nameInput = document.getElementById('modalCustomerName');
    if (nameInput) nameInput.value = state.customer_name;
    const prodInput = document.getElementById('modalProductName');
    if (prodInput) prodInput.value = state.product_name;
    const priceInput = document.getElementById('modalProductPrice');
    if (priceInput) priceInput.value = state.product_price;

    const emailFeedback = document.getElementById('emailValidationFeedback');
    if (emailFeedback) emailFeedback.innerText = '';
    const matchBadge = document.getElementById('modalCustomerMatchBadge');
    if (matchBadge) matchBadge.style.display = 'none';

    // Set default mode to preview
    setComposeMode('preview');

    // Show modal
    const modalEl = document.getElementById('sendEmailModal');
    if (modalEl) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
        if (!state.to && emailInput) {
            setTimeout(() => emailInput.focus(), 350);
        }
    }

    // Fetch and populate customer dropdown if not cached
    loadCrmCustomersDropdown();

    // Fetch initial dynamic preview
    await refreshGeneratedTemplate(false);
}

function setComposeMode(mode) {
    const state = window.sendEmailModalState;
    state.mode = mode;

    const previewContainer = document.getElementById('composePreviewContainer');
    const editContainer = document.getElementById('composeEditContainer');
    const btnPreview = document.getElementById('btnPreviewMode');
    const btnEdit = document.getElementById('btnEditEmail');
    const statusBadge = document.getElementById('composeModeStatusBadge');
    const footerEditToggleBtn = document.getElementById('footerEditToggleBtn');

    const subjectInput = document.getElementById('modalEmailSubjectInput');
    const bodyTextarea = document.getElementById('modalEmailBodyTextarea');
    const previewSubject = document.getElementById('previewSubjectDisplay');
    const previewBody = document.getElementById('previewMessageBody');

    if (mode === 'edit') {
        // Sync preview text to edit inputs
        if (subjectInput && !state.is_user_edited) {
            subjectInput.value = state.subject || '';
        }
        if (bodyTextarea && !state.is_user_edited) {
            bodyTextarea.value = state.message || '';
        }

        if (previewContainer) previewContainer.classList.add('d-none');
        if (editContainer) editContainer.classList.remove('d-none');

        if (btnEdit) {
            btnEdit.className = 'btn btn-primary-saas';
        }
        if (btnPreview) {
            btnPreview.className = 'btn btn-secondary-saas';
        }
        if (statusBadge) {
            statusBadge.className = 'badge bg-primary font-mono';
            statusBadge.innerText = 'EDITING MODE';
        }
        if (footerEditToggleBtn) {
            footerEditToggleBtn.innerHTML = '<i class="fas fa-eye me-1"></i> Preview Email';
        }
        if (subjectInput) subjectInput.focus();

    } else {
        // Mode is preview: sync edit inputs to state and preview display
        if (subjectInput && subjectInput.value.trim()) {
            state.subject = subjectInput.value.trim();
        }
        if (bodyTextarea && bodyTextarea.value.trim()) {
            state.message = bodyTextarea.value.trim();
        }

        if (previewSubject) previewSubject.innerText = state.subject || 'Recovery Email';
        if (previewBody) previewBody.innerText = state.message || 'Loading email content...';

        if (previewContainer) previewContainer.classList.remove('d-none');
        if (editContainer) editContainer.classList.add('d-none');

        if (btnEdit) {
            btnEdit.className = 'btn btn-outline-primary';
        }
        if (btnPreview) {
            btnPreview.className = 'btn btn-secondary-saas';
        }
        if (statusBadge) {
            statusBadge.className = 'badge bg-secondary font-mono';
            statusBadge.innerText = 'PREVIEW MODE';
        }
        if (footerEditToggleBtn) {
            footerEditToggleBtn.innerHTML = '<i class="fas fa-edit me-1"></i> Edit Email';
        }
    }
}

function toggleEditEmailMode() {
    if (window.sendEmailModalState.mode === 'edit') {
        setComposeMode('preview');
    } else {
        setComposeMode('edit');
    }
}

async function refreshGeneratedTemplate(forceRegenerate = false) {
    const state = window.sendEmailModalState;
    const toEmail = document.getElementById('modalCustomerEmail')?.value.trim() || state.to || 'friend@gmail.com';
    const name = document.getElementById('modalCustomerName')?.value.trim() || state.customer_name || 'Valued Customer';
    const product = document.getElementById('modalProductName')?.value.trim() || state.product_name || 'Premium Laptop';
    const price = document.getElementById('modalProductPrice')?.value.trim() || state.product_price || '75,000';

    const previewSubject = document.getElementById('previewSubjectDisplay');
    const previewBody = document.getElementById('previewMessageBody');
    const previewTo = document.getElementById('previewToDisplay');
    const previewFrom = document.getElementById('previewFromDisplay');
    const modeBadge = document.getElementById('composeModalModeBadge');
    const subjectInput = document.getElementById('modalEmailSubjectInput');
    const bodyTextarea = document.getElementById('modalEmailBodyTextarea');

    if (previewTo) previewTo.innerText = toEmail || 'friend@gmail.com';

    // If already edited by user and not forced regenerate, keep user changes
    if (state.is_user_edited && !forceRegenerate) {
        return;
    }

    if (!state.subject || forceRegenerate) {
        if (previewSubject) previewSubject.innerText = 'Generating recovery copy...';
        if (previewBody) previewBody.innerText = 'Drafting personalized outreach...';

        try {
            const resp = await fetch('/api/email/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    to: toEmail,
                    customer_name: name,
                    product_name: product,
                    product_price: price
                })
            });
            const data = await resp.json();

            state.to = data.to || toEmail;
            state.subject = data.subject;
            state.message = data.message;
            if (forceRegenerate) state.is_user_edited = false;

            if (previewSubject) previewSubject.innerText = data.subject;
            if (previewBody) previewBody.innerText = data.message;
            if (previewFrom && data.from) previewFrom.innerText = `MissedSale AI <${data.from}>`;
            if (subjectInput) subjectInput.value = data.subject;
            if (bodyTextarea) bodyTextarea.value = data.message;

            if (modeBadge) {
                if (data.mode === 'LIVE') {
                    modeBadge.className = 'badge bg-success font-mono';
                    modeBadge.innerHTML = '<i class="fas fa-check-circle me-1"></i>Live Resend API Connected';
                } else {
                    modeBadge.className = 'badge bg-warning text-dark font-mono';
                    modeBadge.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Demo Mode: Simulation';
                }
            }
        } catch (e) {
            console.error('Error generating email preview:', e);
        }
    }
}

function handleCustomerEmailChange(val) {
    const email = (val || '').trim();
    const state = window.sendEmailModalState;
    state.to = email;

    const previewTo = document.getElementById('previewToDisplay');
    if (previewTo) previewTo.innerText = email || 'friend@gmail.com';

    // Check against CRM customer list
    if (window.crmCustomersCache && Array.isArray(window.crmCustomersCache)) {
        const matched = window.crmCustomersCache.find(c => c.email && c.email.toLowerCase() === email.toLowerCase());
        const matchBadge = document.getElementById('modalCustomerMatchBadge');
        if (matched) {
            state.customer_id = matched.id;
            state.customer_name = matched.name;
            const nameInput = document.getElementById('modalCustomerName');
            if (nameInput) nameInput.value = matched.name;
            if (matchBadge) {
                matchBadge.style.display = 'inline-block';
                matchBadge.innerText = `Matched: ${matched.name}`;
            }
        } else {
            if (matchBadge) matchBadge.style.display = 'none';
        }
    }
}

function onContextFieldChange() {
    const nameInput = document.getElementById('modalCustomerName');
    const prodInput = document.getElementById('modalProductName');
    const priceInput = document.getElementById('modalProductPrice');

    if (nameInput) window.sendEmailModalState.customer_name = nameInput.value.trim();
    if (prodInput) window.sendEmailModalState.product_name = prodInput.value.trim();
    if (priceInput) window.sendEmailModalState.product_price = priceInput.value.trim();
}

async function loadCrmCustomersDropdown() {
    const listEl = document.getElementById('modalCustomerDropdownList');
    if (!listEl) return;

    if (window.crmCustomersCache) {
        renderCustomerDropdownItems(window.crmCustomersCache);
        return;
    }

    try {
        const resp = await fetch('/api/customers');
        const data = await resp.json();
        if (Array.isArray(data)) {
            window.crmCustomersCache = data;
            renderCustomerDropdownItems(data);
        }
    } catch (e) {
        console.error('Error loading CRM customers:', e);
    }
}

function renderCustomerDropdownItems(customers) {
    const listEl = document.getElementById('modalCustomerDropdownList');
    if (!listEl) return;

    let html = '<li><h6 class="dropdown-header">Select from CRM:</h6></li>';
    if (!customers || customers.length === 0) {
        html += '<li><span class="dropdown-item text-muted">No customers found</span></li>';
    } else {
        customers.slice(0, 15).forEach(c => {
            const safeName = (c.name || 'Customer').replace(/'/g, "\\'");
            const safeEmail = (c.email || '').replace(/'/g, "\\'");
            html += `<li>
                <a class="dropdown-item d-flex justify-content-between align-items-center py-2" href="javascript:void(0)" onclick="selectCustomerFromPicker('${safeEmail}', '${safeName}', ${c.id})">
                    <div>
                        <div class="fw-bold text-white">${c.name}</div>
                        <div class="text-muted font-mono" style="font-size: 11px;">${c.email}</div>
                    </div>
                    <span class="badge bg-dark border border-secondary text-info ms-2">${c.customer_value || 'CRM'}</span>
                </a>
            </li>`;
        });
    }
    listEl.innerHTML = html;
}

function selectCustomerFromPicker(email, name, custId) {
    const emailInput = document.getElementById('modalCustomerEmail');
    if (emailInput) emailInput.value = email;

    const nameInput = document.getElementById('modalCustomerName');
    if (nameInput) nameInput.value = name;

    const state = window.sendEmailModalState;
    state.to = email;
    state.customer_name = name;
    state.customer_id = custId;

    const matchBadge = document.getElementById('modalCustomerMatchBadge');
    if (matchBadge) {
        matchBadge.style.display = 'inline-block';
        matchBadge.innerText = `Matched: ${name}`;
    }

    const previewTo = document.getElementById('previewToDisplay');
    if (previewTo) previewTo.innerText = email;

    refreshGeneratedTemplate(true);
}

// Track user edit in textarea/inputs
document.addEventListener('input', function(e) {
    if (e.target && (e.target.id === 'modalEmailSubjectInput' || e.target.id === 'modalEmailBodyTextarea')) {
        window.sendEmailModalState.is_user_edited = true;
    }
});

async function executeRealEmailSend() {
    const state = window.sendEmailModalState || {};
    const emailInput = document.getElementById('modalCustomerEmail');
    const toEmail = emailInput ? emailInput.value.trim() : (state.to || '').trim();

    const sendBtn = document.getElementById('sendRealEmailBtn');
    const resultBox = document.getElementById('sendResultBox');

    // Validation for "Enter e-mail of customer"
    if (!toEmail) {
        alert('Please enter the customer e-mail address.');
        if (emailInput) emailInput.focus();
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(toEmail)) {
        alert('Please enter a valid e-mail address (e.g. friend@gmail.com).');
        if (emailInput) emailInput.focus();
        return;
    }

    // Pull subject and body (from inputs if in edit mode, or from state/preview)
    const subjectInput = document.getElementById('modalEmailSubjectInput');
    const bodyTextarea = document.getElementById('modalEmailBodyTextarea');

    let finalSubject = state.subject;
    let finalMessage = state.message;

    if (subjectInput && subjectInput.value.trim()) {
        finalSubject = subjectInput.value.trim();
    }
    if (bodyTextarea && bodyTextarea.value.trim()) {
        finalMessage = bodyTextarea.value.trim();
    }

    const nameInput = document.getElementById('modalCustomerName');
    const prodInput = document.getElementById('modalProductName');
    const priceInput = document.getElementById('modalProductPrice');

    const customerName = nameInput ? nameInput.value.trim() : (state.customer_name || 'Valued Customer');
    const productName = prodInput ? prodInput.value.trim() : (state.product_name || 'Premium Laptop');
    const productPrice = priceInput ? priceInput.value.trim() : (state.product_price || '75,000');

    const payload = {
        to: toEmail,
        customer_name: customerName,
        product_name: productName,
        product_price: productPrice,
        subject: finalSubject,
        message: finalMessage,
        opportunity_id: state.opportunity_id,
        customer_id: state.customer_id
    };

    // Keep context updated
    window.currentEmailContext = payload;

    // In-flight spinner
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Sending real email...';
    }

    if (resultBox) {
        resultBox.className = 'p-3 rounded mb-3 text-info font-mono';
        resultBox.style.background = 'rgba(14, 165, 233, 0.1)';
        resultBox.style.border = '1px solid rgba(14, 165, 233, 0.3)';
        resultBox.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Connecting to Resend API & dispatching to ' + toEmail + '...';
    }

    try {
        const resp = await fetch('/api/email/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await resp.json();

        if (data.success && data.status === 'SENT') {
            if (resultBox) {
                resultBox.className = 'p-3 rounded mb-3 text-success';
                resultBox.style.background = 'rgba(16, 185, 129, 0.1)';
                resultBox.style.border = '1px solid rgba(16, 185, 129, 0.4)';
                resultBox.innerHTML = `
                    <div class="fw-bold fs-6 mb-2">
                        <i class="fas fa-check-circle me-1"></i>✓ Email sent successfully
                    </div>
                    <div class="row g-1 text-light" style="font-size: 13px;">
                        <div class="col-sm-4 text-muted">Recipient:</div>
                        <div class="col-sm-8 font-mono text-white">${data.recipient || toEmail}</div>
                        <div class="col-sm-4 text-muted">Status:</div>
                        <div class="col-sm-8"><span class="badge bg-success font-mono">SENT</span></div>
                        <div class="col-sm-4 text-muted">Message ID:</div>
                        <div class="col-sm-8 font-mono text-info fw-bold">${data.message_id || 're_recorded'}</div>
                        <div class="col-sm-4 text-muted">Provider:</div>
                        <div class="col-sm-8 font-mono">Resend API</div>
                    </div>
                    <div class="text-muted mt-2" style="font-size: 11px;">
                        CRM status updated to: <span class="badge bg-dark border border-info text-info">EMAIL_SENT</span>
                    </div>
                `;
            }

            if (sendBtn) {
                sendBtn.disabled = true;
                sendBtn.className = 'btn btn-success px-4';
                sendBtn.innerHTML = '<i class="fas fa-check me-1"></i> Sent ✓';
            }

            showToast("Real Email Sent", `Successfully dispatched to ${toEmail} via Resend.`);

            // Auto-refresh logs after 1.5s if on campaigns, communications, or crm
            setTimeout(() => {
                if (window.location.pathname.includes('/campaigns') || 
                    window.location.pathname.includes('/communications') || 
                    window.location.pathname.includes('/crm') || 
                    window.location.pathname.includes('/opportunities')) {
                    window.location.reload();
                }
            }, 1500);

        } else if (data.status === 'DEMO_UNSENT') {
            if (resultBox) {
                resultBox.className = 'p-3 rounded mb-3 text-warning';
                resultBox.style.background = 'rgba(245, 158, 11, 0.1)';
                resultBox.style.border = '1px solid rgba(245, 158, 11, 0.4)';
                resultBox.innerHTML = `
                    <div class="fw-bold fs-6 mb-2 text-warning">
                        <i class="fas fa-exclamation-triangle me-1"></i>DEMO MODE
                    </div>
                    <div class="text-light" style="font-size: 13px;">
                        Real email sending is disabled because <code>RESEND_API_KEY</code> is not configured.
                    </div>
                    <div class="text-white mt-1 fw-bold" style="font-size: 12px;">
                        Demo email generated but NOT sent.
                    </div>
                    <div class="text-muted mt-2" style="font-size: 11px;">
                        To send real emails, set a valid <code>RESEND_API_KEY</code> in your <code>.env</code> file.
                    </div>
                `;
            }
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.className = 'btn btn-primary-saas px-4';
                sendBtn.innerHTML = '<i class="fas fa-paper-plane me-1"></i> Send Real Email';
            }

        } else {
            const safeError = data.error || data.message || 'Resend API rejected the request.';
            if (resultBox) {
                resultBox.className = 'p-3 rounded mb-3 text-danger';
                resultBox.style.background = 'rgba(239, 68, 68, 0.1)';
                resultBox.style.border = '1px solid rgba(239, 68, 68, 0.4)';
                resultBox.innerHTML = `
                    <div class="fw-bold fs-6 mb-2 text-danger">
                        <i class="fas fa-times-circle me-1"></i>✕ Email could not be sent
                    </div>
                    <div class="text-light" style="font-size: 13px;">
                        <strong>Reason:</strong> ${safeError}
                    </div>
                `;
            }
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.className = 'btn btn-primary-saas px-4';
                sendBtn.innerHTML = '<i class="fas fa-redo me-1"></i> Retry Send';
            }
        }
    } catch (err) {
        if (resultBox) {
            resultBox.className = 'p-3 rounded mb-3 text-danger';
            resultBox.style.background = 'rgba(239, 68, 68, 0.1)';
            resultBox.style.border = '1px solid rgba(239, 68, 68, 0.4)';
            resultBox.innerHTML = `
                <div class="fw-bold fs-6 mb-1 text-danger">
                    <i class="fas fa-exclamation-triangle me-1"></i>✕ Network Dispatch Failure
                </div>
                <div class="text-light" style="font-size: 13px;">${err.message}</div>
            `;
        }
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.className = 'btn btn-primary-saas px-4';
            sendBtn.innerHTML = '<i class="fas fa-redo me-1"></i> Retry Send';
        }
    }
}

function showToast(title, body) {
    const toast = document.createElement("div");
    toast.style.position = "fixed";
    toast.style.bottom = "24px";
    toast.style.right = "24px";
    toast.style.background = "var(--bg-card)";
    toast.style.border = "1px solid var(--primary)";
    toast.style.color = "#fff";
    toast.style.padding = "14px 20px";
    toast.style.borderRadius = "12px";
    toast.style.boxShadow = "0 10px 30px rgba(0,0,0,0.6)";
    toast.style.zIndex = "9999";
    toast.innerHTML = `<strong><i class="fas fa-check-circle text-success me-2"></i>${title}</strong><div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">${body}</div>`;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.4s ease";
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
