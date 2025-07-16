from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, validate, validates_schema, ValidationError
from app.models.project import Project
from app.enums import ProjectStatusEnum

class ProjectSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        load_instance = True
        include_fk = True

    id = auto_field(dump_only=True)

    name = auto_field(
        required=True,
        validate=validate.Length(min=3, max=255)
    )
    description = auto_field(
        allow_none=True,
        validate=validate.Length(max=5000)
    )

    job_id = auto_field(required=True)
    team_lead_id = auto_field(required=True)
    proposal_id = auto_field(required=False, allow_none=True)

    status = fields.String(
    required=False,
    load_default=ProjectStatusEnum.active.value,
    validate=validate.OneOf([e.value for e in ProjectStatusEnum])
)


    start_date = fields.DateTime(
        required=False,
        allow_none=True,
        format='iso'
    )
    end_date = fields.DateTime(
        required=False,
        allow_none=True,
        format='iso'
    )

    created_at = auto_field(dump_only=True)

    # Optional: Validate end_date > start_date
    @validates_schema
    def validate_dates(self, data, **kwargs):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end < start:
            raise ValidationError("End date cannot be before start date.")
