from fastapi import APIRouter

router = APIRouter(
    prefix='/analytics',
    tags=['analytics']
)

@router.get('/user-stats')
async def get_user_stats():
    # Placeholder for user statistics logic
    return {"total_users": 100, "active_users": 80}