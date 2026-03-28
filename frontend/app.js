const TASKS_URL  = window.DEVBOARD_TASKS_URL || "http://localhost:8001";
const WIKI_URL   = window.DEVBOARD_WIKI_URL  || "http://localhost:8002";
const DRAFT_KEY  = "devboard_task_draft";
const AUTH_KEY   = "devboard_api_key";

let API_KEY = localStorage.getItem(AUTH_KEY) || "";

let currentTaskFilter = "all";
let currentSearch = { tasks: "", pages: "" };
let taskSearchTimer = null;
let pageSearchTimer = null;

marked.setOptions({ breaks: true, gfm: true });

// ── Auth ──────────────────────────────────────────────────

async function tryLogin() {
  const userEl = document.getElementById("login-user");
  const passEl = document.getElementById("login-pass");
  const err    = document.getElementById("login-err");
  err.textContent = "";

  const username = userEl.value.trim();
  const password = passEl.value;
  if (!username || !password) { err.textContent = "Enter username and password."; return; }

  const res = await fetch(`${TASKS_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) { err.textContent = "Invalid credentials."; passEl.value = ""; passEl.focus(); return; }

  const { api_key } = await res.json();
  API_KEY = api_key;
  localStorage.setItem(AUTH_KEY, api_key);
  document.getElementById("login-screen").classList.add("hidden");
  document.getElementById("app").classList.remove("hidden");
  setTaskFilter("all");
  loadTasks();
  loadAssignees();
}

function logout() {
  API_KEY = "";
  localStorage.removeItem(AUTH_KEY);
  document.getElementById("app").classList.add("hidden");
  document.getElementById("login-screen").classList.remove("hidden");
  document.getElementById("login-user").value = "";
  document.getElementById("login-pass").value = "";
  document.getElementById("login-err").textContent = "";
}

// ── Navigation ────────────────────────────────────────────

function showSection(name) {
  ["tasks", "wiki"].forEach(s => {
    document.getElementById(`section-${s}`).classList.add("hidden");
    const btn = document.getElementById(`nav-${s}`);
    btn.classList.remove("active");
    btn.style.color = "var(--nav-muted)";
  });
  document.getElementById(`section-${name}`).classList.remove("hidden");
  const active = document.getElementById(`nav-${name}`);
  active.classList.add("active");
  active.style.color = "var(--nav-text)";
  if (name === "tasks") { loadTasks(); loadAssignees(); }
  if (name === "wiki")  loadPages();
}

// ── Filter & search ───────────────────────────────────────

function setTaskFilter(filter) {
  currentTaskFilter = filter;
  document.querySelectorAll(".filter-tab").forEach(b => b.classList.remove("active"));
  document.getElementById(`filter-${filter}`).classList.add("active");
  loadTasks();
}

function onTaskSearch(value) {
  clearTimeout(taskSearchTimer);
  taskSearchTimer = setTimeout(() => {
    currentSearch.tasks = value.trim();
    loadTasks();
  }, 300);
}

function onPageSearch(value) {
  clearTimeout(pageSearchTimer);
  pageSearchTimer = setTimeout(() => {
    currentSearch.pages = value.trim();
    loadPages();
  }, 300);
}

// ── Assignees autocomplete ────────────────────────────────

async function loadAssignees() {
  try {
    const data = await apiFetch(`${TASKS_URL}/tasks/assignees`);
    const dl = document.getElementById("assignees-list");
    dl.innerHTML = data.assignees.map(a => `<option value="${escAttr(a)}">`).join("");
  } catch (_) {}
}

// ── Validation ────────────────────────────────────────────

function setFieldError(el, message) {
  el.style.borderColor = "var(--rose)";
  const errId = `${el.id}-err`;
  let err = document.getElementById(errId);
  if (!err) {
    err = document.createElement("p");
    err.id = errId;
    err.style.cssText = "color:var(--rose); font-size:.7rem; margin-top:.2rem;";
    el.insertAdjacentElement("afterend", err);
  }
  err.textContent = message;
}

function clearFieldError(el) {
  el.style.borderColor = "";
  const err = document.getElementById(`${el.id}-err`);
  if (err) err.remove();
}

function validateRequired(el, label) {
  if (!el.value.trim()) { setFieldError(el, `${label} is required`); return false; }
  clearFieldError(el);
  return true;
}

// ── Tasks — list ─────────────────────────────────────────

const STATUS_CYCLE = ["todo", "in_progress", "done"];

async function loadTasks() {
  const params = new URLSearchParams({ page_size: 100 });
  if (currentTaskFilter === "overdue") {
    params.set("overdue", "true");
  } else if (currentTaskFilter !== "all") {
    params.set("status", currentTaskFilter);
  }
  if (currentSearch.tasks) params.set("q", currentSearch.tasks);

  const data = await apiFetch(`${TASKS_URL}/tasks?${params}`);
  const list = document.getElementById("tasks-list");
  if (!data.items.length) { list.innerHTML = emptyState("No tasks found."); return; }
  list.innerHTML = data.items.map(t => taskCard(t)).join("");
}

function taskCard(task, editMode = false) {
  if (editMode) return taskEditCard(task);

  const labels = (task.labels || "").split(",").map(l => l.trim()).filter(Boolean)
    .map(l => `<span class="badge-label text-xs px-2 py-0.5 rounded-full">${escHtml(l)}</span>`).join("");

  const wikiLink = task.wiki_page_id
    ? `<a href="#" onclick="event.preventDefault();goToWikiPage(${task.wiki_page_id})"
        class="badge-wiki text-xs px-2 py-0.5 rounded-full">&#128196; ${wikiPageTitle(task.wiki_page_id)}</a>`
    : "";

  const dueHtml = formatDue(task.due_at, task.status);

  return `
  <div id="task-card-${task.id}" class="card" style="overflow:hidden;">
    <div class="px-5 py-4 flex items-start gap-3">
      <div class="flex-1 min-w-0">
        <p class="font-semibold text-sm leading-snug">${escHtml(task.title)}</p>
        ${task.description ? `<p class="text-xs mt-1" style="color:var(--muted);">${escHtml(task.description)}</p>` : ""}
        <div class="flex flex-wrap gap-1.5 mt-2 items-center">
          <button onclick="cycleStatus(${task.id},'${task.status}')"
            class="badge-${task.status} text-xs px-2 py-0.5 rounded-full cursor-pointer font-medium hover:opacity-75"
            title="Click to advance status">${statusLabel(task.status)}</button>
          <span class="badge-${task.priority} text-xs px-2 py-0.5 rounded-full">${task.priority}</span>
          ${task.assignee ? `<span class="badge-assignee text-xs px-2 py-0.5 rounded-full">&#128100; ${escHtml(task.assignee)}</span>` : ""}
          ${labels}${wikiLink}${dueHtml}
        </div>
      </div>
      <div class="flex gap-2 mt-0.5 shrink-0">
        <button onclick="startEditTask(${task.id})" title="Edit"
          style="color:var(--border);" class="text-sm transition-colors"
          onmouseover="this.style.color='var(--action)'" onmouseout="this.style.color='var(--border)'">&#9998;</button>
        <button onclick="deleteTask(${task.id})" title="Delete"
          style="color:var(--border);" class="text-sm transition-colors"
          onmouseover="this.style.color='var(--rose)'" onmouseout="this.style.color='var(--border)'">&#10005;</button>
      </div>
    </div>
    <div class="px-5 py-2 flex gap-1 border-t" style="border-color:var(--border-soft);">
      <button class="btn-inline" onclick="toggleSection('comments',${task.id})">&#128172; Comments</button>
      <button class="btn-inline" onclick="toggleSection('history',${task.id})">&#128203; History</button>
    </div>
    <div id="task-comments-${task.id}" class="hidden border-t" style="border-color:var(--border-soft);">
      <div id="comments-list-${task.id}" class="px-5 pt-3 space-y-2"></div>
      <div class="px-5 py-3 space-y-2">
        <input  id="comment-author-${task.id}"  class="field text-xs" type="text" placeholder="Your name" />
        <textarea id="comment-content-${task.id}" class="field text-xs resize-none" rows="2" placeholder="Write a comment…"></textarea>
        <button class="btn-action" style="font-size:.75rem; padding:.25rem .85rem;"
          onclick="submitComment(${task.id})">Post</button>
      </div>
    </div>
    <div id="task-history-${task.id}" class="hidden px-5 py-3 border-t" style="border-color:var(--border-soft);">
      <div id="history-list-${task.id}"></div>
    </div>
  </div>`;
}

function taskEditCard(task) {
  const wikiOpts = (window._wikiPages || [])
    .map(p => `<option value="${p.id}" ${task.wiki_page_id === p.id ? "selected" : ""}>${escHtml(p.title)}</option>`)
    .join("");
  return `
  <div id="task-card-${task.id}" class="card px-5 py-4 space-y-3 shadow-sm">
    <p class="text-xs font-semibold" style="color:var(--action-hov);">Editing task #${task.id}</p>
    <div>
      <input class="field" id="et-title-${task.id}" type="text" value="${escAttr(task.title)}" placeholder="Title *" />
    </div>
    <textarea class="field resize-none" id="et-desc-${task.id}" rows="2" placeholder="Description">${escHtml(task.description || "")}</textarea>
    <input  class="field" id="et-labels-${task.id}" type="text" value="${escAttr(task.labels || "")}" placeholder="Labels (comma-separated)" />
    <div class="flex flex-wrap gap-2">
      <select class="field" id="et-status-${task.id}" style="width:auto;">
        ${["todo","in_progress","done"].map(s =>
          `<option value="${s}" ${task.status===s?"selected":""}>${statusLabel(s)}</option>`).join("")}
      </select>
      <select class="field" id="et-priority-${task.id}" style="width:auto;">
        ${["low","medium","high"].map(p =>
          `<option value="${p}" ${task.priority===p?"selected":""}>${p}</option>`).join("")}
      </select>
      <input class="field flex-1 min-w-28" id="et-assignee-${task.id}" type="text"
        value="${escAttr(task.assignee || "")}" placeholder="Assignee" list="assignees-list" />
      <input class="field" id="et-due-${task.id}" type="datetime-local"
        value="${toDatetimeLocal(task.due_at)}" style="width:auto;" title="Due date" />
      <select class="field" id="et-wiki-${task.id}" style="width:auto;">
        <option value="">No wiki page</option>${wikiOpts}
      </select>
    </div>
    <div class="flex gap-2 pt-1">
      <button class="btn-action" onclick="saveEditTask(${task.id})">Save</button>
      <button class="btn-ghost"  onclick="cancelEditTask(${task.id})">Cancel</button>
    </div>
  </div>`;
}

async function startEditTask(id) {
  if (!window._wikiPages) {
    const d = await apiFetch(`${WIKI_URL}/pages?page_size=100`);
    window._wikiPages = d.items;
  }
  const task = await apiFetch(`${TASKS_URL}/tasks/${id}`);
  document.getElementById(`task-card-${id}`).outerHTML = taskCard(task, true);
}

async function saveEditTask(id) {
  const titleEl = document.getElementById(`et-title-${id}`);
  if (!validateRequired(titleEl, "Title")) return;

  const wikiVal = document.getElementById(`et-wiki-${id}`).value;
  const dueVal  = document.getElementById(`et-due-${id}`).value;
  await apiFetch(`${TASKS_URL}/tasks/${id}`, {
    method: "PATCH",
    body: {
      title:        titleEl.value.trim(),
      description:  document.getElementById(`et-desc-${id}`).value     || null,
      labels:       document.getElementById(`et-labels-${id}`).value   || null,
      status:       document.getElementById(`et-status-${id}`).value,
      priority:     document.getElementById(`et-priority-${id}`).value,
      assignee:     document.getElementById(`et-assignee-${id}`).value || null,
      due_at:       dueVal ? new Date(dueVal).toISOString() : null,
      wiki_page_id: wikiVal ? parseInt(wikiVal) : null,
    },
  });
  loadTasks();
  loadAssignees();
}

async function cancelEditTask(id) {
  const task = await apiFetch(`${TASKS_URL}/tasks/${id}`);
  document.getElementById(`task-card-${id}`).outerHTML = taskCard(task);
}

async function cycleStatus(id, current) {
  const next = STATUS_CYCLE[(STATUS_CYCLE.indexOf(current) + 1) % STATUS_CYCLE.length];
  await apiFetch(`${TASKS_URL}/tasks/${id}`, { method: "PATCH", body: { status: next } });
  loadTasks();
}

// ── Wiki navigation from task ─────────────────────────────

function wikiPageTitle(id) {
  const page = (window._wikiPages || []).find(p => p.id === id);
  return page ? escHtml(page.title) : `#${id}`;
}

async function goToWikiPage(pageId) {
  showSection("wiki");
  // Wait for loadPages() to render, then scroll + expand
  await new Promise(r => setTimeout(r, 200));
  const card = document.getElementById(`page-card-${pageId}`);
  if (!card) return;
  card.scrollIntoView({ behavior: "smooth", block: "center" });
  const full = document.getElementById(`page-full-${pageId}`);
  if (full && full.classList.contains("hidden")) togglePage(pageId);
}

// ── Comments ──────────────────────────────────────────────

async function toggleSection(type, taskId) {
  const el = document.getElementById(`task-${type}-${taskId}`);
  const opening = el.classList.contains("hidden");
  el.classList.toggle("hidden");
  if (!opening) return;
  if (type === "comments") await loadComments(taskId);
  if (type === "history")  await loadHistory(taskId);
}

async function loadComments(taskId) {
  const data = await apiFetch(`${TASKS_URL}/tasks/${taskId}/comments`);
  const list = document.getElementById(`comments-list-${taskId}`);
  if (!data.items.length) {
    list.innerHTML = `<p class="text-xs italic pb-1" style="color:var(--muted);">No comments yet.</p>`;
    return;
  }
  list.innerHTML = data.items.map(c => `
    <div class="pb-2 border-b" style="border-color:var(--border-soft);">
      <div class="flex justify-between items-baseline">
        <span class="text-xs font-semibold" style="color:var(--action);">${escHtml(c.author)}</span>
        <span class="text-xs" style="color:var(--muted);">${formatDate(c.created_at)}</span>
      </div>
      <p class="text-xs mt-0.5">${escHtml(c.content)}</p>
    </div>`).join("");
}

async function submitComment(taskId) {
  const authorEl  = document.getElementById(`comment-author-${taskId}`);
  const contentEl = document.getElementById(`comment-content-${taskId}`);
  let ok = true;
  if (!validateRequired(authorEl,  "Name"))    ok = false;
  if (!validateRequired(contentEl, "Comment")) ok = false;
  if (!ok) return;
  await apiFetch(`${TASKS_URL}/tasks/${taskId}/comments`, {
    method: "POST", body: { author: authorEl.value.trim(), content: contentEl.value.trim() },
  });
  contentEl.value = "";
  clearFieldError(authorEl);
  clearFieldError(contentEl);
  await loadComments(taskId);
}

// ── History ───────────────────────────────────────────────

async function loadHistory(taskId) {
  const data = await apiFetch(`${TASKS_URL}/tasks/${taskId}/history`);
  const list = document.getElementById(`history-list-${taskId}`);
  if (!data.items.length) {
    list.innerHTML = `<p class="text-xs italic" style="color:var(--muted);">No history yet.</p>`;
    return;
  }
  list.innerHTML = data.items.map(h => `
    <div class="py-1.5 border-b text-xs flex items-baseline justify-between gap-2"
      style="border-color:var(--border-soft);">
      <div class="flex gap-2 flex-1 min-w-0 flex-wrap items-baseline">
        <span class="font-semibold" style="color:var(--muted); min-width:6rem;">${escHtml(h.field)}</span>
        <span style="color:var(--rose);">${escHtml(h.old_value ?? "—")}</span>
        <span style="color:var(--muted);">→</span>
        <span style="color:var(--green);">${escHtml(h.new_value ?? "—")}</span>
      </div>
      <span class="shrink-0" style="color:var(--muted);">${formatDate(h.changed_at)}</span>
    </div>`).join("");
}

// ── Tasks — create form ───────────────────────────────────

async function openTaskForm() {
  const sel = document.getElementById("task-wiki-page");
  sel.innerHTML = '<option value="">No wiki page</option>';
  try {
    const data = await apiFetch(`${WIKI_URL}/pages?page_size=100`);
    window._wikiPages = data.items;
    data.items.forEach(p => {
      const o = document.createElement("option");
      o.value = p.id; o.textContent = p.title; sel.appendChild(o);
    });
  } catch (_) {}

  const draft = JSON.parse(localStorage.getItem(DRAFT_KEY) || "{}");
  if (draft.title)       document.getElementById("task-title").value  = draft.title;
  if (draft.description) document.getElementById("task-desc").value   = draft.description;
  if (draft.labels)      document.getElementById("task-labels").value = draft.labels;
  document.getElementById("task-form").classList.remove("hidden");
}

function closeTaskForm() {
  document.getElementById("task-form").classList.add("hidden");
  clearFieldError(document.getElementById("task-title"));
  localStorage.removeItem(DRAFT_KEY);
}

function saveDraft() {
  localStorage.setItem(DRAFT_KEY, JSON.stringify({
    title:       document.getElementById("task-title").value,
    description: document.getElementById("task-desc").value,
    labels:      document.getElementById("task-labels").value,
  }));
}

async function submitTask() {
  const titleEl = document.getElementById("task-title");
  if (!validateRequired(titleEl, "Title")) return;

  const wikiVal = document.getElementById("task-wiki-page").value;
  const dueVal  = document.getElementById("task-due-at").value;
  await apiFetch(`${TASKS_URL}/tasks`, {
    method: "POST",
    body: {
      title:        titleEl.value.trim(),
      description:  document.getElementById("task-desc").value     || null,
      labels:       document.getElementById("task-labels").value   || null,
      status:       document.getElementById("task-status").value,
      priority:     document.getElementById("task-priority").value,
      assignee:     document.getElementById("task-assignee").value || null,
      due_at:       dueVal ? new Date(dueVal).toISOString() : null,
      wiki_page_id: wikiVal ? parseInt(wikiVal) : null,
    },
  });
  ["task-title","task-desc","task-labels","task-assignee","task-due-at"].forEach(id => {
    document.getElementById(id).value = "";
  });
  closeTaskForm();
  loadTasks();
  loadAssignees();
}

async function deleteTask(id) {
  await fetch(`${TASKS_URL}/tasks/${id}`, { method: "DELETE", headers: { "X-API-Key": API_KEY } });
  loadTasks();
}

// ── Wiki — list ───────────────────────────────────────────

async function loadPages() {
  const params = new URLSearchParams({ page_size: 100 });
  if (currentSearch.pages) params.set("q", currentSearch.pages);
  const data = await apiFetch(`${WIKI_URL}/pages?${params}`);
  window._wikiPages = data.items;
  const list = document.getElementById("pages-list");
  if (!data.items.length) { list.innerHTML = emptyState("No pages found."); return; }
  list.innerHTML = data.items.map(p => pageCard(p)).join("");
}

function pageCard(page, editMode = false) {
  if (editMode) return pageEditCard(page);

  const preview = page.content ? page.content.slice(0, 180) + (page.content.length > 180 ? "…" : "") : null;
  const rendered = page.content ? marked.parse(page.content) : null;

  return `
  <div id="page-card-${page.id}" class="card" style="overflow:hidden;">
    <div class="px-5 py-4 flex items-start gap-3 cursor-pointer card-hover" onclick="togglePage(${page.id})">
      <div class="flex-1 min-w-0">
        <p class="font-semibold text-sm">&#128196; ${escHtml(page.title)}</p>
        ${preview ? `<p id="page-preview-${page.id}" class="text-xs mt-1 font-mono" style="color:var(--muted);">${escHtml(preview)}</p>` : ""}
      </div>
      <div class="flex items-center gap-3 shrink-0 mt-0.5" onclick="event.stopPropagation()">
        <span id="toggle-icon-${page.id}" class="text-xs select-none" style="color:var(--muted);">&#9660;</span>
        <button onclick="startEditPage(${page.id})" title="Edit"
          style="color:var(--border);" class="text-sm transition-colors"
          onmouseover="this.style.color='var(--action)'" onmouseout="this.style.color='var(--border)'">&#9998;</button>
        <button onclick="deletePage(${page.id})" title="Delete"
          style="color:var(--border);" class="text-sm transition-colors"
          onmouseover="this.style.color='var(--rose)'" onmouseout="this.style.color='var(--border)'">&#10005;</button>
      </div>
    </div>
    <div id="page-full-${page.id}" class="hidden px-5 pb-5 border-t" style="border-color:var(--border-soft);">
      ${rendered
        ? `<div class="md-body mt-4">${rendered}</div>`
        : `<p class="text-xs mt-4 italic" style="color:var(--muted);">No content.</p>`}
    </div>
  </div>`;
}

function pageEditCard(page) {
  return `
  <div id="page-card-${page.id}" class="card px-5 py-4 space-y-3 shadow-sm">
    <p class="text-xs font-semibold" style="color:var(--action-hov);">Editing page #${page.id}</p>
    <div>
      <input class="field" id="ep-title-${page.id}" type="text" value="${escAttr(page.title)}" placeholder="Title *" />
    </div>
    <textarea class="field font-mono resize-none" id="ep-content-${page.id}" rows="10"
      placeholder="Content (markdown supported)">${escHtml(page.content || "")}</textarea>
    <div class="flex gap-2 pt-1">
      <button class="btn-action" onclick="saveEditPage(${page.id})">Save</button>
      <button class="btn-ghost"  onclick="cancelEditPage(${page.id})">Cancel</button>
    </div>
  </div>`;
}

async function startEditPage(id) {
  const page = await apiFetch(`${WIKI_URL}/pages/${id}`);
  document.getElementById(`page-card-${id}`).outerHTML = pageCard(page, true);
}

async function saveEditPage(id) {
  const titleEl = document.getElementById(`ep-title-${id}`);
  if (!validateRequired(titleEl, "Title")) return;
  await apiFetch(`${WIKI_URL}/pages/${id}`, {
    method: "PATCH",
    body: {
      title:   titleEl.value.trim(),
      content: document.getElementById(`ep-content-${id}`).value || null,
    },
  });
  loadPages();
}

async function cancelEditPage(id) {
  const page = await apiFetch(`${WIKI_URL}/pages/${id}`);
  document.getElementById(`page-card-${id}`).outerHTML = pageCard(page);
}

function togglePage(id) {
  const full    = document.getElementById(`page-full-${id}`);
  const icon    = document.getElementById(`toggle-icon-${id}`);
  const preview = document.getElementById(`page-preview-${id}`);
  const opening = full.classList.contains("hidden");
  full.classList.toggle("hidden", !opening);
  if (preview) preview.classList.toggle("hidden", opening);
  icon.innerHTML = opening ? "&#9650;" : "&#9660;";
}

// ── Wiki — create form ────────────────────────────────────

function openPageForm()  { document.getElementById("page-form").classList.remove("hidden"); }

function closePageForm() {
  document.getElementById("page-form").classList.add("hidden");
  clearFieldError(document.getElementById("page-title"));
}

async function submitPage() {
  const titleEl = document.getElementById("page-title");
  if (!validateRequired(titleEl, "Title")) return;
  await apiFetch(`${WIKI_URL}/pages`, {
    method: "POST",
    body: { title: titleEl.value.trim(), content: document.getElementById("page-content").value || null },
  });
  document.getElementById("page-title").value   = "";
  document.getElementById("page-content").value = "";
  closePageForm();
  loadPages();
}

async function deletePage(id) {
  await fetch(`${WIKI_URL}/pages/${id}`, { method: "DELETE", headers: { "X-API-Key": API_KEY } });
  loadPages();
}

// ── Helpers ───────────────────────────────────────────────

async function apiFetch(url, { method = "GET", body } = {}) {
  const opts = { method, headers: { "X-API-Key": API_KEY } };
  if (body) { opts.headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(body); }
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`${method} ${url} → ${res.status}`);
  if (res.status === 204) return null;
  return res.json();
}

function statusLabel(s) {
  return { todo: "Todo", in_progress: "In Progress", done: "Done" }[s] || s;
}

function formatDate(iso) {
  if (!iso) return "";
  // Treat naive datetimes from SQLite as UTC
  const utc = /[Z+]/.test(iso) ? iso : iso + "Z";
  return new Date(utc).toLocaleString("en-US", { month:"short", day:"numeric", hour:"2-digit", minute:"2-digit" });
}

function formatDue(due_at, status) {
  if (!due_at) return "";
  const utc = /[Z+]/.test(due_at) ? due_at : due_at + "Z";
  const d   = new Date(utc);
  const now = new Date();
  const fmt = d.toLocaleDateString("en-US", { month:"short", day:"numeric", year:"numeric" });
  if (status !== "done" && d < now)
    return `<span class="badge-overdue text-xs px-2 py-0.5 rounded-full">&#9888; ${fmt}</span>`;
  if (d.toDateString() === now.toDateString())
    return `<span class="badge-due-today text-xs px-2 py-0.5 rounded-full">Due today</span>`;
  return `<span class="badge-due text-xs px-2 py-0.5 rounded-full">Due ${fmt}</span>`;
}

function toDatetimeLocal(iso) {
  if (!iso) return "";
  // Treat naive datetimes from SQLite as UTC
  const utc = /[Z+]/.test(iso) ? iso : iso + "Z";
  const d = new Date(utc);
  const p = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
}

function escHtml(str) {
  return String(str ?? "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
function escAttr(str) { return escHtml(str); }

function emptyState(msg) {
  return `<div class="text-center py-12 rounded-2xl border border-dashed"
    style="border-color:var(--border); color:var(--muted);">
    <p class="text-sm italic">${msg}</p>
  </div>`;
}

// ── Init ──────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  // Draft auto-save
  ["task-title","task-desc","task-labels"].forEach(id =>
    document.getElementById(id)?.addEventListener("input", saveDraft));

  // Search inputs — use addEventListener so both typing and clear work reliably
  const searchTasks = document.getElementById("search-tasks");
  const searchPages = document.getElementById("search-pages");
  if (searchTasks) searchTasks.addEventListener("input", e => onTaskSearch(e.target.value));
  if (searchPages) searchPages.addEventListener("input", e => onPageSearch(e.target.value));

  // Login inputs: submit on Enter
  ["login-user", "login-pass"].forEach(id =>
    document.getElementById(id)?.addEventListener("keydown", e => {
      if (e.key === "Enter") tryLogin();
    }));

  if (API_KEY) {
    document.getElementById("login-screen").classList.add("hidden");
    document.getElementById("app").classList.remove("hidden");
    setTaskFilter("all");
    loadTasks();
    loadAssignees();
  } else {
    document.getElementById("login-screen").classList.remove("hidden");
    document.getElementById("app").classList.add("hidden");
  }
});
