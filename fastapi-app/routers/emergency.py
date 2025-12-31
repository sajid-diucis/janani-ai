from fastapi import APIRouter, HTTPException

from models import EmergencyCheckRequest, EmergencyCheckResponse
from services.emergency_service import EmergencyService

router = APIRouter()
emergency_service = EmergencyService()

@router.post("/check", response_model=EmergencyCheckResponse)
async def check_emergency(request: EmergencyCheckRequest):
    """Check if message contains emergency keywords"""
    try:
        result = await emergency_service.check_emergency(request.text)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keywords")
async def get_emergency_keywords():
    """Get list of emergency keywords"""
    return {
        "keywords": emergency_service.get_emergency_keywords(),
        "description": "Bengali keywords that trigger emergency alerts"
    }