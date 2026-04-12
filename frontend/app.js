const API_BASE = window.REVELIO_API_BASE || "/api/v1";
const appRoot = document.querySelector("#app");
const DISPLAY_TIME_ZONE = "Europe/Rome";

const DEMO_CREDENTIALS = [
  { fullName: "Alessio Maggio", username: "Amaggio", password: "Alessiom92!" },
  { fullName: "Roberto Maselli", username: "Rmaselli", password: "Robertom79!" },
  { fullName: "Erika Di Piero", username: "Edipiero", password: "Erikad98!" },
];

const MACHINE_ASSETS = {
  RM: {
    src: "/images/Risonanza%20magnetica.jpg",
    alt: "Icona della risonanza magnetica",
  },
  TC: {
    src: "/images/Tomografia%20computerizzata.png",
    alt: "Icona della tomografia computerizzata",
  },
  RX: {
    src: "/images/Radiografia.png",
    alt: "Icona della radiografia",
  },
};

const STATUS_CONFIG = {
  SCHEDULED: {
    label: "Programmato",
    badgeClass: "badge--scheduled",
    actionClass: "",
  },
  ARRIVED: {
    label: "Arrivato",
    badgeClass: "badge--arrived",
    actionClass: "action-button--arrived",
  },
  IN_PROGRESS: {
    label: "In Corso",
    badgeClass: "badge--progress",
    actionClass: "action-button--progress",
  },
  COMPLETED: {
    label: "Completato",
    badgeClass: "badge--completed",
    actionClass: "action-button--completed",
  },
  CANCELLED: {
    label: "Cancellato",
    badgeClass: "badge--cancelled",
    actionClass: "action-button--cancelled",
  },
};

const TRANSITION_BUTTON = {
  ARRIVED: { label: "Arrivato", icon: "✔", className: "action-button--arrived" },
  IN_PROGRESS: { label: "Avvia esame", icon: "▶", className: "action-button--progress" },
  COMPLETED: { label: "Completa esame", icon: "■", className: "action-button--completed" },
  CANCELLED: { label: "Cancella esame", icon: "✕", className: "action-button--cancelled" },
};

const SESSION_STATUS_LABELS = {
  PLANNED: "Pianificata",
  ACTIVE: "Attiva",
  CLOSED: "Chiusa",
};

const WORKFLOW_LINES = [
  "Programmato → Arrivato",
  "Programmato → Cancellato",
  "Arrivato → In Corso",
  "Arrivato → Cancellato",
  "In Corso → Completato",
];

const state = {
  booting: true,
  view: "loading",
  token: sessionStorage.getItem("revelio-token") || "",
  currentUser: parseJson(sessionStorage.getItem("revelio-user")),
  loginForm: {
    username: "",
    password: "",
  },
  loginPending: false,
  dashboardPending: false,
  worklistPending: false,
  examPending: false,
  transitionPending: "",
  machines: [],
  dashboardWorklists: {},
  selectedMachineCode: "",
  selectedMachineWorklist: null,
  selectedExamId: null,
  examDetail: null,
  showCancelNote: false,
  cancelNote: "",
  toast: null,
};

let toastTimer = null;
let lastAutoRefreshAt = 0;
const AUTO_REFRESH_COOLDOWN_MS = 4000;
let scrollbarHideTimer = null;
let lastRenderedView = null;
let chromeSyncTimer = null;
let lastOverflowState = false;

appRoot.addEventListener("click", handleClick);
appRoot.addEventListener("submit", handleSubmit);
appRoot.addEventListener("input", handleInput);
window.addEventListener("scroll", handlePageScroll, { passive: true });
window.addEventListener("resize", syncPageChrome);
window.addEventListener("focus", triggerAutoRefresh);
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    triggerAutoRefresh();
  }
});

boot();

async function boot() {
  if (!state.token || !state.currentUser) {
    state.booting = false;
    state.view = "login";
    render();
    return;
  }

  state.booting = false;
  state.dashboardPending = true;
  state.view = "home";
  render();

  try {
    const me = await apiFetch("/auth/me");
    state.currentUser = me;
    sessionStorage.setItem("revelio-user", JSON.stringify(me));
    await loadDashboard({ silent: true, preservePending: true });
  } catch (error) {
    clearSession(false);
    state.view = "login";
    showToast(error.message || "Sessione non valida. Effettua di nuovo l'accesso.", "error");
  }
}

function handleClick(event) {
  const trigger = event.target.closest("[data-action]");
  if (!trigger) {
    return;
  }

  const { action } = trigger.dataset;

  if (action === "dismiss-toast") {
    clearToast();
    return;
  }

  if (action === "fill-demo") {
    state.loginForm.username = trigger.dataset.username || "";
    state.loginForm.password = trigger.dataset.password || "";
    render();
    return;
  }

  if (action === "logout") {
    clearSession(false);
    state.view = "login";
    showToast("Sessione chiusa correttamente.", "success");
    render();
    return;
  }

  if (action === "go-home") {
    loadDashboard();
    return;
  }

  if (action === "open-machine") {
    const machineCode = trigger.dataset.machineCode;
    if (machineCode) {
      openMachine(machineCode);
    }
    return;
  }

  if (action === "back-home") {
    state.view = "home";
    state.selectedExamId = null;
    state.examDetail = null;
    render();
    return;
  }

  if (action === "open-exam") {
    const examId = Number(trigger.dataset.examId);
    if (examId) {
      openExam(examId);
    }
    return;
  }

  if (action === "back-worklist") {
    state.view = "worklist";
    state.selectedExamId = null;
    state.examDetail = null;
    state.showCancelNote = false;
    state.cancelNote = "";
    render();
    return;
  }

  if (action === "toggle-cancel-note") {
    state.showCancelNote = true;
    render();
    return;
  }

  if (action === "close-cancel-note") {
    state.showCancelNote = false;
    state.cancelNote = "";
    render();
    return;
  }

  if (action === "transition") {
    const targetStatus = trigger.dataset.targetStatus;
    if (targetStatus) {
      changeExamStatus(targetStatus);
    }
  }
}

function handleSubmit(event) {
  const form = event.target;

  if (form.dataset.form === "login") {
    event.preventDefault();
    login();
    return;
  }

  if (form.dataset.form === "cancel-note") {
    event.preventDefault();
    changeExamStatus("CANCELLED");
  }
}

function handleInput(event) {
  const target = event.target;
  const { field } = target.dataset;

  if (field === "username") {
    state.loginForm.username = target.value;
    return;
  }

  if (field === "password") {
    state.loginForm.password = target.value;
    return;
  }

  if (field === "cancelNote") {
    state.cancelNote = target.value;
  }
}

async function login() {
  const username = state.loginForm.username.trim();
  const password = state.loginForm.password;

  if (!username || !password) {
    showToast("Inserisci username e password per accedere.", "error");
    return;
  }

  state.loginPending = true;
  render();

  try {
    const response = await apiFetch("/auth/login", {
      method: "POST",
      body: {
        username,
        password,
      },
    });

    state.token = response.access_token;
    state.currentUser = response.technician;
    sessionStorage.setItem("revelio-token", response.access_token);
    sessionStorage.setItem("revelio-user", JSON.stringify(response.technician));
    state.loginForm.password = "";
    await loadDashboard({ silent: true });
    showToast(`Bentornato, ${response.technician.full_name}.`, "success");
  } catch (error) {
    showToast(error.message || "Credenziali non valide.", "error");
  } finally {
    state.loginPending = false;
    render();
  }
}

async function loadDashboard(options = {}) {
  state.view = "home";
  if (!options.preservePending) {
    state.dashboardPending = true;
    render();
  }

  try {
    const machines = await apiFetch("/machines");
    state.machines = machines;

    const settled = await Promise.allSettled(
      machines.map((machine) => apiFetch(`/machines/${machine.code}/worklist`)),
    );

    const summaries = {};
    settled.forEach((result, index) => {
      const code = machines[index].code;
      summaries[code] =
        result.status === "fulfilled"
          ? result.value
          : { __error: result.reason?.message || "Worklist non disponibile." };
    });

    state.dashboardWorklists = summaries;
    state.view = "home";
  } catch (error) {
    if (!options.silent) {
      showToast(error.message || "Impossibile caricare la dashboard.", "error");
    }
  } finally {
    state.dashboardPending = false;
    render();
  }
}

async function openMachine(machineCode) {
  state.selectedMachineCode = machineCode;
  state.selectedMachineWorklist = state.dashboardWorklists[machineCode] || null;
  state.worklistPending = true;
  state.view = "worklist";
  render();

  try {
    const worklist = await apiFetch(`/machines/${machineCode}/worklist`);
    state.dashboardWorklists[machineCode] = worklist;
    state.selectedMachineWorklist = worklist;
  } catch (error) {
    showToast(error.message || "Impossibile caricare la worklist.", "error");
  } finally {
    state.worklistPending = false;
    render();
  }
}

async function openExam(examId) {
  state.selectedExamId = examId;
  state.examDetail = null;
  state.examPending = true;
  state.showCancelNote = false;
  state.cancelNote = "";
  state.view = "examDetail";
  render();

  try {
    const detail = await apiFetch(`/exams/${examId}`);
    state.examDetail = detail;
  } catch (error) {
    showToast(error.message || "Impossibile caricare il dettaglio esame.", "error");
  } finally {
    state.examPending = false;
    render();
  }
}

async function refreshMachineWorklist() {
  if (!state.selectedMachineCode) {
    return;
  }

  const worklist = await apiFetch(`/machines/${state.selectedMachineCode}/worklist`);
  state.dashboardWorklists[state.selectedMachineCode] = worklist;
  state.selectedMachineWorklist = worklist;
}

async function refreshExamDetail() {
  if (!state.selectedExamId) {
    return;
  }

  const detail = await apiFetch(`/exams/${state.selectedExamId}`);
  state.examDetail = detail;
}

async function changeExamStatus(targetStatus) {
  if (!state.examDetail || !targetStatus) {
    return;
  }

  if (targetStatus === "CANCELLED" && !state.cancelNote.trim()) {
    showToast("Per cancellare un esame devi inserire una nota con il motivo.", "error");
    return;
  }

  state.transitionPending = targetStatus;
  render();

  try {
    const payload = {
      target_status: targetStatus,
    };

    if (targetStatus === "CANCELLED") {
      payload.note = state.cancelNote.trim();
    }

    const response = await apiFetch(
      `/exams/${state.examDetail.id}/state-transitions`,
      {
        method: "POST",
        body: payload,
      },
    );

    state.showCancelNote = false;
    state.cancelNote = "";

    await Promise.all([refreshMachineWorklist(), refreshExamDetail()]);

    showToast(
      `Stato aggiornato: ${statusLabel(response.previous_status)} → ${statusLabel(response.current_status)}`,
      "success",
    );
  } catch (error) {
    showToast(error.message || "Transizione non riuscita.", "error");
  } finally {
    state.transitionPending = "";
    render();
  }
}

async function apiFetch(path, options = {}) {
  const headers = {
    Accept: "application/json",
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}),
  };

  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method || "GET",
    cache: "no-store",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json().catch(() => null)
    : await response.text().catch(() => "");

  if (!response.ok) {
    const message =
      (payload && typeof payload.detail === "string" && payload.detail) ||
      (typeof payload === "string" && payload) ||
      "Si è verificato un errore inatteso.";

    if (response.status === 401 && path !== "/auth/login") {
      clearSession(false);
      state.view = "login";
      render();
      throw new Error("Sessione scaduta. Effettua di nuovo l'accesso.");
    }

    throw new Error(message);
  }

  return payload;
}

function render() {
  appRoot.innerHTML = `
    ${renderToast()}
    ${renderScreen()}
  `;

  syncPageChrome();
  queueChromeSync();

  if (state.showCancelNote) {
    const textarea = appRoot.querySelector("[data-note-input]");
    if (textarea) {
      textarea.focus();
      textarea.selectionStart = textarea.value.length;
    }
  }
}

function renderScreen() {
  if (state.booting || state.view === "loading") {
    return renderLoading();
  }

  if (state.view === "login") {
    return renderLogin();
  }

  if (state.view === "worklist") {
    return renderWorklist();
  }

  if (state.view === "examDetail") {
    return renderExamDetail();
  }

  return renderHome();
}

function handlePageScroll() {
  if (!isScrollableView()) {
    return;
  }

  if (!hasPageVerticalOverflow()) {
    return;
  }

  showScrollbarTemporarily();
}

function syncPageChrome() {
  const scrollableView = isScrollableView();
  const body = document.body;
  const worklistView = state.view === "worklist";

  body.classList.toggle("body-worklist-scroll", worklistView);

  if (!scrollableView) {
    clearScrollbarTimer();
    body.classList.remove("page-scrollbar-visible");
    lastRenderedView = state.view;
    lastOverflowState = false;
    return;
  }

  const hasOverflow = hasPageVerticalOverflow();
  if (!hasOverflow) {
    clearScrollbarTimer();
    body.classList.remove("page-scrollbar-visible");
    lastRenderedView = state.view;
    lastOverflowState = false;
    return;
  }

  if (lastRenderedView !== state.view) {
    window.scrollTo({ top: 0, behavior: "auto" });
    showScrollbarTemporarily();
  } else if (!lastOverflowState) {
    showScrollbarTemporarily();
  } else if (body.classList.contains("page-scrollbar-visible")) {
    resetScrollbarTimer();
  }

  lastRenderedView = state.view;
  lastOverflowState = hasOverflow;
}

function queueChromeSync() {
  window.requestAnimationFrame(syncPageChrome);
  if (chromeSyncTimer) {
    window.clearTimeout(chromeSyncTimer);
  }
  chromeSyncTimer = window.setTimeout(syncPageChrome, 140);
}

function isScrollableView() {
  return state.view === "worklist" || state.view === "examDetail";
}

function showScrollbarTemporarily() {
  const body = document.body;
  if (!isScrollableView()) {
    return;
  }

  body.classList.add("page-scrollbar-visible");
  resetScrollbarTimer();
}

function hasPageVerticalOverflow() {
  const root = document.documentElement;
  const body = document.body;
  const maxHeight = Math.max(root.scrollHeight, body.scrollHeight);
  return maxHeight > window.innerHeight + 1;
}

function resetScrollbarTimer() {
  clearScrollbarTimer();
  scrollbarHideTimer = window.setTimeout(() => {
    document.body.classList.remove("page-scrollbar-visible");
  }, 3000);
}

function clearScrollbarTimer() {
  if (scrollbarHideTimer) {
    window.clearTimeout(scrollbarHideTimer);
    scrollbarHideTimer = null;
  }
}

function renderToast() {
  if (!state.toast) {
    return "";
  }

  const icon = state.toast.type === "error" ? "!" : "✓";
  return `
    <div class="toast-host" role="status" aria-live="polite">
      <div class="toast toast--${state.toast.type}">
        <span class="toast__icon">${icon}</span>
        <div class="toast__body">${escapeHtml(state.toast.message)}</div>
        <button
          type="button"
          class="toast__dismiss"
          data-action="dismiss-toast"
          aria-label="Chiudi notifica"
        >
          ✕
        </button>
      </div>
    </div>
  `;
}

function renderLoading() {
  return `
    <section class="screen loading-screen">
      <div class="loading-card">
        <div class="brand-mark">R</div>
        <h1 class="brand-title">Revelio</h1>
        <p class="brand-subtitle">
          Stiamo preparando dashboard, worklist ed esami nel linguaggio visivo del tuo design system.
        </p>
        <div class="loading-line" aria-hidden="true"><span></span></div>
      </div>
    </section>
  `;
}

function renderLogin() {
  return `
    <section class="screen login">
      <aside class="login__visual">
        <div class="login__copy">
          <h1 class="login__headline">Revelio</h1>
          <div class="login__eyebrow">RADIOLOGY WORKFLOW</div>
          <p class="login__lead">
            Visualizza gli esami programmati per la giornata e gestiscili con semplicità.
          </p>
        </div>
      </aside>
      <div class="login__panel">
        <div class="login__card">
          <h2 class="card-heading">Accedi</h2>
          <p class="card-copy">
            Inserisci le credenziali del tecnico radiologo per aprire la dashboard operativa.
          </p>
          <form class="form-stack" data-form="login">
            <div class="field">
              <label class="field__label" for="username">Username</label>
              <input
                id="username"
                class="field__control"
                data-field="username"
                value="${escapeHtml(state.loginForm.username)}"
                placeholder="es. Amaggio"
                autocomplete="username"
              />
            </div>
            <div class="field">
              <label class="field__label" for="password">Password</label>
              <input
                id="password"
                class="field__control"
                type="password"
                data-field="password"
                value="${escapeHtml(state.loginForm.password)}"
                placeholder="Inserisci password"
                autocomplete="current-password"
              />
            </div>
            <button class="primary-button" type="submit" ${state.loginPending ? "disabled" : ""}>
              ${state.loginPending ? "Accesso in corso..." : "Accedi"}
            </button>
          </form>
          <div class="demo-card">
            <div class="demo-card__title">Credenziali di prova</div>
            <div class="demo-list">
              ${DEMO_CREDENTIALS.map(renderDemoUser).join("")}
            </div>
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderDemoUser(user) {
  return `
    <button
      type="button"
      class="demo-user"
      data-action="fill-demo"
      data-username="${escapeHtml(user.username)}"
      data-password="${escapeHtml(user.password)}"
    >
      <span class="demo-user__name">${escapeHtml(user.fullName)}</span>
      <span class="demo-user__creds">${escapeHtml(user.username)} / ${escapeHtml(user.password)}</span>
    </button>
  `;
}

function renderHome() {
  const dashboardShift = findDashboardReferenceShift();
  const activeMachines = countMachinesInShift(dashboardShift);
  const machinesLabel = activeMachines === 1 ? "MACCHINA ATTIVA" : "MACCHINE ATTIVE";
  const shiftLabel = dashboardShift
    ? `${formatTime(dashboardShift.start_at)} – ${formatTime(dashboardShift.end_at)}`
    : "NESSUN TURNO";

  return `
    <section class="screen">
      ${renderTopBar()}
      <main class="page">
        <div class="shell">
          <header class="page__header">
            <div>
              <div class="page__eyebrow">Dashboard</div>
              <h1 class="page__title">Macchinari e worklist</h1>
              <p class="page__copy page__copy--dashboard">
                Seleziona un macchinario per aprire la worklist completa. La dashboard evidenzia quali macchine sono in turno in questo momento e quante attività risultano già in lista.
              </p>
            </div>
            <div class="hero-chip">
              <div class="hero-chip__line">
                <strong class="hero-chip__metric">${activeMachines}</strong>
                <span class="hero-chip__copy">${machinesLabel} - ${shiftLabel}</span>
              </div>
            </div>
          </header>
          ${
            state.dashboardPending
              ? renderDashboardSkeleton()
              : state.machines.length
                ? `
                <div class="machine-grid">
                  ${state.machines.map(renderMachineCard).join("")}
                </div>
              `
                : `<div class="empty-state">Nessuna macchina attiva disponibile.</div>`
          }
        </div>
      </main>
    </section>
  `;
}

function renderDashboardSkeleton() {
  return `
    <div class="machine-grid">
      <div class="skeleton skeleton--card"></div>
      <div class="skeleton skeleton--card"></div>
      <div class="skeleton skeleton--card"></div>
    </div>
  `;
}

function renderMachineCard(machine) {
  const worklist = state.dashboardWorklists[machine.code];
  const activeSession = findMachineActiveSession(worklist);
  const activeSessionOwned =
    activeSession && activeSession.technician_id === state.currentUser?.id;
  const nextSession = findUpcomingMachineSession(worklist);
  const machineExams = flattenExams(worklist);
  const badge = activeSessionOwned
    ? `<span class="badge badge--active">Sessione attiva</span>`
    : activeSession
      ? `<span class="badge badge--scheduled">Turno in corso</span>`
      : nextSession
        ? `<span class="badge badge--scheduled">Prossima sessione</span>`
        : `<span class="badge badge--scheduled">Nessun turno in corso</span>`;

  const summaryText = worklist?.__error
    ? "Worklist non disponibile in questo momento."
    : activeSession
      ? `${formatTime(activeSession.start_at)} – ${formatTime(activeSession.end_at)}`
      : nextSession
        ? `${formatTime(nextSession.start_at)} – ${formatTime(nextSession.end_at)}`
        : "Apri la worklist della macchina.";

  const footerText = worklist?.__error
    ? "Ricarica la dashboard per riprovare."
    : activeSession
      ? `${activeSession.technician_name} · ${activeSession.exams.length} esami in turno`
      : nextSession
        ? `${nextSession.technician_name} · ${nextSession.exams.length} esami previsti`
        : `${machineExams.length} esami visibili`;

  return `
    <button
      type="button"
      class="machine-card ${activeSessionOwned ? "machine-card--active" : ""}"
      data-action="open-machine"
      data-machine-code="${escapeHtml(machine.code)}"
    >
      ${badge}
      <div class="machine-visual">${renderMachineArtwork(machine.code)}</div>
      <div>
        <div class="machine-code">${escapeHtml(machine.code)}</div>
        <div class="machine-name">${escapeHtml(machine.display_name)}</div>
      </div>
      <div class="machine-meta">
        <div class="machine-meta__copy">${summaryText}</div>
        <div class="machine-meta__footer">${footerText}</div>
      </div>
    </button>
  `;
}

function renderWorklist() {
  const worklist = state.selectedMachineWorklist;
  const machine = worklist?.machine;
  const sessions = normalizedSessions(worklist);
  const exams = flattenExams(worklist);
  const activeSession = findMachineActiveSession(worklist);
  const nextSession = findUpcomingMachineSession(worklist);
  const completedOrCancelled = exams.filter(
    (exam) => exam.status === "COMPLETED" || exam.status === "CANCELLED",
  ).length;
  const examsInList = exams.length - completedOrCancelled;
  const referenceSession = activeSession || nextSession || sessions[0];
  const sessionOverview = collectSessionsOverview(machine?.code);
  const worklistTitle = machine
    ? `${escapeHtml(machine.code)} — ${escapeHtml(machine.display_name)}`
    : "Worklist";

  return `
    <section class="screen screen--worklist">
      ${renderTopBar()}
      <main class="page">
        <div class="shell">
          <button class="back-link button-reset" type="button" data-action="back-home">
            ← Dashboard
          </button>
          <header class="page__header">
            <div>
              <div class="page__eyebrow">Worklist</div>
              <h1 class="page__title">${worklistTitle}</h1>
              <p class="page__copy page__copy--worklist">
                Consulta gli esami ordinati per orario, verifica chi sta lavorando sulla macchina in questo momento e apri il dettaglio per seguire lo stato di avanzamento.
              </p>
            </div>
          </header>
          ${
            state.worklistPending
              ? renderWorklistSkeleton()
              : worklist?.__error
                ? `<div class="empty-state">${escapeHtml(worklist.__error)}</div>`
                : `
                  <div class="summary-grid">
                    <div class="summary-card">
                      <div class="summary-card__label">Esami in lista</div>
                      <div class="summary-card__value">${Math.max(examsInList, 0)}</div>
                      <div class="summary-card__meta">Ordinati per orario programmato</div>
                    </div>
                    <div class="summary-card">
                      <div class="summary-card__label">Esami conclusi</div>
                      <div class="summary-card__value">${completedOrCancelled}</div>
                      <div class="summary-card__meta">Completati o cancellati</div>
                    </div>
                    <div class="summary-card">
                      <div class="summary-card__label">Turno assegnato</div>
                      <div class="summary-card__value">${
                        referenceSession
                          ? `${formatTime(referenceSession.start_at)} – ${formatTime(referenceSession.end_at)}`
                          : "N/D"
                      }</div>
                      <div class="summary-card__meta">${
                        referenceSession
                          ? `${escapeHtml(referenceSession.technician_name)} · ${referenceSession.exams.length} esami previsti`
                          : "Nessun turno disponibile per questa macchina."
                      }</div>
                    </div>
                  </div>
                  <div class="layout-grid">
                    <section class="panel">
                      <div class="panel__header">
                        <div>
                          <div class="panel__title">Esami della macchina</div>
                          <div class="panel__copy">Le righe con bordo verde appartengono alla tua sessione su questa macchina.</div>
                        </div>
                        ${
                          worklist?.generated_at
                            ? `<div class="muted-copy">Aggiornato alle ${formatTime(worklist.generated_at)}</div>`
                            : ""
                        }
                      </div>
                      <div class="panel__body">
                        ${
                          exams.length
                            ? `
                              <div class="table-wrap">
                                <div class="table-head">
                                  <div>Codice</div>
                                  <div>Paziente</div>
                                  <div>Orario</div>
                                  <div>Sessione</div>
                                  <div>Stato</div>
                                </div>
                                ${exams.map(renderExamRow).join("")}
                              </div>
                            `
                            : `<div class="empty-state">Nessun esame disponibile per questa macchina.</div>`
                        }
                      </div>
                    </section>
                    <aside class="panel">
                      <div class="panel__header">
                        <div>
                          <div class="panel__title">Sessioni operative</div>
                          <div class="panel__copy">Panoramica dei turni ordinati per macchina e orario.</div>
                        </div>
                      </div>
                      <div class="panel__body">
                        ${
                          sessionOverview.length
                            ? `<div class="session-stack">${sessionOverview.map(renderSessionOverviewItem).join("")}</div>`
                            : `<div class="empty-state">Nessuna sessione presente.</div>`
                        }
                      </div>
                    </aside>
                  </div>
                `
          }
        </div>
      </main>
    </section>
  `;
}

function renderWorklistSkeleton() {
  return `
    <div class="summary-grid">
      <div class="skeleton skeleton--card"></div>
      <div class="skeleton skeleton--card"></div>
      <div class="skeleton skeleton--card"></div>
    </div>
    <div class="layout-grid">
      <div class="loading-state">
        <div class="skeleton skeleton--line"></div>
        <div class="skeleton skeleton--card"></div>
      </div>
      <div class="loading-state">
        <div class="skeleton skeleton--line"></div>
        <div class="skeleton skeleton--card"></div>
      </div>
    </div>
  `;
}

function renderExamRow(item) {
  const patientName = `${item.patient.first_name} ${item.patient.last_name}`;
  const isInProgress = item.status === "IN_PROGRESS";
  return `
    <button
      type="button"
      class="table-row ${isInProgress ? "table-row--in-progress" : ""}"
      data-action="open-exam"
      data-exam-id="${item.id}"
    >
      <div class="table-row__cell table-row__cell--code">
        <div class="code-pill">${escapeHtml(item.exam_code)}</div>
      </div>
      <div class="table-row__cell table-row__cell--patient">
        <div class="patient-name">${escapeHtml(patientName)}</div>
        <div class="patient-code">${escapeHtml(item.patient.patient_code)}</div>
      </div>
      <div class="table-row__cell table-row__cell--time">
        <div class="table-meta table-meta--strong">${formatTime(item.scheduled_time)}</div>
        <div class="table-meta">programmato</div>
      </div>
      <div class="table-row__cell table-row__cell--session">
        <div class="session-meta__line">${formatTime(item.session.start_at)} – ${formatTime(item.session.end_at)}</div>
        <div class="session-meta__line">${escapeHtml(item.session.technician_name)}</div>
      </div>
      <div class="table-row__cell table-row__cell--status">${renderStatusBadge(item.status)}</div>
    </button>
  `;
}

function collectSessionsOverview(skipMachineCode) {
  const entries = [];

  Object.entries(state.dashboardWorklists || {}).forEach(([code, worklist]) => {
    if (!worklist || worklist.__error) {
      return;
    }
    if (skipMachineCode && code === skipMachineCode) {
      return;
    }

    const machineName = worklist.machine?.display_name || code;
    normalizedSessions(worklist).forEach((session) => {
      entries.push({
        machineCode: code,
        machineName,
        session,
      });
    });
  });

  return entries.sort((left, right) => {
    const byMachine = left.machineName.localeCompare(right.machineName, "it");
    if (byMachine !== 0) {
      return byMachine;
    }
    return toDate(left.session.start_at) - toDate(right.session.start_at);
  });
}

function renderSessionOverviewItem(item) {
  const session = item.session;
  const active = session.is_active_now;

  return `
    <div class="session-card session-card--overview ${active ? "session-card--active" : ""}">
      <div class="session-card__row">
        <div class="session-card__heading">
          <div class="session-card__title">${escapeHtml(item.machineName)}</div>
          <div class="session-card__shift">${formatTime(session.start_at)} – ${formatTime(session.end_at)}</div>
        </div>
        ${
          active
            ? `<span class="badge badge--active">Attiva</span>`
            : `<span class="badge badge--scheduled">${sessionStatusLabel(session.status)}</span>`
        }
      </div>
      <div class="session-card__copy">${escapeHtml(session.technician_name)}</div>
      <div class="session-card__meta">
        <span>${session.exams.length} esami previsti</span>
      </div>
    </div>
  `;
}

function renderExamDetail() {
  const detail = state.examDetail;
  const allowed = detail?.allowed_transitions || [];
  const isOwnSession = detail?.session.technician_id === state.currentUser?.id;
  const isSessionWindowOpen = detail ? isSessionInProgress(detail.session) : false;

  return `
    <section class="screen">
      ${renderTopBar()}
      <main class="page">
        <div class="shell">
          <button class="back-link button-reset" type="button" data-action="back-worklist">
            ← Worklist
          </button>
          ${
            state.examPending
              ? renderExamSkeleton()
              : !detail
                ? `<div class="empty-state">Dettaglio esame non disponibile.</div>`
                : `
                  <div class="detail-layout">
                    <section class="detail-card">
                      <div class="detail-header">
                        <div>
                          <h1 class="detail-title">${escapeHtml(detail.exam_code)}</h1>
                          <div class="detail-subtitle">
                            Macchina ${escapeHtml(detail.session.machine.code)} · Sessione ${formatTime(detail.session.start_at)} – ${formatTime(detail.session.end_at)}
                          </div>
                        </div>
                        ${renderStatusBadge(detail.status, true)}
                      </div>

                      <div class="detail-info-grid">
                        ${renderInfoBlock("Paziente", `${detail.patient.last_name} ${detail.patient.first_name}`)}
                        ${renderInfoBlock("Codice paziente", detail.patient.patient_code)}
                        ${renderInfoBlock("Data di nascita", formatDate(detail.patient.birth_date))}
                        ${renderInfoBlock("Sesso", detail.patient.sex || "—")}
                        ${renderInfoBlock("Orario programmato", formatDateTime(detail.scheduled_time))}
                        ${renderInfoBlock("Ultimo aggiornamento", formatDateTime(detail.status_updated_at))}
                        ${renderInfoBlock("Tecnico assegnato", detail.session.technician_name)}
                        ${renderInfoBlock(
                          "Sessione propria",
                          detail.session.technician_id === state.currentUser?.id ? "Sì" : "No",
                        )}
                      </div>

                      <div class="section-divider"></div>
                      <h2 class="section-title">Cambia stato dell’esame</h2>
                      <p class="section-copy">
                        Aggiorna l'esame seguendo il flusso previsto. Se lo cancelli, serve una nota con il motivo.
                      </p>
                      ${
                        !isOwnSession
                          ? `<div class="warning-box" style="margin-top:16px;">Questo esame e' assegnato a ${escapeHtml(detail.session.technician_name)}. Puoi consultarlo, ma per modificarlo deve intervenire il tecnico della sessione.</div>`
                          : !isSessionWindowOpen && !allowed.length
                          ? `<div class="warning-box" style="margin-top:16px;">Puoi cambiare stato solo durante la fascia oraria della sessione assegnata (${formatTime(detail.session.start_at)} – ${formatTime(detail.session.end_at)}).</div>`
                          : allowed.length
                          ? `
                            <div class="action-row">
                              ${allowed.map(renderActionButton).join("")}
                            </div>
                            ${
                              state.showCancelNote
                                ? `
                                  <form class="inline-note" data-form="cancel-note">
                                    <div class="field">
                                      <label class="field__label" for="cancel-note">Motivo della cancellazione</label>
                                      <textarea
                                        id="cancel-note"
                                        class="field__textarea"
                                        data-field="cancelNote"
                                        data-note-input="true"
                                        placeholder="Inserisci il motivo per cui l'esame viene cancellato..."
                                      >${escapeHtml(state.cancelNote)}</textarea>
                                    </div>
                                    <div class="inline-note__actions">
                                      <button
                                        class="action-button action-button--cancelled"
                                        type="submit"
                                        ${state.transitionPending === "CANCELLED" ? "disabled" : ""}
                                      >
                                        ${state.transitionPending === "CANCELLED" ? "Salvataggio..." : "Conferma cancellazione"}
                                      </button>
                                      <button
                                        class="secondary-button"
                                        type="button"
                                        data-action="close-cancel-note"
                                      >
                                        Annulla
                                      </button>
                                    </div>
                                  </form>
                                `
                                : ""
                            }
                          `
                          : `<div class="info-box" style="margin-top:16px;">Questo esame si trova in uno stato finale: non sono previste ulteriori transizioni.</div>`
                      }
                    </section>

                    <aside class="detail-card">
                      <h2 class="section-title">Cronologia operazioni</h2>
                      <p class="section-copy">
                        Ogni cambio di stato viene storicizzato con tecnico, orario ed eventuale nota.
                      </p>
                      ${
                        detail.audit_events.length
                          ? `<div class="audit-stack">${detail.audit_events
                              .slice()
                              .sort((left, right) => new Date(right.performed_at) - new Date(left.performed_at))
                              .map(renderAuditItem)
                              .join("")}</div>`
                          : `<div class="empty-state" style="margin-top:16px;">Nessuna operazione registrata per questo esame.</div>`
                      }
                      <div class="workflow-box">
                        <div class="workflow-box__title">Flusso consentito</div>
                        <div class="workflow-box__list">
                          ${WORKFLOW_LINES.map((line) => `<span>${line}</span>`).join("")}
                        </div>
                      </div>
                    </aside>
                  </div>
                `
          }
        </div>
      </main>
    </section>
  `;
}

function renderExamSkeleton() {
  return `
    <div class="detail-layout">
      <div class="loading-state">
        <div class="skeleton skeleton--line"></div>
        <div class="skeleton skeleton--card"></div>
      </div>
      <div class="loading-state">
        <div class="skeleton skeleton--line"></div>
        <div class="skeleton skeleton--card"></div>
      </div>
    </div>
  `;
}

function renderTopBar() {
  return `
    <header class="page-topbar">
      <div class="page-topbar__inner">
        <button type="button" class="logo-button button-reset" data-action="go-home">
          <span class="logo-button__mark">R</span>
          <span class="logo-button__meta">
            <span class="logo-button__brand">Revelio</span>
            <span class="logo-button__strap">Sistema di gestione radiologica</span>
          </span>
        </button>
        <div class="page-topbar__actions">
          <span class="greeting">${getGreeting()}, <strong>${escapeHtml(state.currentUser?.full_name || "")}</strong></span>
          <button type="button" class="logout-button button-reset" data-action="logout">Esci</button>
        </div>
      </div>
    </header>
  `;
}

function renderInfoBlock(label, value) {
  return `
    <div class="info-block">
      <div class="info-block__label">${escapeHtml(label)}</div>
      <div class="info-block__value">${escapeHtml(value)}</div>
    </div>
  `;
}

function renderActionButton(status) {
  const config = TRANSITION_BUTTON[status];
  const isDisabled = state.transitionPending && state.transitionPending !== status;
  if (!config) {
    return "";
  }

  if (status === "CANCELLED") {
    return `
      <button
        type="button"
        class="action-button ${config.className}"
        data-action="toggle-cancel-note"
        ${isDisabled ? "disabled" : ""}
      >
        <span>${config.icon}</span>
        <span>${config.label}</span>
      </button>
    `;
  }

  return `
    <button
      type="button"
      class="action-button ${config.className}"
      data-action="transition"
      data-target-status="${status}"
      ${isDisabled || state.transitionPending === status ? "disabled" : ""}
    >
      <span>${config.icon}</span>
      <span>${state.transitionPending === status ? "Aggiornamento..." : config.label}</span>
    </button>
  `;
}

function renderAuditItem(event) {
  return `
    <div class="audit-item">
      <div class="audit-item__meta">
        ${formatDateTime(event.performed_at)} · ${escapeHtml(event.performed_by.full_name)}
      </div>
      <div class="audit-item__transition">
        ${renderStatusBadge(event.from_status)}
        <span>→</span>
        ${renderStatusBadge(event.to_status)}
      </div>
      ${
        event.note
          ? `<div class="audit-item__note">Motivo: "${escapeHtml(event.note)}"</div>`
          : ""
      }
    </div>
  `;
}

function renderStatusBadge(status, large = false) {
  const config = STATUS_CONFIG[status];
  if (!config) {
    return "";
  }

  return `
    <span class="badge ${config.badgeClass}" ${large ? 'style="font-size:14px;padding:5px 14px;"' : ""}>
      ${config.label}
    </span>
  `;
}

function renderMachineArtwork(code) {
  const asset = MACHINE_ASSETS[code] || MACHINE_ASSETS.RM;

  return `
    <img
      class="machine-visual__image"
      src="${asset.src}"
      alt="${escapeHtml(asset.alt)}"
      decoding="async"
    />
  `;
}

function flattenExams(worklist) {
  if (!worklist || worklist.__error) {
    return [];
  }

  return normalizedSessions(worklist)
    .flatMap((session) =>
      session.exams.map((exam) => ({
        ...exam,
        session,
      })),
    )
    .sort((left, right) => toDate(left.scheduled_time) - toDate(right.scheduled_time));
}

function normalizedSessions(worklist) {
  if (!worklist || worklist.__error) {
    return [];
  }

  return (worklist.sessions || []).slice().sort(
    (left, right) => toDate(left.start_at) - toDate(right.start_at),
  );
}

function findMachineActiveSession(worklist) {
  const sessions = normalizedSessions(worklist);
  if (!sessions.length) {
    return null;
  }

  if (worklist?.active_session_id) {
    return sessions.find((session) => session.id === worklist.active_session_id) || null;
  }

  return sessions.find((session) => session.is_active_now) || null;
}

function findDashboardReferenceShift() {
  const worklists = Object.values(state.dashboardWorklists || {});
  const allSessions = worklists
    .filter((worklist) => worklist && !worklist.__error)
    .flatMap((worklist) => normalizedSessions(worklist));

  const activeSessions = allSessions
    .filter((session) => session.is_active_now)
    .sort((left, right) => toDate(left.start_at) - toDate(right.start_at));
  if (activeSessions.length) {
    return activeSessions[0];
  }

  const ownSessions = allSessions.filter(
    (session) => session.technician_id === state.currentUser?.id,
  );

  if (!ownSessions.length) {
    return null;
  }

  const activeOwnSession = ownSessions.find((session) => session.is_active_now);
  if (activeOwnSession) {
    return activeOwnSession;
  }

  const upcomingOwnSession = ownSessions
    .filter((session) => toDate(session.start_at) >= new Date())
    .sort((left, right) => toDate(left.start_at) - toDate(right.start_at))[0];

  return upcomingOwnSession || ownSessions[0];
}

function countMachinesInShift(referenceShift) {
  if (!referenceShift) {
    return 0;
  }

  const shiftStart = toDate(referenceShift.start_at).getTime();
  const shiftEnd = toDate(referenceShift.end_at).getTime();

  return state.machines.filter((machine) => {
    if (machine.is_active === false) {
      return false;
    }

    const sessions = normalizedSessions(state.dashboardWorklists[machine.code]);
    return sessions.some((session) => {
      const sessionStart = toDate(session.start_at).getTime();
      const sessionEnd = toDate(session.end_at).getTime();
      return session.is_active_now && sessionStart === shiftStart && sessionEnd === shiftEnd;
    });
  }).length;
}

async function triggerAutoRefresh() {
  if (!state.token || state.view === "login" || state.view === "loading") {
    return;
  }

  const now = Date.now();
  if (now - lastAutoRefreshAt < AUTO_REFRESH_COOLDOWN_MS) {
    return;
  }
  lastAutoRefreshAt = now;

  try {
    if (state.view === "home") {
      await loadDashboard({ silent: true, preservePending: true });
      return;
    }

    if (state.selectedMachineCode) {
      await refreshMachineWorklist();
    }

    if (state.view === "examDetail" && state.selectedExamId) {
      await refreshExamDetail();
    }

    render();
  } catch {
  }
}

function isSessionInProgress(session) {
  if (!session) {
    return false;
  }

  const now = new Date();
  const start = toDate(session.start_at);
  const end = toDate(session.end_at);
  return start <= now && now < end;
}

function findUpcomingMachineSession(worklist) {
  return normalizedSessions(worklist)
    .filter((session) => toDate(session.start_at) > new Date())
    .sort((left, right) => toDate(left.start_at) - toDate(right.start_at))[0];
}

function statusLabel(status) {
  return STATUS_CONFIG[status]?.label || status || "—";
}

function sessionStatusLabel(status) {
  return SESSION_STATUS_LABELS[status] || status || "—";
}

function formatTime(value) {
  return toDate(value).toLocaleTimeString("it-IT", {
    timeZone: DISPLAY_TIME_ZONE,
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDateTime(value) {
  return toDate(value).toLocaleString("it-IT", {
    timeZone: DISPLAY_TIME_ZONE,
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-");
    return `${day}/${month}/${year}`;
  }

  return toDate(value).toLocaleDateString("it-IT", {
    timeZone: DISPLAY_TIME_ZONE,
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function getGreeting() {
  const hour = Number(
    new Intl.DateTimeFormat("en-GB", {
      hour: "2-digit",
      hour12: false,
      timeZone: DISPLAY_TIME_ZONE,
    }).format(new Date()),
  );

  if (hour >= 5 && hour < 12) {
    return "Buongiorno";
  }
  if (hour >= 12 && hour < 18) {
    return "Buon pomeriggio";
  }
  return "Buonasera";
}

function showToast(message, type = "success") {
  state.toast = { message, type };
  render();
  clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    clearToast();
  }, 3400);
}

function clearToast() {
  clearTimeout(toastTimer);
  state.toast = null;
  render();
}

function clearSession(shouldRender = true) {
  state.token = "";
  state.currentUser = null;
  state.dashboardWorklists = {};
  state.machines = [];
  state.selectedMachineCode = "";
  state.selectedMachineWorklist = null;
  state.selectedExamId = null;
  state.examDetail = null;
  state.showCancelNote = false;
  state.cancelNote = "";
  sessionStorage.removeItem("revelio-token");
  sessionStorage.removeItem("revelio-user");

  if (shouldRender) {
    render();
  }
}

function toDate(value) {
  if (value instanceof Date) {
    return value;
  }

  if (typeof value !== "string") {
    return new Date(value);
  }

  const normalized = value.trim().replace(" ", "T");
  const isNaiveIso = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?$/.test(normalized);
  return new Date(isNaiveIso ? `${normalized}Z` : normalized);
}

function parseJson(value) {
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
