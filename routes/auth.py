from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from extensions import db
from models import User
import re

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _err(msg, code=400):
    return jsonify({"error": msg}), code


# ── POST /api/auth/register ───────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name   = (data.get("name") or "").strip()
    email  = (data.get("email") or "").strip().lower()
    pw     = (data.get("password") or "")
    stream = (data.get("stream") or "").strip()

    # Validation
    if not name:
        return _err("Name is required.")
    if not EMAIL_RE.match(email):
        return _err("Invalid email address.")
    if len(pw) < 8:
        return _err("Password must be at least 8 characters.")
    
    # Normalize stream values - Accept various input formats
    stream_mapping = {
        "engineering (b.tech)": "Engineering",
        "b.tech": "Engineering",
        "btech": "Engineering",
        "engineering": "Engineering",
        "mba / management": "MBA",
        "mba": "MBA",
        "m.tech / ms": "M.Tech",
        "m.tech": "M.Tech",
        "ms": "M.Tech",
        "mca": "MCA"
    }
    
    stream_lower = stream.lower()
    if stream_lower in stream_mapping:
        stream = stream_mapping[stream_lower]
    elif stream not in ("Engineering", "MBA", "MCA", "M.Tech", ""):
        return _err("Stream must be Engineering, MBA, M.Tech, or MCA.")

    if User.query.filter_by(email=email).first():
        return _err("An account with this email already exists.", 409)

    user = User(name=name, email=email, stream=stream or None)
    user.set_password(pw)
    db.session.add(user)
    db.session.commit()

    access  = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Account created.",
        "user":    user.to_dict(),
        "access_token":  access,
        "refresh_token": refresh,
    }), 201


# ── POST /api/auth/login ──────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data  = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    pw    = (data.get("password") or "")

    if not email or not pw:
        return _err("Email and password are required.")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(pw):
        return _err("Invalid email or password.", 401)

    access  = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful.",
        "user":    user.to_dict(),
        "access_token":  access,
        "refresh_token": refresh,
    })


# ── POST /api/auth/refresh ────────────────────────────────────
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access   = create_access_token(identity=identity)
    return jsonify({"access_token": access})


# ── GET  /api/auth/me ─────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return _err("User not found.", 404)
    return jsonify({"user": user.to_dict()})


# ── PATCH /api/auth/me ────────────────────────────────────────
@auth_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return _err("User not found.", 404)

    data = request.get_json(silent=True) or {}
    if "name" in data:
        user.name = data["name"].strip() or user.name
    
    # Update stream with mapping support
    if "stream" in data:
        new_stream = data["stream"].strip()
        stream_mapping = {
            "engineering (b.tech)": "Engineering",
            "b.tech": "Engineering",
            "btech": "Engineering",
            "engineering": "Engineering",
            "mba / management": "MBA",
            "mba": "MBA",
            "m.tech / ms": "M.Tech",
            "m.tech": "M.Tech",
            "ms": "M.Tech",
            "mca": "MCA"
        }
        stream_lower = new_stream.lower()
        if stream_lower in stream_mapping:
            new_stream = stream_mapping[stream_lower]
        
        if new_stream in ("Engineering", "MBA", "MCA", "M.Tech"):
            user.stream = new_stream

    db.session.commit()
    return jsonify({"user": user.to_dict()})