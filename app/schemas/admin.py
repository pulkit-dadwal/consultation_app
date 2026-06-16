from enum import Enum
from pydantic import BaseModel


class ConsultantRequestDecision(str, Enum):
    approved = "approved"
    rejected = "rejected"


class ConsultantRequestReview(BaseModel):
    status: ConsultantRequestDecision
    rejection_reason: str | None = None