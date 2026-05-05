"""
routes/views.py — Page rendering blueprint
===========================================
Serves the main SPA shell.  Initial workspace + gecks are injected into the
template so the page renders without an extra round-trip.
"""
import json

from flask import Blueprint, render_template

from models.database import Geck, Workspace

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    """Render the Gecky board page."""
    workspaces = Workspace.query.order_by(Workspace.created_at).all()

    # Show the first workspace by default
    active_workspace = workspaces[0] if workspaces else None

    gecks = (
        Geck.query.filter_by(workspace_id=active_workspace.id).all()
        if active_workspace
        else []
    )

    return render_template(
        "index.html",
        workspaces=workspaces,
        active_workspace=active_workspace,
        gecks=gecks,
        # Pre-serialised JSON for the JS bootstrap block
        workspaces_json=json.dumps([w.to_dict() for w in workspaces]),
        gecks_json=json.dumps([g.to_dict() for g in gecks]),
    )
