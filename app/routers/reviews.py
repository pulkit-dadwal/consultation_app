from fastapi import APIRouter

router = APIRouter(
    prefix='/reviews',
    tags=['reviews']
)

@router.post('/')
async def create_review():
    # Placeholder for creating a review logic
    return {"message": "Review created successfully"}