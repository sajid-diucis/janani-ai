from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import tempfile
import os

from models import PrescriptionAnalysisResponse, FoodAnalysisResponse
from services.vision_service import VisionService
from services.speech_service import SpeechService
from config import settings

router = APIRouter()
vision_service = VisionService()
speech_service = SpeechService()

# Extended list of allowed image MIME types
ALLOWED_IMAGE_TYPES = [
    "image/jpeg", "image/png", "image/jpg", "image/webp", "image/gif",
    "image/bmp", "image/tiff", "application/octet-stream"  # Some browsers send this
]

def is_valid_image(content_type: str, filename: str) -> bool:
    """Check if file is a valid image by content type or extension"""
    if content_type and content_type.lower() in ALLOWED_IMAGE_TYPES:
        return True
    # Fallback: check file extension
    if filename:
        ext = filename.lower().split(".")[-1]
        if ext in ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"]:
            return True
    return False

@router.post("/prescription/analyze", response_model=PrescriptionAnalysisResponse)
async def analyze_prescription(image: UploadFile = File(...)):
    """Analyze prescription image"""
    try:
        # Validate file type - more flexible check
        if not is_valid_image(image.content_type, image.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format. Content-Type: {image.content_type}, Filename: {image.filename}"
            )

        # Read and validate file size
        contents = await image.read()
        if len(contents) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_file_size/1024/1024}MB"
            )

        # Analyze prescription
        result = await vision_service.analyze_prescription(contents)

        return PrescriptionAnalysisResponse(
            success=True,
            medicines=result.get("medicines", []),
            safety_info=result.get("safety_info", {}),
            warnings=result.get("warnings", []),
            recommendations=result.get("recommendations", ""),
            pregnancy_safe=result.get("pregnancy_safe"),
            audio_url="/api/voice/speak"
        )

    except HTTPException:
        raise
    except Exception as e:
        return PrescriptionAnalysisResponse(success=False, error=str(e))

@router.post("/food/analyze", response_model=FoodAnalysisResponse)
async def analyze_food(image: UploadFile = File(...)):
    """Analyze food image"""
    try:
        # Validate file type - more flexible check
        if not is_valid_image(image.content_type, image.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format. Content-Type: {image.content_type}, Filename: {image.filename}"
            )

        # Read and validate file size
        contents = await image.read()
        if len(contents) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_file_size/1024/1024}MB"
            )

        # Analyze food
        result = await vision_service.analyze_food(contents)

        return FoodAnalysisResponse(
            success=True,
            food_name=result.get("food_name"),
            calories=result.get("calories"),
            pregnancy_safe=result.get("pregnancy_safe"),
            nutritional_benefits=result.get("nutritional_benefits", []),
            warnings=result.get("warnings", []),
            recommendations=result.get("recommendations", ""),
            audio_url="/api/voice/speak"
        )

    except HTTPException:
        raise
    except Exception as e:
        return FoodAnalysisResponse(success=False, error=str(e))