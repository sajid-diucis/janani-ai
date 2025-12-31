"""
Patient-Centric Food Recommendation API Endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import json

from models.recommendation_models import (
    PatientProfile, FoodRecommendationRequest, FoodRecommendationResponse,
    FoodCheckRequest, FoodCheckResponse, ImageFoodCheckRequest, ImageFoodCheckResponse,
    ConversationalFoodResponse
)
from services.recommendation_service import recommendation_service
from services.vision_service import VisionService
from config import settings

router = APIRouter(prefix="/api/food", tags=["Food Recommendations"])
vision_service = VisionService()

# Extended list of allowed image MIME types
ALLOWED_IMAGE_TYPES = [
    "image/jpeg", "image/png", "image/jpg", "image/webp", "image/gif",
    "image/bmp", "image/tiff", "application/octet-stream"
]

def is_valid_image(content_type: str, filename: str) -> bool:
    """Check if file is a valid image by content type or extension"""
    if content_type and content_type.lower() in ALLOWED_IMAGE_TYPES:
        return True
    if filename:
        ext = filename.lower().split(".")[-1]
        if ext in ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"]:
            return True
    return False


@router.get("/health")
async def health_check():
    """Check if recommendation service is healthy"""
    return {"status": "healthy", "service": "food_recommendations"}


@router.post("/check-image", response_model=ImageFoodCheckResponse)
async def check_food_from_image(
    image: UploadFile = File(...),
    patient_data: str = Form(...)
):
    """
    🎯 SMART FOOD CHECK - The Jeff Dean Solution
    
    Upload a food image + patient profile → Get instant personalized safety recommendation
    
    This unified endpoint:
    1. Analyzes the food image (vision AI)
    2. Checks safety against patient's health conditions  
    3. Provides personalized recommendations
    4. Returns alternatives if unsafe
    
    Perfect for: "I have this food, should I eat it?"
    """
    try:
        # Validate image
        if not is_valid_image(image.content_type, image.filename):
            return ImageFoodCheckResponse(
                success=False,
                error=f"Unsupported image format. Content-Type: {image.content_type}"
            )

        # Check file size
        contents = await image.read()
        if len(contents) > settings.max_file_size:
            return ImageFoodCheckResponse(
                success=False,
                error=f"File too large. Max size: {settings.max_file_size/1024/1024}MB"
            )

        # Parse patient profile
        try:
            patient_profile_dict = json.loads(patient_data)
            patient_profile = PatientProfile(**patient_profile_dict)
        except Exception as e:
            return ImageFoodCheckResponse(
                success=False,
                error=f"Invalid patient profile data: {str(e)}"
            )

        # Step 1: Analyze food image
        vision_result = await vision_service.analyze_food(contents)
        food_name = vision_result.get("food_name", "Unknown food")
        
        if not food_name or food_name == "Unknown food":
            return ImageFoodCheckResponse(
                success=False,
                error="Could not identify food from image. Please try a clearer photo."
            )

        # Step 2: Check food safety for this patient
        food_check_request = FoodCheckRequest(
            user_id=patient_profile.user_id,
            food_name=food_name
        )
        safety_result = await recommendation_service.check_food_safety(food_check_request)

        # Step 3: Combine results
        return ImageFoodCheckResponse(
            success=True,
            food_name=food_name,
            is_safe=safety_result.is_safe,
            safety_level=safety_result.safety_level,
            calories=vision_result.get("calories"),
            nutritional_benefits=vision_result.get("nutritional_benefits", []),
            warnings=vision_result.get("warnings", []),
            reason=safety_result.reason,
            alternatives=[safety_result.alternative] if safety_result.alternative else [],
            tips=safety_result.tips,
            recommendations=vision_result.get("recommendations", ""),
            confidence=0.85,  # Combined confidence
            audio_url="/api/voice/speak"
        )

    except Exception as e:
        return ImageFoodCheckResponse(
            success=False,
            error=f"Failed to analyze food: {str(e)}"
        )


@router.post("/quick-check", response_model=ConversationalFoodResponse)
async def quick_food_check(
    image: UploadFile = File(...),
    patient_data: str = Form(...)
):
    """
    🎯 CONVERSATIONAL FOOD CHECK - Simple Bengali Response
    
    Upload a food image → Get ONE simple Bengali sentence answer!
    
    Perfect for busy pregnant mothers who just need to know:
    "এটা খেতে পারবো?" (Can I eat this?)
    
    Response example:
    ✅ "হ্যাঁ, ডাল খেতে পারেন! এতে আয়রন ও প্রোটিন আছে।"
    ❌ "এটা এড়িয়ে চলুন। আপনার ডায়াবেটিস আছে।"
    """
    try:
        # Validate image
        if not is_valid_image(image.content_type, image.filename):
            return ConversationalFoodResponse(
                success=False,
                error="ছবি সঠিক নয়। JPG বা PNG ছবি দিন।"
            )

        contents = await image.read()
        if len(contents) > settings.max_file_size:
            return ConversationalFoodResponse(
                success=False,
                error="ছবি অনেক বড়। ছোট ছবি দিন।"
            )

        # Parse patient profile
        try:
            patient_profile_dict = json.loads(patient_data)
            patient_profile = PatientProfile(**patient_profile_dict)
        except Exception as e:
            return ConversationalFoodResponse(
                success=False,
                error="প্রোফাইল তথ্য সঠিক নয়।"
            )

        # Step 1: Identify food from image
        vision_result = await vision_service.analyze_food(contents)
        food_name = vision_result.get("food_name", "")
        
        if not food_name:
            return ConversationalFoodResponse(
                success=False,
                verdict="🤔 বুঝতে পারছি না",
                message="ছবি থেকে খাবার চিনতে পারছি না। আবার চেষ্টা করুন।",
                error="Could not identify food"
            )

        # Step 2: Get conversational response
        conv_result = recommendation_service.get_conversational_response(food_name, patient_profile)
        
        return ConversationalFoodResponse(
            success=True,
            verdict=conv_result["verdict"],
            message=conv_result["message"],
            tip=conv_result.get("tip"),
            alternative=conv_result.get("alternative"),
            food_name=conv_result.get("food_name"),
            food_name_bengali=conv_result.get("food_name_bengali"),
            is_safe=conv_result["is_safe"],
            audio_url="/api/voice/speak"
        )

    except Exception as e:
        return ConversationalFoodResponse(
            success=False,
            verdict="❌ সমস্যা হয়েছে",
            message="দুঃখিত, কিছু সমস্যা হয়েছে। আবার চেষ্টা করুন।",
            error=str(e)
        )


@router.post("/recommendations", response_model=FoodRecommendationResponse)
async def get_food_recommendations(request: FoodRecommendationRequest):
    """
    Get personalized food recommendations based on patient profile
    
    - Analyzes patient conditions (anemia, diabetes, hypertension)
    - Considers allergies and medications
    - Optimizes for budget
    - Returns recommended foods, foods to avoid, and shopping list
    """
    try:
        response = await recommendation_service.get_recommendations(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check", response_model=FoodCheckResponse)
async def check_food_safety(request: FoodCheckRequest):
    """
    Check if a specific food is safe for the patient
    
    - Checks against patient conditions
    - Checks allergies
    - Provides alternatives if not safe
    """
    try:
        response = await recommendation_service.check_food_safety(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}", response_model=PatientProfile)
async def get_patient_profile(user_id: str):
    """Get patient profile"""
    try:
        profile = recommendation_service.get_patient_profile(user_id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile")
async def update_patient_profile(profile: PatientProfile):
    """Update or create patient profile"""
    try:
        recommendation_service.update_patient_profile(profile)
        return {"status": "success", "message": "Profile updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conditions")
async def get_supported_conditions():
    """Get list of supported health conditions"""
    return {
        "conditions": [
            {"id": "anemia", "name_en": "Anemia", "name_bn": "রকতসবলপত"},
            {"id": "gestational_diabetes", "name_en": "Gestational Diabetes", "name_bn": "গরভকলন ডযবটস"},
            {"id": "hypertension", "name_en": "High Blood Pressure", "name_bn": "উচচ রকতচপ"},
            {"id": "morning_sickness", "name_en": "Morning Sickness", "name_bn": "সকল বম ভব"},
            {"id": "lactose_intolerant", "name_en": "Lactose Intolerance", "name_bn": "দধ হজম ন হওয"}
        ]
    }