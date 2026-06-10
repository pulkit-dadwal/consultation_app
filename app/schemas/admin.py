from pydantic import BaseModel, EmailStr


class PromoteUserRequest(BaseModel):
    email: EmailStr
