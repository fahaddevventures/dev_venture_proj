from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager,current_user
from app.config import Config
from app.extensions import db, migrate

from app.models.user import User
from app.models.upwork_job import UpworkJob
from app.models.proposal import Proposal
from app.models.project import Project
from app.models.project_member import ProjectMember

from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.jobs_routes import job_bp
from app.routes.proposal_routes import proposal_bp
from app.routes.project_routes import project_bp
from app.routes.task_routes import task_bp

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates')  
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(proposal_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(task_bp)

    @app.route("/", methods=["GET"])
    def home():
        return redirect(url_for('auth.login'))

    

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html", role=getattr(current_user, "role", "Unknown")), 403

    return app
