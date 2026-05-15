"""
app.py — Gecky application entry point
=======================================
Usage (development):
    python app.py

Usage (production):
    gunicorn "app:create_app()"
"""
from flask import Flask

from config import Config
from models.database import db
from routes.api import api_bp
from routes.views import views_bp


def create_app(config_class: type = Config) -> Flask:
    """Application factory — instantiates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    # ── Database bootstrap ─────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _migrate_add_user_token()

    return app


def _migrate_add_user_token() -> None:
    """Add user_token column to workspaces if it doesn't exist (one-time migration)."""
    from sqlalchemy import text

    with db.engine.connect() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(workspaces)"))]
        if "user_token" not in cols:
            conn.execute(
                text("ALTER TABLE workspaces ADD COLUMN user_token VARCHAR(36) NOT NULL DEFAULT ''")
            )
            conn.commit()


def _seed_default_workspace() -> None:
    """No-op: workspaces are created per-user token, not at startup."""
    pass


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
