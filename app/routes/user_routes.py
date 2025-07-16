from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.user import User
from app.enums import UserRoleEnum
from werkzeug.security import generate_password_hash
from flask_login import login_required
from app.utils.role_required import role_required

user_bp = Blueprint("user", __name__, url_prefix="/users")

@user_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required(UserRoleEnum.admin)
def add_user():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        contact = request.form.get("contact")
        role = request.form.get("role")

        # Basic validation
        if not all([first_name, last_name, email, password, contact, role]):
            flash("All fields are required.", "danger")
            return render_template("users/add_user.html")

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return render_template("users/add_user.html")

        try:
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=generate_password_hash(password),
                contact=contact,
                role=UserRoleEnum[role],
            )
            db.session.add(user)
            db.session.commit()
            flash("User added successfully!", "success")
            return redirect(url_for("user.add_user"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while adding the user.", "danger")

    return render_template("users/add_user.html",UserRoleEnum=UserRoleEnum)


@user_bp.route("/", methods=["GET"])
@login_required
@role_required(UserRoleEnum.admin)
def get_all_users():
    users = User.query.all()
    return render_template("users/user_list.html", users=users)


@user_bp.route("/delete/<int:user_id>", methods=["POST"])
@login_required
@role_required(UserRoleEnum.admin)
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting user.", "danger")
    return redirect(url_for("user.get_all_users"))


@user_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@role_required(UserRoleEnum.admin)
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        contact = request.form.get("contact")
        role = request.form.get("role")

        if not all([first_name, last_name, email, contact, role]):
            flash("All fields except password are required.", "danger")
            return render_template("users/edit_user.html", user=user)

        try:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.contact = contact
            user.role = UserRoleEnum[role]

            db.session.commit()
            flash("User updated successfully!", "success")
            return redirect(url_for("user.get_all_users"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the user.", "danger")

    return render_template("users/edit_user.html", user=user)

@user_bp.route("/analytics", methods=["GET"])
@login_required
@role_required(UserRoleEnum.admin)
def user_analytics():
    total_users = User.query.count()
    total_admins = User.query.filter_by(role=UserRoleEnum.admin).count()
    total_team_leads = User.query.filter_by(role=UserRoleEnum.team_lead).count()
    total_employees = User.query.filter_by(role=UserRoleEnum.employee).count()
    total_salesmen = User.query.filter_by(role=UserRoleEnum.salesman).count()

    return render_template(
        "users/analytics.html",
        total_users=total_users,
        total_admins=total_admins,
        total_team_leads=total_team_leads,
        total_employees=total_employees,
        total_salesmen=total_salesmen,
    )

