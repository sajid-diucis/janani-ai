from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Voice/Speech Models
class VoiceTranscriptionRequest(BaseModel):
    """Request model for voice transcription"""
    pass  # File will be handled as UploadFile

class VoiceTranscriptionResponse(BaseModel):
    """Response model for voice transcription"""
    success: bool
    transcription: Optional[str] = None
    language_detected: str = "bn-BD"
    confidence: float = 0.0
    error: Optional[str] = None

class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech conversion"""
    text: str
    language: str = "bn"

# Chat Models
class ChatMessageRequest(BaseModel):
    """Request model for chat messages"""
    message: str
    conversation_id: Optional[str] = None
    user_context: Optional[dict] = None

class ChatMessageResponse(BaseModel):
    """Response model for chat messages"""
    success: bool
    response: Optional[str] = None
    conversation_id: str
    is_emergency: bool = False
    emergency_level: str = "normal"  # normal, warning, critical
    timestamp: datetime
    audio_url: Optional[str] = None
    error: Optional[str] = None

# Emergency Models
class EmergencyCheckRequest(BaseModel):
    """Request model for emergency detection"""
    text: str

class EmergencyCheckResponse(BaseModel):
    """Response model for emergency detection"""
    is_emergency: bool
    emergency_level: str = "normal"  # normal, warning, critical
    detected_keywords: List[str] = []
    recommendation: str
    urgent_action: Optional[str] = None

# Image Analysis Models
class ImageAnalysisRequest(BaseModel):
    """Base request model for image analysis"""
    pass  # File will be handled as UploadFile

class PrescriptionAnalysisResponse(BaseModel):
    """Response model for prescription analysis"""
    success: bool
    medicines: List[dict] = []
    safety_info: dict = {}
    warnings: List[str] = []
    recommendations: str = ""
    pregnancy_safe: Optional[bool] = None
    audio_url: Optional[str] = None
    error: Optional[str] = None

class FoodAnalysisResponse(BaseModel):
    """Response model for food analysis"""
    success: bool
    food_name: Optional[str] = None
    calories: Optional[int] = None
    pregnancy_safe: Optional[bool] = None
    nutritional_benefits: List[str] = []
    warnings: List[str] = []
    recommendations: str = ""
    audio_url: Optional[str] = None
    error: Optional[str] = None

# General Response Models
class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str
    app: str
    version: str
    apis_configured: dict