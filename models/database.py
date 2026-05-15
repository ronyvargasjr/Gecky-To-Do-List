"""
models/database.py — SQLAlchemy models
=======================================
Defines the three core tables:
  • Workspace  — a named board that groups gecks
  • Geck       — a task card belonging to a workspace
  • Todo       — a checklist item belonging to a geck
"""
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now():
    """UTC timestamp helper (timezone-aware)."""
    return datetime.now(timezone.utc)


# ── Models ────────────────────────────────────────────────────────────────────

class Workspace(db.Model):
    __tablename__ = "workspaces"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False, default="My Board")
    user_token = db.Column(db.String(36), nullable=False, index=True, default="")
    created_at = db.Column(db.DateTime, default=_now)

    # Cascade deletes gecks (and their todos) when the workspace is removed
    gecks = db.relationship(
        "Geck", backref="workspace", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id":         self.id,
            "name":       self.name,
            "created_at": self.created_at.isoformat(),
        }


class Geck(db.Model):
    __tablename__ = "gecks"

    id           = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey("workspaces.id"), nullable=False)
    title        = db.Column(db.String(200), nullable=False)
    # Absolute pixel position on the board canvas
    pos_x        = db.Column(db.Integer, default=50)
    pos_y        = db.Column(db.Integer, default=50)
    # Background colour of the sticky note (hex)
    color        = db.Column(db.String(20), default="#fef08a")
    created_at   = db.Column(db.DateTime, default=_now)

    # Cascade deletes todos when the geck is removed
    todos = db.relationship(
        "Todo", backref="geck", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        sorted_todos = sorted(self.todos, key=lambda t: t.position)
        return {
            "id":           self.id,
            "workspace_id": self.workspace_id,
            "title":        self.title,
            "pos_x":        self.pos_x,
            "pos_y":        self.pos_y,
            "color":        self.color,
            "created_at":   self.created_at.isoformat(),
            "todos":        [t.to_dict() for t in sorted_todos],
        }


class Todo(db.Model):
    __tablename__ = "todos"

    id         = db.Column(db.Integer, primary_key=True)
    geck_id    = db.Column(db.Integer, db.ForeignKey("gecks.id"), nullable=False)
    text       = db.Column(db.String(500), nullable=False)
    completed  = db.Column(db.Boolean, default=False, nullable=False)
    # Used to preserve insertion order
    position   = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=_now)

    def to_dict(self):
        return {
            "id":        self.id,
            "geck_id":   self.geck_id,
            "text":      self.text,
            "completed": self.completed,
            "position":  self.position,
        }
