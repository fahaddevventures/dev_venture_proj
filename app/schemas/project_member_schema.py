from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import validate, validates_schema, ValidationError, fields
from app.models.project_member import ProjectMember

class ProjectMemberSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProjectMember
        load_instance = True
        include_fk = True  # To serialize/deserialize user_id and project_id

    user_id = auto_field(required=True)
    project_id = auto_field(required=True)

    role_in_project = auto_field(
        required=False,
        allow_none=True,
        validate=validate.Length(min=2, max=100)
    )

    joined_at = auto_field(dump_only=True)

    @validates_schema
    def validate_ids(self, data, **kwargs):
        if not data.get("user_id"):
            raise ValidationError("user_id is required.", field_name="user_id")
        if not data.get("project_id"):
            raise ValidationError("project_id is required.", field_name="project_id")
