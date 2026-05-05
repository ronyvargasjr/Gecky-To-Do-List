/**
 * drag.js — Draggable geck cards
 * ─────────────────────────────────────────────────────────────────────────────
 * Implements click-and-drag movement for .geck elements.
 * After a drag ends, the new position is persisted via PUT /api/gecks/<id>.
 *
 * Public API (consumed by main.js):
 *   makeDraggable(el)  — attach drag behaviour to a geck DOM element
 */

/** @type {{ el: HTMLElement, board: HTMLElement, offsetX: number, offsetY: number, moved: boolean, finalX: number, finalY: number } | null} */
let _dragState = null;

/**
 * Attach drag listeners to a single geck element.
 * @param {HTMLElement} el  The .geck element to make draggable.
 */
function makeDraggable(el) {
  el.addEventListener('mousedown', _onDragStart);
}

// ── Internal handlers ─────────────────────────────────────────────────────────

function _onDragStart(e) {
  // Only handle primary (left) mouse button
  if (e.button !== 0) return;
  // Don't hijack clicks on interactive children (delete button, etc.)
  if (e.target.closest('button, input, textarea')) return;

  const el    = e.currentTarget;
  const board = document.getElementById('board');
  const elRect = el.getBoundingClientRect();

  _dragState = {
    el,
    board,
    // Offset of the cursor within the card at the moment of mousedown
    offsetX : e.clientX - elRect.left,
    offsetY : e.clientY - elRect.top,
    moved   : false,
    finalX  : parseInt(el.style.left, 10) || 0,
    finalY  : parseInt(el.style.top,  10) || 0,
  };

  el.classList.add('dragging');
  document.addEventListener('mousemove', _onDragMove);
  document.addEventListener('mouseup',   _onDragEnd);
  e.preventDefault(); // prevent text selection while dragging
}

function _onDragMove(e) {
  if (!_dragState) return;

  const { el, board, offsetX, offsetY } = _dragState;
  const boardRect = board.getBoundingClientRect();

  // Position relative to the board canvas, accounting for scroll
  let x = e.clientX - boardRect.left - offsetX + board.scrollLeft;
  let y = e.clientY - boardRect.top  - offsetY + board.scrollTop;

  // Clamp: keep card fully inside the visible board (minimum 0,0)
  x = Math.max(0, x);
  y = Math.max(0, y);

  el.style.left = `${x}px`;
  el.style.top  = `${y}px`;

  _dragState.moved  = true;
  _dragState.finalX = x;
  _dragState.finalY = y;
}

function _onDragEnd() {
  if (!_dragState) return;

  const { el, moved, finalX, finalY } = _dragState;

  el.classList.remove('dragging');

  if (moved) {
    _savePosition(el.dataset.id, Math.round(finalX), Math.round(finalY));
  }

  document.removeEventListener('mousemove', _onDragMove);
  document.removeEventListener('mouseup',   _onDragEnd);
  _dragState = null;
}

/**
 * Persist the geck's new position to the server.
 * Failures are non-fatal — the card has already moved visually.
 *
 * @param {string|number} geckId
 * @param {number}        x       New left position in pixels.
 * @param {number}        y       New top position in pixels.
 */
async function _savePosition(geckId, x, y) {
  try {
    const res = await fetch(`/api/gecks/${geckId}`, {
      method  : 'PUT',
      headers : { 'Content-Type': 'application/json' },
      body    : JSON.stringify({ pos_x: x, pos_y: y }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  } catch (err) {
    // Position will re-sync on next full page load
    console.warn('[Gecky] Could not save geck position:', err);
  }
}
