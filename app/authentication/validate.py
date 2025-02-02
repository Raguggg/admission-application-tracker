from pydantic import BaseModel
from pydantic.networks import EmailStr

from app.authentication.models import RoleEnum


class UserDTO(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.USER


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str
