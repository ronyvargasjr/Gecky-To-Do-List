"""
routes/views.py — Page rendering blueprint
===========================================
Serves the main SPA shell.  Initial workspace + gecks are injected into the
template so the page renders without an extra round-trip.

Each visitor is identified by a UUID stored in a secure HttpOnly cookie
(gecky_token).  Only workspaces owned by that token are visible.
"""
import json
import uuid

from flask import Blueprint, current_app, make_response, render_template, request

from models.database import Geck, Workspace

views_bp = Blueprint("views", __name__)

_COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # 1 year in seconds


def _is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


@views_bp.route("/")
def index():
    """Render the Gecky board page."""
    token = request.cookies.get("gecky_token", "")
    is_new_token = not _is_valid_uuid(token)
    if is_new_token:
        token = str(uuid.uuid4())

    workspaces = (
        Workspace.query.filter_by(user_token=token)
        .order_by(Workspace.created_at)
        .all()
    )

    # Show the first workspace by default
    active_workspace = workspaces[0] if workspaces else None

    gecks = (
        Geck.query.filter_by(workspace_id=active_workspace.id).all()
        if active_workspace
        else []
    )

    resp = make_response(render_template(
        "index.html",
        workspaces=workspaces,
        active_workspace=active_workspace,
        gecks=gecks,
        # Pre-serialised JSON for the JS bootstrap block
        workspaces_json=json.dumps([w.to_dict() for w in workspaces]),
        gecks_json=json.dumps([g.to_dict() for g in gecks]),
    ))

    if is_new_token:
        resp.set_cookie(
            "gecky_token",
            token,
            max_age=_COOKIE_MAX_AGE,
            httponly=True,
            samesite="Lax",
            secure=not current_app.debug,
        )

    return resp
