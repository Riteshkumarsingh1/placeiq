from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import College
from sqlalchemy import or_, and_

colleges_bp = Blueprint("colleges", __name__)


def _err(msg, code=400):
    return jsonify({"error": msg}), code


# ── GET /api/colleges ─────────────────────────────────────────
# Query params: q, stream, state, fees, tier, page, per_page
@colleges_bp.route("", methods=["GET"])
def list_colleges():
    q        = request.args.get("q", "").strip()
    stream   = request.args.get("stream", "")
    state    = request.args.get("state", "")
    fees     = request.args.get("fees", "")          # low / mid / high
    tier     = request.args.get("tier", "")
    page     = max(1, int(request.args.get("page", 1)))
    per_page = request.args.get("per_page", type=int) or College.query.count()

    query = College.query

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                College.name.ilike(like),
                College.city.ilike(like),
                College.state.ilike(like),
            )
        )

    if stream:
        query = query.filter(College.stream == stream)

    if state:
        query = query.filter(College.state == state)

    if fees == "low":
        query = query.filter(College.fees_per_year < 5)
    elif fees == "mid":
        query = query.filter(and_(College.fees_per_year >= 5, College.fees_per_year <= 12))
    elif fees == "high":
        query = query.filter(College.fees_per_year > 12)

    if tier:
        query = query.filter(College.tier == int(tier))

    total = query.count()
    colleges = query.order_by(College.nirf_rank.asc().nullslast()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "colleges":  [c.to_dict() for c in colleges.items],
        "total":     total,
        "page":      page,
        "per_page":  per_page,
        "pages":     colleges.pages,
    })


# ── GET /api/colleges/<id> ────────────────────────────────────
@colleges_bp.route("/<int:college_id>", methods=["GET"])
def get_college(college_id):
    college = db.session.get(College, college_id)
    if not college:
        return _err("College not found.", 404)
    return jsonify(college.to_dict())


# ── GET /api/colleges/compare?ids=1,2,3,4 ────────────────────
@colleges_bp.route("/compare", methods=["GET"])
def compare_colleges():
    raw = request.args.get("ids", "")
    try:
        ids = [int(x) for x in raw.split(",") if x.strip()]
    except ValueError:
        return _err("ids must be comma-separated integers.")

    if not ids:
        return _err("Provide at least 2 college ids.")
    if len(ids) > 4:
        return _err("Maximum 4 colleges can be compared at once.")

    colleges = College.query.filter(College.id.in_(ids)).all()
    if len(colleges) < 2:
        return _err("Could not find enough colleges for comparison.")

    data = [c.to_dict() for c in colleges]

    # Auto-highlight best values per numeric metric
    metrics = ["avg_ctc", "highest_ctc", "placement_pct", "nirf_rank", "fees_per_year"]
    higher_is_better = {"avg_ctc", "highest_ctc", "placement_pct"}
    lower_is_better  = {"nirf_rank", "fees_per_year"}

    highlights = {}
    for m in metrics:
        values = {str(c["id"]): c.get(m) for c in data if c.get(m) is not None}
        if not values:
            continue
        if m in higher_is_better:
            best_id = max(values, key=values.get)
        else:
            best_id = min(values, key=values.get)
        highlights[m] = best_id

    return jsonify({"colleges": data, "highlights": highlights})


# ── POST /api/colleges  (admin only) ─────────────────────────
@colleges_bp.route("", methods=["POST"])
@jwt_required()
def create_college():
    from models import User
    from flask_jwt_extended import get_jwt_identity
    user = db.session.get(User, int(get_jwt_identity()))
    if not user or user.role != "admin":
        return _err("Admin access required.", 403)

    data = request.get_json(silent=True) or {}
    required = ["name", "state", "stream"]
    for f in required:
        if not data.get(f):
            return _err(f"'{f}' is required.")

    college = College(**{
        k: data.get(k) for k in [
            "name", "city", "state", "stream", "tier",
            "nirf_rank", "fees_per_year", "avg_ctc",
            "highest_ctc", "placement_pct", "top_recruiters",
            "established", "accreditation", "website"
        ]
    })
    db.session.add(college)
    db.session.commit()
    return jsonify(college.to_dict()), 201


# ── PATCH /api/colleges/<id>  (admin only) ────────────────────
@colleges_bp.route("/<int:college_id>", methods=["PATCH"])
@jwt_required()
def update_college(college_id):
    from models import User
    from flask_jwt_extended import get_jwt_identity
    user = db.session.get(User, int(get_jwt_identity()))
    if not user or user.role != "admin":
        return _err("Admin access required.", 403)

    college = db.session.get(College, college_id)
    if not college:
        return _err("College not found.", 404)

    data = request.get_json(silent=True) or {}
    updatable = [
        "name", "city", "state", "stream", "tier",
        "nirf_rank", "fees_per_year", "avg_ctc",
        "highest_ctc", "placement_pct", "top_recruiters",
        "established", "accreditation", "website"
    ]
    for field in updatable:
        if field in data:
            setattr(college, field, data[field])

    db.session.commit()
    return jsonify(college.to_dict())
