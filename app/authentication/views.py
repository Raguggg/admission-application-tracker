from flask import request
from flask_login import current_user, login_required, login_user, logout_user
from flask_restx import Resource
from pydantic import ValidationError

from app.authentication.models import RoleEnum, User
from app.authentication.validate import UserDTO, UserLoginDTO
from app.extensions import db

from .serializers import auth_ns, login_model, user_model


@auth_ns.route("/register")
class Register(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = request.json
        if not data:
            return {"message": "No input data provided"}, 400

        try:
            validated_data = UserDTO(**data)
        except (ValueError, ValidationError) as e:
            return {"error": str(e)}, 400

        if User.query.filter_by(email=validated_data.email).first():
            return {"message": "User already exists"}, 400

        if validated_data.role == RoleEnum.ADMIN and (
            not current_user.is_authenticated or not current_user.is_admin()
        ):
            return {"message": "Cannot create admin user"}, 403

        user = User(**validated_data.model_dump())
        user.set_password(validated_data.password)
        db.session.add(user)
        db.session.commit()
        return {"message": "User created successfully"}, 201


@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        """
        Log in a user.
        """
        if request.json is None:
            return {"message": "No input data provided."}, 400
        try:
            data = UserLoginDTO(**request.json)
        except (ValueError, ValidationError) as e:
            return {"error": str(e)}, 400

        user = User.query.filter_by(email=data.email).first()
        if user is None or not user.check_password(data.password):
            return {"message": "Invalid credentials."}, 401

        login_user(user)
        return {
            "message": "Logged in successfully.",
            "name": user.name,
            "is_admin": user.role == RoleEnum.ADMIN,
        }


@auth_ns.route("/logout")
class Logout(Resource):
    @login_required
    def post(self):
        """
        Log out the currently logged-in user.
        """
        logout_user()
        return {"message": "Logged out successfully."}, 200
