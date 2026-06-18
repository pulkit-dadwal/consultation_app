from enum import Enum

from pydantic import BaseModel, EmailStr

from app.schemas.consultant_request import ConsultantRequestResponse


class ConsultantRequestDecision(str, Enum):
    approved = "approved"
    rejected = "rejected"


class ConsultantRequestReview(BaseModel):
    status: ConsultantRequestDecision
    rejection_reason: str | None = None


class AdminConsultantRequestResponse(ConsultantRequestResponse):
    applicant_name: str
    applicant_email: EmailStr