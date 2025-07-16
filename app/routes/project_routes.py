from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.project import Project
from app.models.upwork_job import UpworkJob
from app.models.proposal import Proposal
from app.models.user import User
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
