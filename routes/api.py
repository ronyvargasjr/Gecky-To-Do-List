"""
routes/api.py — REST API blueprint
====================================
Endpoints:
  Workspaces
    GET    /api/workspaces
    POST   /api/workspaces
    DELETE /api/workspaces/<id>

  Gecks
    POST   /api/gecks
    GET    /api/gecks/<workspace_id>
    PUT    /api/gecks/<id>
    DELETE /api/gecks/<id>

  AI
    POST   /api/ai/generate
"""
from flask import Blueprint, abort, jsonify, request

from models.database import Geck, Workspace, db
from services.ai_agent import generate_tasks

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ── Workspaces ────────────────────────────────────────────────────────────────

@api_bp.route("/workspaces", methods=["GET"])
def get_workspaces():
    workspaces = Workspace.query.all()
    return jsonify([w.to_dict() for w in workspaces])


@api_bp.route("/workspaces", methods=["POST"])
def create_workspace():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    workspace = Workspace(name=name)
    db.session.add(workspace)
    db.session.commit()
    return jsonify(workspace.to_dict()), 201


@api_bp.route("/workspaces/<int:workspace_id>", methods=["DELETE"])
def delete_workspace(workspace_id):
    workspace = db.get_or_404(Workspace, workspace_id)
    db.session.delete(workspace)
    db.session.commit()
    return jsonify({"message": "Workspace deleted"}), 200


# ── Gecks ─────────────────────────────────────────────────────────────────────

@api_bp.route("/gecks", methods=["POST"])
def create_geck():
    data = request.get_json(silent=True) or {}
    workspace_id = data.get("workspace_id")
    title = str(data.get("title", "")).strip()

    if not workspace_id or not title:
        return jsonify({"error": "workspace_id and title are required"}), 400

    # Validate workspace exists
    db.get_or_404(Workspace, workspace_id)

    geck = Geck(
        workspace_id=workspace_id,
        title=title,
        description=str(data.get("description", "")),
        pos_x=int(data.get("pos_x", 50)),
        pos_y=int(data.get("pos_y", 50)),
        color=str(data.get("color", "#fef08a")),
    )
    db.session.add(geck)
    db.session.commit()
    return jsonify(geck.to_dict()), 201


@api_bp.route("/gecks/<int:workspace_id>", methods=["GET"])
def get_gecks(workspace_id):
    db.get_or_404(Workspace, workspace_id)
    gecks = Geck.query.filter_by(workspace_id=workspace_id).all()
    return jsonify([g.to_dict() for g in gecks])


@api_bp.route("/gecks/<int:geck_id>", methods=["PUT"])
def update_geck(geck_id):
    geck = db.get_or_404(Geck, geck_id)
    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = str(data["title"]).strip()
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400
        geck.title = title

    if "description" in data:
        geck.description = str(data["description"])

    if "pos_x" in data:
        geck.pos_x = int(data["pos_x"])

    if "pos_y" in data:
        geck.pos_y = int(data["pos_y"])

    if "color" in data:
        geck.color = str(data["color"])

    db.session.commit()
    return jsonify(geck.to_dict())


@api_bp.route("/gecks/<int:geck_id>", methods=["DELETE"])
def delete_geck(geck_id):
    geck = db.get_or_404(Geck, geck_id)
    db.session.delete(geck)
    db.session.commit()
    return jsonify({"message": "Geck deleted"}), 200


# ── AI ────────────────────────────────────────────────────────────────────────

@api_bp.route("/ai/generate", methods=["POST"])
def ai_generate():
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    workspace_id = data.get("workspace_id")

    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    if not workspace_id:
        return jsonify({"error": "workspace_id is required"}), 400

    db.get_or_404(Workspace, workspace_id)

    task_titles = generate_tasks(prompt)
    created: list[Geck] = []

    for i, title in enumerate(task_titles):
        geck = Geck(
            workspace_id=workspace_id,
            title=title,
            description="",
            # Lay cards out in a grid: 4 columns, 230 px wide, 200 px tall
            pos_x=50 + (i % 4) * 230,
            pos_y=50 + (i // 4) * 200,
        )
        db.session.add(geck)
        created.append(geck)

    db.session.commit()
    return jsonify([g.to_dict() for g in created]), 201
