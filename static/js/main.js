/**
 * main.js — Gecky frontend controller
 * ─────────────────────────────────────────────────────────────────────────────
 * Responsibilities:
 *   • Sidebar: toggle collapse, create / switch / delete workspaces
 *   • Board:   open modal, create / render / delete gecks
 *   • AI panel: send prompt to /api/ai/generate, render returned gecks
 *
 * Depends on:  drag.js  (must be loaded first — provides makeDraggable)
 * Bootstrap:   window.GECKY  (injected by Jinja2 in index.html)
 */

'use strict';

// ── State ─────────────────────────────────────────────────────────────────────
let activeWorkspaceId = window.GECKY?.activeWorkspaceId ?? null;

// ── DOM references ────────────────────────────────────────────────────────────
const sidebar          = document.getElementById('sidebar');
const toggleSidebarBtn = document.getElementById('toggle-sidebar');
const workspaceList    = document.getElementById('workspace-list');
const newWorkspaceBtn  = document.getElementById('new-workspace-btn');
const workspaceTitle   = document.getElementById('workspace-title');

const board            = document.getElementById('board');
const addGeckBtn       = document.getElementById('add-geck-btn');

const geckModal        = document.getElementById('geck-modal');
const geckTitleInput   = document.getElementById('geck-title-input');
const geckDescInput    = document.getElementById('geck-desc-input');
const saveGeckBtn      = document.getElementById('save-geck-btn');
const cancelGeckBtn    = document.getElementById('cancel-geck-btn');

const aiPrompt         = document.getElementById('ai-prompt');
const askGeckyBtn      = document.getElementById('ask-gecky-btn');

// ── Boot ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  _bindSidebar();
  _bindBoard();
  _bindModal();
  _bindAiPanel();

  // Make gecks that were server-rendered draggable
  document.querySelectorAll('.geck').forEach(makeDraggable);
});

// ═════════════════════════════════════════════════════════════════════════════
// SIDEBAR
// ═════════════════════════════════════════════════════════════════════════════

function _bindSidebar() {
  // Collapse / expand
  toggleSidebarBtn.addEventListener('click', () => {
    const collapsed = document.body.classList.toggle('sidebar-collapsed');
    toggleSidebarBtn.textContent       = collapsed ? '▶' : '◀';
    toggleSidebarBtn.title             = collapsed ? 'Expand sidebar' : 'Collapse sidebar';
  });

  // Create workspace
  newWorkspaceBtn.addEventListener('click', async () => {
    const name = _promptUser('Workspace name:');
    if (!name) return;
    try {
      const res = await fetch('/api/workspaces', {
        method  : 'POST',
        headers : { 'Content-Type': 'application/json' },
        body    : JSON.stringify({ name }),
      });
      if (!res.ok) throw new Error(await res.text());
      const ws = await res.json();
      _appendWorkspaceItem(ws);
      _switchWorkspace(ws.id, ws.name);
      showToast('Workspace created', 'success');
    } catch {
      showToast('Could not create workspace', 'error');
    }
  });

  // Delegate: switch / delete workspace
  workspaceList.addEventListener('click', async (e) => {
    const deleteBtn = e.target.closest('.delete-workspace-btn');
    const item      = e.target.closest('.workspace-item');

    if (deleteBtn) {
      e.stopPropagation();
      if (!confirm('Delete this workspace and all its gecks?')) return;
      const wsId = Number(deleteBtn.dataset.id);
      try {
        const res = await fetch(`/api/workspaces/${wsId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error();
        item.remove();

        // If we deleted the active workspace, try to show the next one
        if (wsId === activeWorkspaceId) {
          const next = workspaceList.querySelector('.workspace-item');
          if (next) {
            _switchWorkspace(
              Number(next.dataset.workspaceId),
              next.querySelector('.workspace-name').textContent.trim(),
            );
          } else {
            activeWorkspaceId       = null;
            workspaceTitle.textContent = 'No Workspace';
            board.innerHTML           = '';
          }
        }
        showToast('Workspace deleted', 'success');
      } catch {
        showToast('Could not delete workspace', 'error');
      }
      return;
    }

    if (item) {
      _switchWorkspace(
        Number(item.dataset.workspaceId),
        item.querySelector('.workspace-name').textContent.trim(),
      );
    }
  });
}

/** Add a workspace <li> to the sidebar list. */
function _appendWorkspaceItem(ws) {
  const li = document.createElement('li');
  li.className              = 'workspace-item';
  li.dataset.workspaceId    = ws.id;
  li.innerHTML = `
    <span class="workspace-name">${_esc(ws.name)}</span>
    <button class="delete-workspace-btn" data-id="${ws.id}" title="Delete workspace" aria-label="Delete ${_esc(ws.name)}">✕</button>
  `;
  workspaceList.appendChild(li);
}

/** Load and display gecks for the selected workspace. */
async function _switchWorkspace(wsId, wsName) {
  activeWorkspaceId      = wsId;
  workspaceTitle.textContent = wsName;

  // Highlight active item in sidebar
  workspaceList.querySelectorAll('.workspace-item').forEach((el) => {
    el.classList.toggle('active', Number(el.dataset.workspaceId) === wsId);
  });

  try {
    const res = await fetch(`/api/gecks/${wsId}`);
    if (!res.ok) throw new Error();
    const gecks = await res.json();
    board.innerHTML = '';
    gecks.forEach(renderGeck);
  } catch {
    showToast('Could not load gecks', 'error');
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// BOARD
// ═════════════════════════════════════════════════════════════════════════════

function _bindBoard() {
  // Open the new-geck modal
  addGeckBtn.addEventListener('click', () => {
    if (!activeWorkspaceId) {
      showToast('Create a workspace first', 'error');
      return;
    }
    _openModal();
  });

  // Delegate geck delete clicks
  board.addEventListener('click', async (e) => {
    const btn = e.target.closest('.geck-delete');
    if (!btn) return;
    const geckId = btn.dataset.id;
    try {
      const res = await fetch(`/api/gecks/${geckId}`, { method: 'DELETE' });
      if (!res.ok) throw new Error();
      document.getElementById(`geck-${geckId}`)?.remove();
    } catch {
      showToast('Could not delete geck', 'error');
    }
  });
}

/** Create a geck via the API and render it on the board. */
async function createGeck(title, description = '', posX = null, posY = null) {
  const existing = board.querySelectorAll('.geck');
  const x = posX ?? (50 + (existing.length % 4) * 230);
  const y = posY ?? (50 + Math.floor(existing.length / 4) * 200);

  try {
    const res = await fetch('/api/gecks', {
      method  : 'POST',
      headers : { 'Content-Type': 'application/json' },
      body    : JSON.stringify({
        workspace_id: activeWorkspaceId,
        title,
        description,
        pos_x: x,
        pos_y: y,
      }),
    });
    if (!res.ok) throw new Error(await res.text());
    const geck = await res.json();
    renderGeck(geck);
    return geck;
  } catch {
    showToast('Could not create geck', 'error');
    return null;
  }
}

/**
 * Build a geck DOM element, add it to the board, and make it draggable.
 * @param {{ id, title, description, pos_x, pos_y, color }} geck
 */
function renderGeck(geck) {
  const el = document.createElement('div');
  el.className    = 'geck';
  el.id           = `geck-${geck.id}`;
  el.dataset.id   = geck.id;
  el.style.left   = `${geck.pos_x}px`;
  el.style.top    = `${geck.pos_y}px`;
  el.style.background = geck.color || '#fef08a';
  el.setAttribute('role', 'article');
  el.setAttribute('aria-label', `Task: ${geck.title}`);

  el.innerHTML = `
    <div class="geck-header">
      <span class="geck-title">${_esc(geck.title)}</span>
      <button class="geck-delete" data-id="${geck.id}" title="Delete geck" aria-label="Delete geck">✕</button>
    </div>
    <div class="geck-body">
      <p class="geck-description">${_esc(geck.description || '')}</p>
    </div>
  `;

  board.appendChild(el);
  makeDraggable(el);
  return el;
}

// ═════════════════════════════════════════════════════════════════════════════
// NEW GECK MODAL
// ═════════════════════════════════════════════════════════════════════════════

function _bindModal() {
  cancelGeckBtn.addEventListener('click', _closeModal);

  // Close on backdrop click
  geckModal.addEventListener('click', (e) => {
    if (e.target === geckModal) _closeModal();
  });

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !geckModal.classList.contains('hidden')) _closeModal();
  });

  // Save on Enter inside the title input
  geckTitleInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); _submitModal(); }
  });

  saveGeckBtn.addEventListener('click', _submitModal);
}

function _openModal() {
  geckTitleInput.value  = '';
  geckDescInput.value   = '';
  geckModal.classList.remove('hidden');
  geckTitleInput.focus();
}

function _closeModal() {
  geckModal.classList.add('hidden');
}

async function _submitModal() {
  const title = geckTitleInput.value.trim();
  if (!title) {
    geckTitleInput.focus();
    return;
  }
  const description = geckDescInput.value.trim();
  _closeModal();
  await createGeck(title, description);
}

// ═════════════════════════════════════════════════════════════════════════════
// AI PANEL
// ═════════════════════════════════════════════════════════════════════════════

function _bindAiPanel() {
  askGeckyBtn.addEventListener('click', _handleAskGecky);
  aiPrompt.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') _handleAskGecky();
  });
}

async function _handleAskGecky() {
  const promptText = aiPrompt.value.trim();
  if (!promptText) return;

  if (!activeWorkspaceId) {
    showToast('Select a workspace first', 'error');
    return;
  }

  askGeckyBtn.disabled    = true;
  askGeckyBtn.textContent = 'Thinking…';

  try {
    const res = await fetch('/api/ai/generate', {
      method  : 'POST',
      headers : { 'Content-Type': 'application/json' },
      body    : JSON.stringify({ prompt: promptText, workspace_id: activeWorkspaceId }),
    });
    if (!res.ok) throw new Error(await res.text());

    const gecks = await res.json();
    gecks.forEach(renderGeck);
    aiPrompt.value = '';
    showToast(`${gecks.length} geck${gecks.length !== 1 ? 's' : ''} created by Gecky AI`, 'success');
  } catch {
    showToast('AI generation failed', 'error');
  } finally {
    askGeckyBtn.disabled    = false;
    askGeckyBtn.textContent = 'Ask Gecky';
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// UTILITIES
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Escape a string for safe HTML insertion.
 * @param {string} str
 * @returns {string}
 */
function _esc(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

/**
 * Prompt the user for text input, returning a non-empty trimmed string or null.
 * @param {string} message
 * @returns {string|null}
 */
function _promptUser(message) {
  const val = window.prompt(message);
  return val && val.trim() ? val.trim() : null;
}

/**
 * Show a transient toast notification.
 * @param {string}            msg
 * @param {'success'|'error'} type
 */
function showToast(msg, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast     = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3200);
}
