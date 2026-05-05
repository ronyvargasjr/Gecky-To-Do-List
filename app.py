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
        _seed_default_workspace()

    return app


def _seed_default_workspace() -> None:
    """Insert a default workspace on first run so the UI is never empty."""
    from models.database import Workspace  # local import avoids circular refs

    if Workspace.query.count() == 0:
        db.session.add(Workspace(name="My Board"))
        db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
