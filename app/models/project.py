from app.extensions import db
from datetime import datetime, timezone
from app.enums import ProjectStatusEnum

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    job_id = db.Column(db.Integer, db.ForeignKey('upwork_jobs.id'), nullable=False)
    team_lead_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposals.id'), nullable=True)

    status = db.Column(db.Enum(ProjectStatusEnum), default=ProjectStatusEnum.active, nullable=False)

    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    job = db.relationship('UpworkJob', backref=db.backref('projects', cascade='all, delete-orphan'))
    team_lead = db.relationship('User', backref=db.backref('led_projects', cascade='all, delete-orphan'))
    proposal = db.relationship('Proposal', backref=db.backref('project', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Project {self.id} - {self.name}>"