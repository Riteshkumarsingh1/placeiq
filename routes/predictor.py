from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from routes.ml import _ctc_model 
from routes.ml import _college_model
import numpy as np
import joblib
import os
# Load trained model if exists
_college_model = None
model_path = os.path.join(os.path.dirname(__file__), '..', 'college_ctc_model.pkl')
if os.path.exists(model_path):
    try:
        _college_model = joblib.load(model_path)
        print("✅ Loaded real-data college CTC model")
    except Exception as e:
        print(f"⚠️ Could not load model: {e}")
predictor_bp = Blueprint("predictor", __name__)


def _err(msg, code=400):
    return jsonify({"error": msg}), code


# ═══════════════════════════════════════════════════════════════
#  CTC PREDICTOR ENGINE
# ═══════════════════════════════════════════════════════════════

# Tier base CTC bands (in LPA): [pessimistic, realistic, optimistic]
TIER_BASE = {
    1: [18.0, 28.0, 60.0],
    2: [8.0,  13.0, 22.0],
    3: [4.5,   7.0, 12.0],
}

# Skills with market demand premium multipliers
SKILL_PREMIUM = {
    "ml":          0.28, "ai":          0.28, "deep learning": 0.30,
    "llm":         0.32, "genai":       0.32, "data science":  0.22,
    "python":      0.12, "java":        0.10, "golang":        0.18,
    "rust":        0.20, "c++":         0.14, "javascript":    0.10,
    "react":       0.10, "node":        0.10, "devops":        0.16,
    "kubernetes":  0.18, "aws":         0.16, "gcp":           0.14,
    "azure":       0.14, "blockchain":  0.15, "cybersecurity": 0.20,
    "dsa":         0.10, "system design": 0.14,
}

def _predict_ctc(tier: int, cgpa: float, skills: list[str], internships: int, stream: str) -> dict:
    # 1. Get base CTC from trained model
    if _college_model is not None:
        # Approximate rank based on tier
        if tier == 1:
            approx_rank = 50
        elif tier == 2:
            approx_rank = 150
        else:
            approx_rank = 300
        features = np.array([[tier, approx_rank]])
        base_ctc = float(_college_model.predict(features)[0])
    else:
        # Fallback to tier bands if model not available
        base_map = {1: 20.0, 2: 9.0, 3: 5.0}
        base_ctc = base_map.get(tier, 10.0)
    
    # 2. Student adjustments
    cgpa_clamped = max(5.0, min(cgpa, 10.0))
    cgpa_mult = 0.7 + (cgpa_clamped - 5.0) / 5.0 * 0.5   # 0.7 to 1.2
    skills_count = len(skills)
    skill_mult = 1.0 + min(skills_count, 10) * 0.03        # up to 1.3
    intern_mult = 1.0 + min(internships, 3) * 0.08         # up to 1.24
    stream_mod = {"Engineering": 1.0, "MBA": 1.12, "MCA": 0.92}.get(stream, 1.0)
    
    mid = base_ctc * cgpa_mult * skill_mult * intern_mult * stream_mod
    mid = round(mid, 1)
    low = round(mid * 0.7, 1)
    high = round(mid * 1.5, 1)
    
    # 3. Placement probability (same logic)
    score = (
        (cgpa_clamped - 5.0) / 5.0 * 35 +
        min(skills_count, 6) * 5 +
        min(internships, 3) * 8 +
        (4 - tier) * 5
    )
    probability = round(min(97, max(35, score)), 1)
    
    if probability >= 85:
        bucket = "Top 10%"
    elif probability >= 70:
        bucket = "Top 25%"
    elif probability >= 55:
        bucket = "Top 50%"
    else:
        bucket = "Bottom 50%"
    
    tips = []
    if cgpa < 7.0:
        tips.append("Improving CGPA above 7.0 significantly opens Tier-1 recruiter shortlists.")
    if internships == 0:
        tips.append("Even 1 relevant internship can boost your CTC range by ~8%.")
    if skills_count < 3:
        tips.append("Add 2–3 in-demand skills (Python, DSA, Cloud) to raise your offer ceiling.")
    skills_lower = [s.lower() for s in skills]
    if not any(word in " ".join(skills_lower) for word in ["ml", "ai", "data"]):
        tips.append("AI/ML skills command the highest premiums in the current market (+28–32%).")
    
    return {
        "ctc_range": {"low": low, "mid": mid, "high": high, "unit": "LPA"},
        "placement_probability": probability,
        "percentile_bucket": bucket,
        "cgpa_multiplier": round(cgpa_mult, 3),
        "skill_multiplier": round(skill_mult, 3),
        "intern_multiplier": round(intern_mult, 3),
        "tips": tips,
    }
# ═══════════════════════════════════════════════════════════════
#  SCORE ORACLE ENGINE
# ═══════════════════════════════════════════════════════════════

GATE_SUBJECT_WEIGHTS = {
    "algorithms":  10, "data structures": 10, "os":            8,
    "dbms":         6, "networks":         6, "theory":        8,
    "compilers":    5, "digital logic":    5, "computer org":  5,
    "maths":       15, "aptitude":         6,
}

CAT_SECTION_WEIGHTS = {
    "quant":   34, "dilr": 32, "varc": 34,
}

def _predict_gate(mock_avg: float, prep_months: int, subjects: dict) -> dict:
    # Base from mock avg (scaled from 0-100 to 0-100 GATE)
    base = max(0.0, min(mock_avg * 0.85, 85.0))

    # Prep duration bonus
    prep_bonus = min(prep_months * 1.2, 12.0)

    # Subject mastery bonus
    mastery_bonus = 0.0
    for subject, mastery in subjects.items():
        subj_lower = subject.lower()
        for key, weight in GATE_SUBJECT_WEIGHTS.items():
            if key in subj_lower:
                mastery_bonus += (mastery / 100) * weight * 0.04
                break
    mastery_bonus = min(mastery_bonus, 8.0)

    raw_score  = round(min(base + prep_bonus + mastery_bonus, 100.0), 1)
    percentile = round(min(99.9, max(1.0, raw_score * 0.99 + (raw_score ** 1.12) * 0.008)), 1)

    # College tier eligibility
    if raw_score >= 72:
        eligibility = ["IISc", "IIT Bombay", "IIT Delhi", "IIT Madras"]
    elif raw_score >= 58:
        eligibility = ["IIT (other branches)", "NIT Trichy", "NIT Warangal"]
    elif raw_score >= 42:
        eligibility = ["NIT (state)", "IIIT Hyderabad", "BITS (M.E.)"]
    else:
        eligibility = ["State universities", "Private colleges with GATE quota"]

    return {
        "predicted_score": raw_score,
        "percentile":      percentile,
        "eligibility":     eligibility,
        "score_breakdown": {
            "from_mock_avg":   round(base, 1),
            "prep_bonus":      round(prep_bonus, 1),
            "mastery_bonus":   round(mastery_bonus, 1),
        },
    }


def _predict_cat(mock_avg: float, prep_months: int, sections: dict) -> dict:
    base = max(0.0, min(mock_avg * 1.05, 98.0))
    prep_bonus = min(prep_months * 0.8, 10.0)

    section_bonus = 0.0
    for section, mastery in sections.items():
        sec_lower = section.lower()
        for key, weight in CAT_SECTION_WEIGHTS.items():
            if key in sec_lower:
                section_bonus += (mastery / 100) * weight * 0.05
                break
    section_bonus = min(section_bonus, 8.0)

    percentile = round(min(99.9, max(1.0, base + prep_bonus + section_bonus)), 1)

    if percentile >= 99:
        colleges = ["IIM Ahmedabad", "IIM Bangalore", "IIM Calcutta"]
    elif percentile >= 97:
        colleges = ["IIM Lucknow", "IIM Kozhikode", "IIM Indore"]
    elif percentile >= 90:
        colleges = ["MDI Gurgaon", "SPJIMR", "IMT Ghaziabad"]
    elif percentile >= 80:
        colleges = ["FORE School", "Great Lakes", "BIMTECH"]
    else:
        colleges = ["Regional B-schools", "Improve mock scores first"]

    return {
        "predicted_percentile": percentile,
        "college_eligibility":  colleges,
        "score_breakdown": {
            "base_percentile":   round(base, 1),
            "prep_bonus":        round(prep_bonus, 1),
            "section_bonus":     round(section_bonus, 1),
        },
    }


# ═══════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════

# ── POST /api/predictor/ctc ───────────────────────────────────
@predictor_bp.route("/ctc", methods=["POST"])
def predict_ctc():
    data = request.get_json(silent=True) or {}

    tier        = data.get("tier")
    cgpa        = data.get("cgpa")
    skills      = data.get("skills", [])
    internships = data.get("internships", 0)
    stream      = data.get("stream", "Engineering")

    # Validation
    if tier not in (1, 2, 3):
        return _err("tier must be 1, 2, or 3.")
    try:
        cgpa = float(cgpa)
        if not (0 < cgpa <= 10):
            raise ValueError()
    except (TypeError, ValueError):
        return _err("cgpa must be a number between 0 and 10.")
    if not isinstance(skills, list):
        return _err("skills must be a list of strings.")
    try:
        internships = int(internships)
    except (TypeError, ValueError):
        return _err("internships must be an integer.")

    result = _predict_ctc(tier, cgpa, skills, internships, stream)
    return jsonify(result)


# ── POST /api/predictor/gate ──────────────────────────────────
@predictor_bp.route("/gate", methods=["POST"])
def predict_gate():
    data = request.get_json(silent=True) or {}

    mock_avg    = data.get("mock_avg")
    prep_months = data.get("prep_months", 6)
    subjects    = data.get("subjects", {})

    try:
        mock_avg = float(mock_avg)
        if not (0 <= mock_avg <= 100):
            raise ValueError()
    except (TypeError, ValueError):
        return _err("mock_avg must be a number between 0 and 100.")

    try:
        prep_months = int(prep_months)
    except (TypeError, ValueError):
        return _err("prep_months must be an integer.")

    result = _predict_gate(mock_avg, prep_months, subjects)
    return jsonify(result)


# ── POST /api/predictor/cat ───────────────────────────────────
@predictor_bp.route("/cat", methods=["POST"])
def predict_cat():
    data = request.get_json(silent=True) or {}

    mock_avg    = data.get("mock_avg")
    prep_months = data.get("prep_months", 6)
    sections    = data.get("sections", {})

    try:
        mock_avg = float(mock_avg)
        if not (0 <= mock_avg <= 100):
            raise ValueError()
    except (TypeError, ValueError):
        return _err("mock_avg must be a number between 0 and 100.")

    try:
        prep_months = int(prep_months)
    except (TypeError, ValueError):
        return _err("prep_months must be an integer.")

    result = _predict_cat(mock_avg, prep_months, sections)
    return jsonify(result)
@predictor_bp.route("/recommend-colleges", methods=["POST"])
def recommend_colleges():
    data = request.get_json(silent=True) or {}
    target_ctc = data.get("target_ctc")
    stream = data.get("stream", "Engineering")
    limit = data.get("limit", 5)

    if target_ctc is None:
        return _err("target_ctc required", 400)

    from models import College
    colleges = College.query.filter(
        College.stream == stream,
        College.avg_ctc.isnot(None),
        College.avg_ctc.between(target_ctc - 5, target_ctc + 5)
    ).order_by(College.avg_ctc.desc()).limit(limit).all()

    return jsonify([c.to_dict() for c in colleges])