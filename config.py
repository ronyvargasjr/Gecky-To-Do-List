"""
config.py — Gecky application configuration
============================================
Centralised settings. Override via environment variables in production.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # ── Database ──────────────────────────────────────────────────────────────
    _db_url = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'gecky.db')}",
    )
    # Railway / Render / Heroku may supply the legacy postgres:// scheme;
    # SQLAlchemy 1.4+ requires postgresql://
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Debug ─────────────────────────────────────────────────────────────────
    DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
