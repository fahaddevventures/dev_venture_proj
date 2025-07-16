from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import validates, ValidationError
from app.models.user import User
from app.enums import UserRoleEnum
from marshmallow_enum import EnumField

class UserSchema(SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True

    id = auto_field(dump_only=True)
    first_name = auto_field(required=True,error_messages={"required": "First name is required."})
    last_name = auto_field(required=True,error_messages={"required": "Last name is required."})
    email = auto_field(required=True,error_messages={"required": "Email is required."})
    password = auto_field(required=True, load_only=True,error_messages={"required": "Password is required."})
    role = EnumField(UserRoleEnum, by_value=True, required=False,error_messages={"required": "USer Role is required."})
    contact = auto_field(required=True,error_messages={"required": "Contact number is required."})
    created_at = auto_field(dump_only=True)

    @validates("email")
    def validate_email(self, value, **kwargs):
        if "@" not in value or "." not in value:
            raise ValidationError("Invalid email address.")

