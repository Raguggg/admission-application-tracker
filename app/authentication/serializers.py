from flask import Blueprint
from flask_restx import Namespace, fields

from app.authentication.models import RoleEnum

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
auth_ns = Namespace("auth", description="Authentication operations")


user_model = auth_ns.model(
    "User",
    {
        "name": fields.String(required=True, description="User full name"),
        "email": fields.String(required=True, description="User email address"),
        "password": fields.String(required=True, description="User password"),
        "role": fields.String(
            required=False,
            description="Role: Must be 'admin' or 'user'",
            enum=[RoleEnum.USER, RoleEnum.ADMIN],
        ),
    },
)


login_model = auth_ns.model(
    "UserLogin",
    {
        "email": fields.String(required=True, description="User email address"),
        "password": fields.String(required=True, description="User password"),
    },
)
