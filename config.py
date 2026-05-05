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
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'gecky.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Debug ─────────────────────────────────────────────────────────────────
    DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
