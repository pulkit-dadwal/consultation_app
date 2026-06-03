from fastapi import APIRouter

router = APIRouter(
    prefix='/chat',
    tags=['chat']
)

@router.post('/send')
async def send_message():   
    # Placeholder for sending a chat message logic
    return {"message": "Chat message sent successfully"}