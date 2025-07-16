from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import validates, ValidationError
from marshmallow_enum import EnumField

from app.models.upwork_job import UpworkJob
from app.enums import BudgetTypeEnum, FeasibilityEnum

class UpworkJobSchema(SQLAlchemySchema):
    class Meta:
        model = UpworkJob
        load_instance = True
        include_fk = True

    id = auto_field(dump_only=True)
    job_id = auto_field(required=True, error_messages={"required": "Job ID is required."})
    title = auto_field(required=True, error_messages={"required": "Job title is required."})
    description = auto_field(required=True, error_messages={"required": "Description is required."})

    skills = auto_field()
    tags = auto_field()
    category = auto_field()

    client_country = auto_field()
    client_payment_verified = auto_field()
    client_total_spent = auto_field()
    client_jobs_posted = auto_field()
    client_hire_rate = auto_field()
    client_reviews = auto_field()

    budget = auto_field()
    budget_type = EnumField(BudgetTypeEnum, by_value=True, required=False)

    project_length = auto_field()
    hours_per_week = auto_field()

    proposals_submitted = auto_field()
    interviewing = auto_field()
    invites_sent = auto_field()

    connect_required = auto_field()
    expected_cost = auto_field()
    expected_earnings = auto_field()

    posted_at = auto_field()
    job_url = auto_field(required=True, error_messages={"required": "Job URL is required."})

    feasibility_status = EnumField(FeasibilityEnum, by_value=True, required=False)

    created_at = auto_field(dump_only=True)

    # Custom validations
    @validates("job_id")
    def validate_job_id(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Job ID cannot be empty.")

    @validates("title")
    def validate_title(self, value, **kwargs):
        if len(value.strip()) < 5:
            raise ValidationError("Job title must be at least 5 characters long.")

    @validates("description")
    def validate_description(self, value, **kwargs):
        if len(value.strip()) < 20:
            raise ValidationError("Description must be at least 20 characters long.")
