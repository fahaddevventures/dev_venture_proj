from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import check_password_hash
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("auth/login.html")

        
        user = User.query.filter_by(email=email).first()

        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f"Welcome back, {user.first_name}!", "success")
            return redirect(url_for("dashboard.index"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")



@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login'))


@auth_bp.route('/current-user', methods=['GET'])
@login_required
def get_current_user():
    user_data = {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "profile_image_url": current_user.profile_image_url,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

    return jsonify({
        "success": True,
        "user": user_data
    }), 200