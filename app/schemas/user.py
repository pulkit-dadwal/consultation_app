from decimal import Decimal
from enum import Enum
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    client = "client"
    consultant = "consultant"
    admin = "admin"


class CreateUserRequest(BaseModel):
    name: str = Field(..., max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    # UserRole was already defined above but wasn't being used here — now wired in
    role: UserRole
    wallet_balance: Decimal

    class Config:
        from_attributes = True