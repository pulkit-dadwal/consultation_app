from uuid import UUID

from fastapi import (
    APIRouter,
    status
)

from app.core.security import (
    db_dependency,
    user_dependency
)

from app.schemas.consultation import (
    ConsultationCreate,
    ConsultationResponse,
    ConsultationExtend
)

from app.services.consultation_service import (
    create_consultation,
    get_consultations,
    get_consultation_by_id,
    accept_consultation,
    reject_consultation,
    request_consultation_extension,
    accept_extension_request,
    reject_extension_request
)

router = APIRouter(
    prefix="/consultations",
    tags=["consultations"]
)


@router.post(
    "/",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_consultation_endpoint(
    consultation_data: ConsultationCreate,
    db: db_dependency,
    user: user_dependency
):
    """Client creates a consultation request."""
    return await create_consultation(db, user, consultation_data)


@router.get(
    "/",
    response_model=list[ConsultationResponse]
)
async def list_consultations_endpoint(
    db: db_dependency,
    user: user_dependency
):
    """List consultations for the current user."""
    return await get_consultations(db, user)


@router.get(
    "/{consultation_id}",
    response_model=ConsultationResponse
)
async def get_consultation_endpoint(
    consultation_id: UUID,
    db: db_dependency,
    user: user_dependency
):
    """Get consultation details."""
    return await get_consultation_by_id(db, user, consultation_id)


@router.patch(
    "/{consultation_id}/accept",
    response_model=ConsultationResponse
)
async def accept_consultation_endpoint(
    consultation_id: UUID,
    db: db_dependency,
    user: user_dependency
):
    """Consultant accepts consultation. Payment is deducted here."""
    return await accept_consultation(db, user, consultation_id)


@router.patch(
    "/{consultation_id}/reject",
    response_model=ConsultationResponse
)
async def reject_consultation_endpoint(
    consultation_id: UUID,
    db: db_dependency,
    user: user_dependency
):
    """Consultant rejects consultation."""
    return await reject_consultation(db, user, consultation_id)


@router.post(
    "/{consultation_id}/extension-request",
    status_code=status.HTTP_201_CREATED
)
async def request_extension_endpoint(
    consultation_id: UUID,
    extension_data: ConsultationExtend,
    db: db_dependency,
    user: user_dependency
):
    """Client requests additional consultation time."""
    return await request_consultation_extension(
        db, user, consultation_id, extension_data
    )


@router.patch(
    "/{consultation_id}/extension-request/accept",
    response_model=ConsultationResponse
)
async def accept_extension_request_endpoint(
    consultation_id: UUID,
    db: db_dependency,
    user: user_dependency
):
    """Consultant accepts extension request. Additional fee deducted here."""
    return await accept_extension_request(db, user, consultation_id)


@router.patch(
    "/{consultation_id}/extension-request/reject"
)
async def reject_extension_request_endpoint(
    consultation_id: UUID,
    db: db_dependency,
    user: user_dependency
):
    """Consultant rejects extension request."""
    return await reject_extension_request(db, user, consultation_id)