from enum import Enum

from flask_login import UserMixin
from sqlalchemy import Column
from sqlalchemy import Enum as sqlEnum
from sqlalchemy import Integer, String
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    role = Column(sqlEnum(RoleEnum), default=RoleEnum.USER, nullable=False)

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(str(self.password), password)

    def is_admin(self) -> bool:
        return self.role == RoleEnum.ADMIN  # pyright: ignore

    def __repr__(self) -> str:
        return f"<User {self.name} ({self.email})>"
