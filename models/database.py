"""
models/database.py — SQLAlchemy models
=======================================
Defines the two core tables:
  • Workspace  — a named board that groups gecks
  • Geck       — a task card belonging to a workspace
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
    created_at = db.Column(db.DateTime, default=_now)

    # Cascade deletes gecks when the workspace is removed
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
    description  = db.Column(db.Text, default="")
    # Absolute pixel position on the board canvas
    pos_x        = db.Column(db.Integer, default=50)
    pos_y        = db.Column(db.Integer, default=50)
    # Background colour of the sticky note (hex)
    color        = db.Column(db.String(20), default="#fef08a")
    created_at   = db.Column(db.DateTime, default=_now)

    def to_dict(self):
        return {
            "id":           self.id,
            "workspace_id": self.workspace_id,
            "title":        self.title,
            "description":  self.description,
            "pos_x":        self.pos_x,
            "pos_y":        self.pos_y,
            "color":        self.color,
            "created_at":   self.created_at.isoformat(),
        }
