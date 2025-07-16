from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.task import Task
from app.schemas.task_schema import TaskSchema
from app.utils.gemini import assess_proposal_from_job
from app.enums import TaskPriorityEnum, TaskStatusEnum
from app.enums import UserRoleEnum
from app.utils.role_required import role_required
from app.models.project import Project
from app.models.user import User
from datetime import datetime

task_bp = Blueprint('task', __name__,url_prefix='/tasks')

task_schema = TaskSchema(session=db.session)
task_list_schema = TaskSchema(many=True)

@task_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(UserRoleEnum.admin, UserRoleEnum.team_lead)
def create_task():
    from app.models import Project, User  # import models as needed

    projects = Project.query.all()
    users = User.query.all()

    if request.method == 'POST':
        # task_code = request.form.get("task_code")
        project_id = request.form.get("project_id")
        assigned_to = request.form.get("assigned_to")
        title = request.form.get("title")
        description = request.form.get("description")
        deliverables = request.form.get("deliverables")
        priority = request.form.get("priority")
        status = request.form.get("status")
        due_date = request.form.get("due_date")

        # Validate
        if not all([project_id, assigned_to, title, deliverables]):
            flash("All required fields must be filled.", "danger")
            return redirect(url_for('task.create_task'))

        try:
            task = Task(
                # task_code=task_code,
                project_id=int(project_id),
                assigned_to=int(assigned_to),
                created_by=current_user.id,
                title=title,
                description=description,
                deliverables=deliverables,
                priority=TaskPriorityEnum(priority),
                status=TaskStatusEnum(status),
                due_date=datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
            )
            db.session.add(task)
            db.session.commit()
            flash("Task created successfully!", "success")
            return redirect(url_for('task.create_task'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating task: {str(e)}", "danger")

    return render_template("tasks/create_task.html", projects=projects, users=users)



@task_bp.route("/all", methods=["GET"])
@login_required
# @role_required(UserRoleEnum.admin, UserRoleEnum.team_lead)
def list_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("tasks/task_list.html", tasks=tasks)


@task_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    users = User.query.all()
    projects = Project.query.all()

    if request.method == "POST":
        task.title = request.form.get("title")
        task.description = request.form.get("description")
        task.deliverables = request.form.get("deliverables")
        task.status = request.form.get("status")
        task.priority = request.form.get("priority")
        task.due_date = request.form.get("due_date")
        task.assigned_to = request.form.get("assigned_to")
        task.project_id = request.form.get("project_id")

        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for("task.list_tasks"))

    return render_template("tasks/update_task.html", task=task, users=users, projects=projects)


@task_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully!", "success")
    return redirect(url_for("task.list_tasks"))
