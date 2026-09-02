from flask import Blueprint, request, jsonify
import numpy as np
import re
import io

ml_bp = Blueprint("ml", __name__)


# ═══════════════════════════════════════════════════════════════
#  1. SMART CTC PREDICTOR (RandomForest)
# ═══════════════════════════════════════════════════════════════
def build_ctc_model():
    try:
        from sklearn.ensemble import RandomForestRegressor
        # Synthetic training data: [cgpa, tier, internships, skills_count]
        X = np.array([
            [9.5,1,3,8],[9.0,1,2,6],[8.5,1,2,5],[8.0,1,1,4],[7.5,1,1,3],
            [9.0,2,3,7],[8.5,2,2,5],[8.0,2,2,4],[7.5,2,1,3],[7.0,2,1,2],
            [8.0,3,2,5],[7.5,3,1,4],[7.0,3,1,3],[6.5,3,0,2],[6.0,3,0,1],
            [9.8,1,3,10],[9.2,1,3,8],[8.8,1,2,6],[8.3,2,2,5],[7.8,2,1,4],
            [7.3,2,1,3],[8.5,3,2,4],[7.0,3,1,3],[6.5,3,0,2],[5.5,3,0,1],
        ])
        y = np.array([
            45,35,28,22,18,
            20,15,12,10,8,
            10,8,6,5,4,
            60,48,36,18,14,
            11,9,7,5,3.5,
        ])
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        return model
    except Exception:
        return None

_ctc_model = build_ctc_model()

SKILL_PREMIUM_ML = {
    "ml": 0.3, "ai": 0.3, "deep learning": 0.32, "llm": 0.35,
    "genai": 0.35, "data science": 0.25, "python": 0.12,
    "golang": 0.2, "rust": 0.22, "aws": 0.18, "kubernetes": 0.2,
    "cybersecurity": 0.22, "blockchain": 0.16,
}

@ml_bp.route("/ctc", methods=["POST"])
def smart_ctc():
    data = request.get_json(silent=True) or {}
    cgpa        = float(data.get("cgpa", 7.0))
    tier        = int(data.get("tier", 2))
    internships = int(data.get("internships", 0))
    skills      = data.get("skills", [])
    stream      = data.get("stream", "Engineering")

    skills_lower = [s.lower() for s in skills]
    skill_mult = 1.0
    for skill in skills_lower:
        for key, premium in SKILL_PREMIUM_ML.items():
            if key in skill:
                skill_mult += premium
                break
    skill_mult = min(skill_mult, 1.9)

    if _ctc_model:
        features = np.array([[cgpa, tier, min(internships,3), min(len(skills),10)]])
        base_ctc = float(_ctc_model.predict(features)[0])
    else:
        base_map = {1: 28, 2: 13, 3: 7}
        base_ctc = base_map.get(tier, 10)

    mid  = round(base_ctc * skill_mult, 1)
    low  = round(mid * 0.7, 1)
    high = round(mid * 1.5, 1)

    prob_score = (
        (cgpa - 5) / 5 * 35 +
        min(len(skills), 6) * 5 +
        min(internships, 3) * 8 +
        (4 - tier) * 5
    )
    probability = round(min(97, max(35, prob_score)), 1)

    if probability >= 85: bucket = "Top 10%"
    elif probability >= 70: bucket = "Top 25%"
    elif probability >= 55: bucket = "Top 50%"
    else: bucket = "Bottom 50%"

    tips = []
    if cgpa < 7.0:
        tips.append("Improving CGPA above 7.0 significantly opens Tier-1 shortlists.")
    if internships == 0:
        tips.append("Even 1 internship can boost your CTC range by ~8%.")
    if len(skills) < 3:
        tips.append("Add 2–3 in-demand skills (Python, DSA, Cloud) to raise your ceiling.")
    if "ml" not in " ".join(skills_lower) and "data" not in " ".join(skills_lower):
        tips.append("AI/ML skills command +28–35% premium in current market.")

    stream_mod = {"Engineering": 1.0, "MBA": 1.12, "MCA": 0.92, "M.Tech": 1.05}.get(stream, 1.0)
    low  = round(low * stream_mod, 1)
    mid  = round(mid * stream_mod, 1)
    high = round(high * stream_mod, 1)

    return jsonify({
        "ctc_range": {"low": low, "mid": mid, "high": high, "unit": "LPA"},
        "placement_probability": probability,
        "percentile_bucket": bucket,
        "model": "RandomForest" if _ctc_model else "Rule-based",
        "tips": tips,
    })


# ═══════════════════════════════════════════════════════════════
#  2. COLLEGE RECOMMENDATION ENGINE
# ═══════════════════════════════════════════════════════════════
@ml_bp.route("/recommend", methods=["POST"])
def recommend_colleges():
    from extensions import db
    from models import College
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics.pairwise import cosine_similarity

    data   = request.get_json(silent=True) or {}
    cgpa   = float(data.get("cgpa", 7.0))
    budget = float(data.get("budget_lpa", 10.0))   # max fees per year
    stream = data.get("stream", "Engineering")
    pref_ctc = float(data.get("preferred_ctc", 10.0))

    colleges = College.query.filter_by(stream=stream).all()
    if not colleges:
        return jsonify({"recommendations": [], "message": "No colleges found for this stream."})

    rows = []
    for c in colleges:
        rows.append({
            "id":            c.id,
            "name":          c.name,
            "city":          c.city,
            "state":         c.state,
            "fees":          c.fees_per_year or 5,
            "avg_ctc":       c.avg_ctc or 5,
            "placement_pct": c.placement_pct or 70,
            "nirf_rank":     c.nirf_rank or 500,
            "tier":          c.tier or 3,
        })

    if not rows:
        return jsonify({"recommendations": []})

    # Feature matrix: [fees, avg_ctc, placement_pct, nirf_rank_inv]
    feat = np.array([
        [r["fees"], r["avg_ctc"], r["placement_pct"], 1000 - (r["nirf_rank"] or 500)]
        for r in rows
    ], dtype=float)

    scaler = MinMaxScaler()
    feat_scaled = scaler.fit_transform(feat)

    # User preference vector
    user_vec = np.array([[budget, pref_ctc, 85, 800]], dtype=float)
    user_scaled = scaler.transform(user_vec)

    sims = cosine_similarity(user_scaled, feat_scaled)[0]

    # Penalize colleges exceeding budget
    for i, r in enumerate(rows):
        if r["fees"] > budget:
            sims[i] *= 0.3

    top_idx = np.argsort(sims)[::-1][:5]

    recommendations = []
    for i in top_idx:
        r = rows[i]
        recommendations.append({
            **r,
            "match_score": round(float(sims[i]) * 100, 1),
        })

    return jsonify({"recommendations": recommendations})


# ═══════════════════════════════════════════════════════════════
#  3. RESUME ANALYZER
# ═══════════════════════════════════════════════════════════════
KNOWN_SKILLS = [
    "python","java","c++","javascript","typescript","react","node","angular","vue",
    "django","flask","fastapi","sql","mysql","postgresql","mongodb","redis",
    "aws","azure","gcp","docker","kubernetes","git","linux","machine learning",
    "deep learning","tensorflow","pytorch","nlp","data science","pandas","numpy",
    "scikit-learn","tableau","power bi","excel","hadoop","spark","kafka",
    "rest api","graphql","microservices","agile","scrum","devops","ci/cd",
    "html","css","bootstrap","tailwind","figma","photoshop",
]

@ml_bp.route("/resume", methods=["POST"])
def analyze_resume():
    try:
        import PyPDF2
    except ImportError:
        return jsonify({"error": "PyPDF2 not installed."}), 503

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Send a PDF as 'file'."}), 400

    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    try:
        reader = PyPDF2.PdfReader(io.BytesIO(f.read()))
        text = " ".join(page.extract_text() or "" for page in reader.pages).lower()
    except Exception as e:
        return jsonify({"error": f"Could not read PDF: {str(e)}"}), 400

    # Extract skills
    found_skills = [s for s in KNOWN_SKILLS if s in text]

    # Extract education level
    education = "Unknown"
    if "ph.d" in text or "doctorate" in text:    education = "PhD"
    elif "m.tech" in text or "mtech" in text:    education = "M.Tech"
    elif "mba" in text:                           education = "MBA"
    elif "mca" in text:                           education = "MCA"
    elif "b.tech" in text or "btech" in text:    education = "B.Tech"
    elif "b.e" in text or "bachelor" in text:    education = "Bachelor's"

    # Extract CGPA
    cgpa_match = re.search(r'cgpa[:\s]*([0-9]\.[0-9]{1,2})', text)
    cgpa = float(cgpa_match.group(1)) if cgpa_match else None

    # Count experience years
    exp_match = re.search(r'(\d+)\+?\s*year', text)
    experience_years = int(exp_match.group(1)) if exp_match else 0

    # Strength score
    score = min(100, len(found_skills) * 5 + experience_years * 8 + (20 if cgpa and cgpa >= 7.5 else 0))

    # Categorize skills
    ml_skills   = [s for s in found_skills if s in ["machine learning","deep learning","tensorflow","pytorch","nlp","data science","pandas","numpy","scikit-learn"]]
    web_skills  = [s for s in found_skills if s in ["react","node","angular","vue","html","css","javascript","typescript","django","flask","fastapi"]]
    cloud_skills= [s for s in found_skills if s in ["aws","azure","gcp","docker","kubernetes","devops","ci/cd"]]

    # Suggestions
    suggestions = []
    if len(found_skills) < 5:
        suggestions.append("Add more technical skills — recruiters scan for 5+ relevant tools.")
    if not ml_skills:
        suggestions.append("Consider adding AI/ML skills — highest demand in 2025 market.")
    if not cloud_skills:
        suggestions.append("Cloud skills (AWS/Docker) are now expected for most tech roles.")
    if experience_years == 0:
        suggestions.append("Add internship experience — even 1 internship significantly boosts shortlisting.")

    return jsonify({
        "education":        education,
        "cgpa":             cgpa,
        "experience_years": experience_years,
        "skills_found":     found_skills,
        "skill_categories": {
            "ml_ai":  ml_skills,
            "web":    web_skills,
            "cloud":  cloud_skills,
        },
        "resume_score":  score,
        "suggestions":   suggestions,
        "total_skills":  len(found_skills),
    })


# ═══════════════════════════════════════════════════════════════
#  4. PLACEMENT TREND PREDICTOR
# ═══════════════════════════════════════════════════════════════
@ml_bp.route("/trends", methods=["POST"])
def placement_trends():
    data   = request.get_json(silent=True) or {}
    stream = data.get("stream", "Engineering")
    years  = int(data.get("years_ahead", 3))

    # Historical CTC data (2019-2024) by stream
    history = {
        "Engineering": [8.5, 9.2, 9.8, 11.5, 13.2, 15.0],
        "MBA":         [14.0,15.5,16.2,18.0,22.0,26.0],
        "MCA":         [5.5, 6.0, 6.5, 7.2,  8.5, 10.0],
        "M.Tech":      [10.0,11.0,12.0,13.5,15.0,17.0],
    }
    base_years = [2019, 2020, 2021, 2022, 2023, 2024]

    ctc_data = history.get(stream, history["Engineering"])

    # Linear regression
    x = np.array(base_years, dtype=float)
    y = np.array(ctc_data, dtype=float)
    coeffs = np.polyfit(x, y, 1)   # slope, intercept
    slope, intercept = coeffs

    future_years = list(range(2025, 2025 + years))
    future_ctc   = [round(slope * yr + intercept, 1) for yr in future_years]

    # Growth rate
    growth_rate = round((slope / ctc_data[-1]) * 100, 1)

    return jsonify({
        "stream":        stream,
        "historical": {
            "years": base_years,
            "avg_ctc": ctc_data,
        },
        "forecast": {
            "years":   future_years,
            "avg_ctc": future_ctc,
        },
        "annual_growth_rate": growth_rate,
        "insight": f"{stream} placements growing at {growth_rate}% per year. "
                    f"Expected avg CTC by {future_years[-1]}: ₹{future_ctc[-1]}L",
    })


# ═══════════════════════════════════════════════════════════════
#  5. COLLEGE CTC MODEL (trained on real database)
# ═══════════════════════════════════════════════════════════════
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from extensions import db
from models import College

_college_model = None

def train_college_ctc_model(app=None):
    """Train a model to predict college average CTC based on tier, stream, city, state."""
    global _college_model
    try:
        # Use the provided app, or create one (should not happen)
        if app is None:
            from app import create_app
            app = create_app()
        with app.app_context():
            colleges = College.query.filter(College.avg_ctc.isnot(None)).all()
            if not colleges:
                print("⚠️ No college CTC data found – cannot train model.")
                return

            X = []
            y = []
            for c in colleges:
                if c.avg_ctc <= 0:
                    continue
                X.append({
                    'tier': c.tier or 2,
                    'stream': c.stream or 'Engineering',
                    'city': c.city or 'Unknown',
                    'state': c.state or 'Unknown'
                })
                y.append(c.avg_ctc)

            if not X:
                print("⚠️ No usable data after filtering.")
                return

            # Preprocessing
            categorical_cols = ['stream', 'city', 'state']
            numeric_cols = ['tier']

            preprocessor = ColumnTransformer([
                ('num', 'passthrough', numeric_cols),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
            ])

            # Pipeline
            model = Pipeline([
                ('preprocessor', preprocessor),
                ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
            ])

            model.fit(X, y)
            _college_model = model
            print(f"✅ College CTC model trained on {len(y)} colleges.")
    except Exception as e:
        print(f"❌ Error training college CTC model: {e}")
