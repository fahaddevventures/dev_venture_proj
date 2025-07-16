from app.extensions import db
from datetime import datetime, timezone

class ProjectMember(db.Model):
    __tablename__ = 'project_members'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)

    role_in_project = db.Column(db.String(100), nullable=True)  # e.g., "frontend dev", "QA", etc.
    joined_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref=db.backref('project_memberships', cascade='all, delete-orphan'))
    project = db.relationship('Project', backref=db.backref('members', cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<ProjectMember user_id={self.user_id}, project_id={self.project_id}>"
