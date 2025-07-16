from app.extensions import db
from datetime import datetime, timezone
from app.enums import TaskPriorityEnum, TaskStatusEnum


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deliverables = db.Column(db.Text, nullable=False)

    status = db.Column(db.Enum(TaskStatusEnum), default=TaskStatusEnum.todo, nullable=False)
    priority = db.Column(db.Enum(TaskPriorityEnum), default=TaskPriorityEnum.medium, nullable=False)

    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = db.relationship('Project', backref=db.backref('tasks', cascade='all, delete-orphan'))
    creator = db.relationship('User', foreign_keys=[created_by], backref=db.backref('created_tasks', cascade='all, delete-orphan'))
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_tasks')


    # In Task model
    def __repr__(self):
        return f"<Task {self.id} - {self.title}>"
    
