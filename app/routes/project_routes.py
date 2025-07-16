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


@project_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required(UserRoleEnum.admin, UserRoleEnum.team_lead)
def create_project():
    jobs = UpworkJob.query.with_entities(UpworkJob.id, UpworkJob.title).all()
    team_leads = User.query.filter_by(role=UserRoleEnum.team_lead).all()
    proposals = Proposal.query.with_entities(Proposal.id).all()

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        job_id = request.form.get("job_id")
        team_lead_id = request.form.get("team_lead_id")
        proposal_id = request.form.get("proposal_id")
        status = request.form.get("status")
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None

        if not name or not job_id or not team_lead_id:
            flash("Project name, job, and team lead are required.", "danger")
            return render_template("projects/create_project.html", jobs=jobs, team_leads=team_leads, proposals=proposals, statuses=ProjectStatusEnum)

        project = Project(
            name=name,
            description=description,
            job_id=job_id,
            team_lead_id=team_lead_id,
            proposal_id=proposal_id or None,
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
