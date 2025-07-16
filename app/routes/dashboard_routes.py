from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.role_required import role_required
from app.enums import UserRoleEnum

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
@login_required
def index():
    return render_template("base_dashboard.html")


