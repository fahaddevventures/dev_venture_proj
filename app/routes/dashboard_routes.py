from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from app.utils.role_required import role_required
from app.enums import UserRoleEnum
from app.extensions import db
from app.models import User, Proposal, Project
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
@login_required
def index():
    # return render_template("base_dashboard.html")
    return redirect(url_for("dashboard.analytics_dashboard"))


@dashboard_bp.route("/analytics")
@login_required
def analytics_dashboard():
    total_users = User.query.count()
    total_projects = Project.query.count()
    total_proposals = Proposal.query.count()

    role_counts = (
        db.session.query(User.role, func.count(User.id))
        .group_by(User.role)
        .all()
    )

    role_data = {
        "admin": 0,
        "team_lead": 0,
        "salesman": 0,
        "employee": 0
    }

    for role, count in role_counts:
        role_name = role.name if hasattr(role, 'name') else role  # enum or str
        role_data[role_name] = count

    return render_template("dashboard/analytics.html",
                           total_users=total_users,
                           total_projects=total_projects,
                           total_proposals=total_proposals,
                           role_data=role_data)
