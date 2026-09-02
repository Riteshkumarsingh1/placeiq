# models.py
from extensions import db  # Import db from extensions
from datetime import datetime, timezone
import bcrypt


# ─────────────────────────────────────────────
#  USER
# ─────────────────────────────────────────────
class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    role          = db.Column(db.String(40), default="student")   # student | admin
    stream        = db.Column(db.String(60))                      # Engineering / MBA / MCA
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password_hash.encode("utf-8")
        )

    def to_dict(self):
        return {
            "id":         self.id,
            "name":       self.name,
            "email":      self.email,
            "role":       self.role,
            "stream":     self.stream,
            "created_at": self.created_at.isoformat(),
            
        }


# ─────────────────────────────────────────────
#  COLLEGE
# ─────────────────────────────────────────────
class College(db.Model):
    __tablename__ = "colleges"

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(200), nullable=False)
    city            = db.Column(db.String(80))
    state           = db.Column(db.String(80))
    stream          = db.Column(db.String(60))          # Engineering / MBA / MCA
    tier            = db.Column(db.Integer)             # 1 / 2 / 3
    nirf_rank       = db.Column(db.Integer)
    fees_per_year   = db.Column(db.Float)               # in lakhs
    about = db.Column(db.Text)      # College description
    trends = db.Column(db.JSON)     # Year-wise CTC data
    # Placement stats
    avg_ctc         = db.Column(db.Float)               # in lakhs
    highest_ctc     = db.Column(db.Float)
    placement_pct   = db.Column(db.Float)               # 0-100
    top_recruiters  = db.Column(db.JSON)                # ["Google","Microsoft", …]

    # Meta
    established     = db.Column(db.Integer)
    accreditation   = db.Column(db.String(40))          # NAAC A++ / A+ / A
    website         = db.Column(db.String(255))
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id":             self.id,
            "name":           self.name,
            "city":           self.city,
            "state":          self.state,
            "stream":         self.stream,
            "tier":           self.tier,
            "nirf_rank":      self.nirf_rank,
            "fees_per_year":  self.fees_per_year,
            "avg_ctc":        self.avg_ctc,
            "highest_ctc":    self.highest_ctc,
            "placement_pct":  self.placement_pct,
            "top_recruiters": self.top_recruiters or [],
            "established":    self.established,
            "accreditation":  self.accreditation,
            "website":        self.website,
        }