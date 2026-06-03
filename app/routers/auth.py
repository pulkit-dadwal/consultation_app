from fastapi import APIRouter

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.get('/')
async def get_user_stats():
    return {"message": "authenticating"}