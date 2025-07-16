from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.upwork_job import UpworkJob
from app.schemas.upwork_jobs_schema import UpworkJobSchema
from app.enums import UserRoleEnum
from app.utils.role_required import role_required
from app.utils.gemini import assess_job_feasibility,generate_dummy_upwork_jobs
from datetime import datetime
import json

job_bp = Blueprint('job', __name__, url_prefix='/jobs')

upwork_jobs_schema = UpworkJobSchema(session=db.session)
upwork_jobs_list_schema = UpworkJobSchema(many=True)

@job_bp.route("/get")
@login_required
@role_required(UserRoleEnum.admin,  UserRoleEnum.salesman)
def get_jobs():
    return render_template("jobs/get_jobs.html")

@job_bp.route('/list', methods=['GET'])
@login_required
@role_required(UserRoleEnum.admin, UserRoleEnum.salesman)
def list_jobs():
    jobs = UpworkJob.query.order_by(UpworkJob.created_at.desc()).all()
    return render_template("jobs/job_list.html", jobs=jobs)


@job_bp.route('/generate-dummy-jobs', methods=['POST'])
def generate_dummy_jobs():
    try:
        # Call Gemini utility to generate 10 dummy jobs
        jobs = generate_dummy_upwork_jobs()

        return jsonify({
            "message": "10 dummy jobs generated successfully.",
            "jobs": jobs
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Failed to generate dummy jobs: {str(e)}"
        }), 500


@job_bp.route('/bulk-create', methods=['POST'])
@login_required
@role_required(UserRoleEnum.admin, UserRoleEnum.salesman)
def bulk_create_upwork_jobs():
    jobs_data = generate_dummy_upwork_jobs()

    if not isinstance(jobs_data, list):
        return jsonify({"error": "Expected a list of jobs"}), 400

    created_jobs = []
    skipped_jobs = []
    errors = []

    for idx, job_data in enumerate(jobs_data):
        try:
            # Step 1: Basic validation
            validation_errors = upwork_jobs_schema.validate(job_data)
            if validation_errors:
                errors.append({
                    "job_index": idx,
                    "job_id": job_data.get("job_id"),
                    "error": validation_errors
                })
                continue

            # Step 2: Check for duplicates
            if UpworkJob.query.filter_by(job_id=job_data.get("job_id")).first():
                skipped_jobs.append(job_data.get("job_id"))
                continue

            # Step 3: AI feasibility assessment
            job_data['feasibility_status'] = assess_job_feasibility(job_data)

            # Step 4: Deserialize and add to session
            upwork_job = upwork_jobs_schema.load(job_data)
            db.session.add(upwork_job)
            created_jobs.append(upwork_job)

        except Exception as e:
            errors.append({
                "job_index": idx,
                "job_id": job_data.get("job_id"),
                "error": str(e)
            })

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to commit jobs: {str(e)}"}), 500

    return jsonify({
        "message": "Bulk job insert complete.",
        "created": [upwork_jobs_schema.dump(job) for job in created_jobs],
        "skipped_existing_job_ids": skipped_jobs,
        "errors": errors
    }), 207  # 207 Multi-Status: Some succeeded, some failed

@job_bp.route('/id-title', methods=['GET'])
@login_required
def get_job_id_and_title():
    jobs = UpworkJob.query.with_entities(UpworkJob.id, UpworkJob.title).all()
    result = [{"id": job.id, "title": job.title} for job in jobs]
    return jsonify(result), 200