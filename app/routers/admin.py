from fastapi import APIRouter, status
from app.schemas.admin import PromoteUserRequest
from app.services.admin_service import promote_client_to_consultant
from app.core.security import db_dependency, user_dependency

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


@router.post('/promote', status_code=status.HTTP_200_OK)
async def promote_user_endpoint(promote_request: PromoteUserRequest, db: db_dependency, user: user_dependency):
    """Promote a client to a consultant using their email."""
    return await promote_client_to_consultant(db, user, promote_request)
