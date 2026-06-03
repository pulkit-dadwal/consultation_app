import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    client = "client"
    consultant = "consultant"
    admin = "admin"


class CreateUserRequest(BaseModel):
    name: str = Field(..., max_length=120)
    email: EmailStr
    role: UserRole
    password: str = Field(..., min_length=8)