from app.extensions import db
from datetime import datetime, timezone
from app.enums import BudgetTypeEnum, FeasibilityEnum

class UpworkJob(db.Model):
    __tablename__ = 'upwork_jobs'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    skills = db.Column(db.JSON, nullable=True)
    tags = db.Column(db.JSON, nullable=True)

    category = db.Column(db.String(100), nullable=True)

    client_country = db.Column(db.String(100), nullable=True)
    client_payment_verified = db.Column(db.Boolean, default=True)
    client_total_spent = db.Column(db.Numeric(10, 2), nullable=True)
    client_jobs_posted = db.Column(db.Integer, nullable=True)
    client_hire_rate = db.Column(db.String(10), nullable=True)

    client_reviews = db.Column(db.Text, nullable=True)

    budget = db.Column(db.Numeric(10, 2), nullable=True)
    budget_type = db.Column(db.Enum(BudgetTypeEnum), nullable=True)

    project_length = db.Column(db.String(100), nullable=True)
    hours_per_week = db.Column(db.String(50), nullable=True)

    proposals_submitted = db.Column(db.Integer, nullable=True)
    interviewing = db.Column(db.Integer, nullable=True)
    invites_sent = db.Column(db.Integer, nullable=True)

    connect_required = db.Column(db.Integer, nullable=True)
    expected_cost = db.Column(db.Numeric(10, 2), nullable=True)
    expected_earnings = db.Column(db.Numeric(10, 2), nullable=True)

    posted_at = db.Column(db.DateTime, nullable=True)
    job_url = db.Column(db.Text, nullable=False)

    feasibility_status = db.Column(db.Enum(FeasibilityEnum), default=FeasibilityEnum.pending, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<UpworkJob {self.job_id} - {self.title}>"