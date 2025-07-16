from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.project import Project
from app.models.upwork_job import UpworkJob
from app.models.proposal import Proposal
from app.models.user import User
from app.models.project_member import ProjectMember
from app.schemas.project_schema import ProjectSchema
from app.enums import ProjectStatusEnum, UserRoleEnum
from flask_login import login_required
from app.utils.role_required import role_required

project_bp = Blueprint("project", __name__, url_prefix="/projects")

project_schema = ProjectSchema(session=db.session)
project_list_schema = ProjectSchema(many=True)


from datetime import datetime

@project_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required(UserRoleEnum.admin, UserRoleEnum.team_lead)
def create_project():
    jobs = UpworkJob.query.with_entities(UpworkJob.id, UpworkJob.title).all()
    team_leads = User.query.filter_by(role=UserRoleEnum.team_lead).all()

    proposals = (
        Proposal.query
        .join(UpworkJob, Proposal.job_id == UpworkJob.id)
        .with_entities(Proposal.id, UpworkJob.title.label("job_title"))
        .all()
    )

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        job_id = request.form.get("job_id")
        team_lead_id = request.form.get("team_lead_id")
        proposal_id = request.form.get("proposal_id")
        status = request.form.get("status")
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")

        if not name or not job_id or not team_lead_id or not proposal_id:
            flash("All fields including linked proposal are required.", "danger")
            return render_template("projects/create_project.html", jobs=jobs, team_leads=team_leads, proposals=proposals, statuses=ProjectStatusEnum)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

        if start_date and end_date and end_date < start_date:
            flash("End date cannot be earlier than start date.", "danger")
            return render_template("projects/create_project.html", jobs=jobs, team_leads=team_leads, proposals=proposals, statuses=ProjectStatusEnum)

        project = Project(
            name=name,
            description=description,
            job_id=job_id,
            team_lead_id=team_lead_id,
            proposal_id=proposal_id,
            status=ProjectStatusEnum[status],
            start_date=start_date,
            end_date=end_date
        )

        try:
            db.session.add(project)
            db.session.commit()
            flash("Project created successfully!", "success")
            return redirect(url_for("project.create_project"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating project: {str(e)}", "danger")

    return render_template("projects/create_project.html", jobs=jobs, team_leads=team_leads, proposals=proposals, statuses=ProjectStatusEnum)


@project_bp.route('/all', methods=['GET'])
@login_required
@role_required(UserRoleEnum.admin, UserRoleEnum.team_lead)
def list_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects/project_list.html', projects=projects)


@project_bp.route('/update/<int:project_id>', methods=['GET', 'POST'])
@login_required
@role_required(UserRoleEnum.admin, UserRoleEnum.team_lead)
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    jobs = UpworkJob.query.with_entities(UpworkJob.id, UpworkJob.title).all()
    team_leads = User.query.filter_by(role=UserRoleEnum.team_lead).all()
    proposals = (
        Proposal.query
        .join(UpworkJob, Proposal.job_id == UpworkJob.id)
        .with_entities(Proposal.id, UpworkJob.title.label("job_title"))
        .all()
    )

    if request.method == 'POST':
        project.name = request.form.get("name")
        project.description = request.form.get("description")
        project.job_id = request.form.get("job_id")
        project.team_lead_id = request.form.get("team_lead_id")
        project.proposal_id = request.form.get("proposal_id")
        project.status = ProjectStatusEnum[request.form.get("status")]
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")

        if not project.name or not project.job_id or not project.team_lead_id or not project.proposal_id:
            flash("All fields are required.", "danger")
            return render_template("projects/update_project.html", project=project, jobs=jobs, team_leads=team_leads, proposals=proposals, statuses=ProjectStatusEnum)

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            if end_date < start_date:
                flash("End date cannot be earlier than start date.", "danger")
                return render_template("projects/update_project.html", project=project, jobs=jobs, team_leads=team_leads, proposals=proposals, statuses=ProjectStatusEnum)
            project.start_date = start_date
            project.end_date = end_date

        try:
            db.session.commit()
            flash("Project updated successfully!", "success")
            return redirect(url_for("project.list_projects"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating project: {str(e)}", "danger")

    return render_template("projects/update_project.html", project=project, jobs=jobs, team_leads=team_leads, proposals=proposals, statuses=ProjectStatusEnum)


@project_bp.route("/assign-members/<int:project_id>", methods=["GET", "POST"])
@login_required
@role_required(UserRoleEnum.admin, UserRoleEnum.team_lead)
def assign_project_members(project_id):
    project = Project.query.get_or_404(project_id)
    users = User.query.filter(User.role.in_([
        UserRoleEnum.team_lead, UserRoleEnum.employee, UserRoleEnum.salesman
    ])).all()

    if request.method == "POST":
        selected_user_ids = request.form.getlist("user_ids")

        # Clear existing members
        ProjectMember.query.filter_by(project_id=project.id).delete()

        for user_id in selected_user_ids:
            role = request.form.get(f"role_in_project_{user_id}")
            member = ProjectMember(
                user_id=int(user_id),
                project_id=project.id,
                role_in_project=role
            )
            db.session.add(member)

        try:
            db.session.commit()
            flash("Team members assigned successfully!", "success")
            return redirect(url_for("project.list_projects"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error assigning team members: {str(e)}", "danger")

    return render_template("projects/assign_members.html", project=project, users=users)

@project_bp.route('/delete/<int:project_id>', methods=['POST'])
@login_required
@role_required(UserRoleEnum.admin)
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)

    try:
        db.session.delete(project)
        db.session.commit()
        flash("Project deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting project: {str(e)}", "danger")

    return redirect(url_for('project.list_projects'))
