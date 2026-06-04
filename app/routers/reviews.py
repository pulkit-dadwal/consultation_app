from fastapi import APIRouter

router = APIRouter(
    prefix='/reviews',
    tags=['reviews']
)

@router.post('/')
async def create_review():
    """Create a review for a consultation."""
    pass
    