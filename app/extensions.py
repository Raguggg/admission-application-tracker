from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

api = Api(
    version="1.0",
    title="Flask API",
    description="A simple API",
    doc="/api/docs",  # Swagger UI documentation URL
)


def create_admin():
    from app.authentication.models import RoleEnum, User

    admin_user = User.query.filter_by(email="admin@gmail.com").first()
    if admin_user:
        return

    # Create a new admin user if none exists
    admin_user = User(
        name="admin",
        email="admin@gmail.com",
        role=RoleEnum.ADMIN,
    )
    admin_user.set_password("admin")  # Set default password
    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created successfully.")
