from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, validate, validates_schema, ValidationError
from app.models.task import Task
from app.enums import TaskStatusEnum, TaskPriorityEnum

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True
        include_fk = True

    id = auto_field(dump_only=True)


    title = auto_field(required=True, validate=validate.Length(min=3, max=255))
    description = auto_field(allow_none=True, validate=validate.Length(max=5000))
    deliverables = auto_field(allow_none=True, validate=validate.Length(max=5000))

    project_id = auto_field(required=True)
    assigned_to = auto_field(required=True)
    created_by = auto_field(required=True)

    status = fields.String(
        load_default=TaskStatusEnum.todo.value,
        validate=validate.OneOf([e.value for e in TaskStatusEnum])
    )
    

    priority = fields.String(
        load_default=TaskPriorityEnum.medium.value,
        validate=validate.OneOf([e.value for e in TaskPriorityEnum])
    )

    due_date = fields.DateTime(
        required=False,
        allow_none=True,
        format='iso'
    )

    created_at = auto_field(dump_only=True)

    @validates_schema
    def validate_due_date(self, data, **kwargs):
        # Optional validation for due_date logic
        pass
