from fastapi import APIRouter

router = APIRouter(
    prefix='/consultations',
    tags=['consultations']
)   

@router.post('/')
async def create_consultation():
    # Placeholder for creating a consultation logic
    return {"message": "Consultation created successfully"}