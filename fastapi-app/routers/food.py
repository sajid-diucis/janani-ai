"""
Food Analysis Router with Multi-Stage RAG
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from models.food_models import (
    FoodAnalysisRequest, FoodAnalysisResponse,
    HealthProfile, HealthDocumentUpload
)
from services.food_rag_service import food_rag_pipeline


from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from services.vision_service import VisionService

router = APIRouter(prefix="/api/food", tags=["Food Analysis"])
vision_service = VisionService()


@router.post("/analyze", response_model=FoodAnalysisResponse)
async def analyze_food(request: FoodAnalysisRequest):
    """
    Analyze food safety using multi-stage RAG pipeline
    
    খাদ্য বিশ্লেষণ (Food Analysis)
    
    4-Stage Pipeline:
    1. Health Profile RAG - Retrieve patient context
    2. AI Reasoning (LLM-1) - Analyze query intent
    3. Nutrition Data RAG - Get food knowledge
    4. Final Decision (LLM-2) - Generate Bengali response
    """
    try:
        result = await food_rag_pipeline.analyze_food(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Food analysis failed: {str(e)}"
        )

@router.post("/health-profile")
async def create_health_profile(profile: HealthProfile):
    """
    Create or update patient health profile
    
    স্বাস্থ্য প্রোফাইল তৈরি করুন
    """
    try:
        food_rag_pipeline.add_health_profile(profile)
        return {
            "status": "success",
            "message": "Health profile saved successfully",
            "user_id": profile.user_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save health profile: {str(e)}"
        )

@router.get("/check-safety/{food_name}")
async def quick_safety_check(
    food_name: str,
    trimester: str = "second",
    user_id: str = None
):
    """
    Quick food safety check (simplified endpoint)
    
    দ্রুত খাদ্য নিরাপত্তা পরীক্ষা
    """
    try:
        from models.food_models import TrimesterStage
        
        # Convert trimester string to enum
        trimester_map = {
            "first": TrimesterStage.FIRST,
            "second": TrimesterStage.SECOND,
            "third": TrimesterStage.THIRD,
            "postpartum": TrimesterStage.POSTPARTUM
        }
        
        request = FoodAnalysisRequest(
            food_name=food_name,
            trimester=trimester_map.get(trimester.lower(), TrimesterStage.SECOND),
            user_id=user_id,
            include_alternatives=True,
            include_nutrition=False
        )
        
        result = await food_rag_pipeline.analyze_food(request)
        
        return {
            "food_name": food_name,
            "safety": result.stage4_final.safety_decision,
            "explanation_bengali": result.stage4_final.explanation_bengali,
            "risks": result.stage4_final.risks,
            "alternatives": result.stage4_final.alternatives
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Safety check failed: {str(e)}"
        )

@router.get("/list")
async def list_foods():
    """
    List all foods in database
    
    সমস্ত খাবার দেখুন
    """
    try:
        foods = food_rag_pipeline.food_database
        return {
            "count": len(foods),
            "foods": [
                {
                    "id": food.id,
                    "name_bengali": food.name_bengali,
                    "name_english": food.name_english,
                    "category": food.category
                }
                for food in foods.values()
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list foods: {str(e)}"
        )

# ==================== VISUAL MENU GENERATION ====================

# In-memory store for food-specific profiles (separate from midwife profile for now)
food_profiles = {}

from models.food_models import MenuPlanResponse
from services.ai_service import AIService
import json

ai_service = AIService()

@router.post("/profile")
async def update_food_profile(profile: dict):
    """
    Update user profile for food recommendations
    """
    try:
        user_id = profile.get("user_id", "anonymous")
        food_profiles[user_id] = profile
        return {"success": True, "message": "Profile updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations", response_model=MenuPlanResponse)
async def get_visual_menu(request: dict):
    """
    Generate a 5-item Visual Menu with prices & images
    """
    try:
        user_id = request.get("user_id", "anonymous")
        budget = request.get("budget_weekly", 2000)
        
        # Get profile
        profile = food_profiles.get(user_id, {})
        
        # Extract context
        name = profile.get("name", "Expectant Mother")
        trimester = profile.get("trimester", "second")
        conditions = profile.get("conditions", [])
        
        # Generate Menu via Gemini
        json_str = await ai_service.generate_visual_menu_plan(
            user_name=name,
            trimester=trimester,
            conditions=conditions,
            budget=budget
        )
        
        # Parse and return
        menu_data = json.loads(json_str)
        return menu_data

    except Exception as e:
        print(f"Menu Gen Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Menu generation failed: {str(e)}"
        )

# ==================== DASHBOARD COMPATIBILITY ENDPOINTS ====================

@router.post("/check")
async def check_food_text_compatibility(request: dict):
    """
    Compatibility endpoint for Dashboard Text Search
    Call GET /check-safety internally
    """
    try:
        food_name = request.get("food_name")
        if not food_name:
            raise HTTPException(status_code=400, detail="food_name required")
            
        # Re-use existing GET logic logic or RAG
        # Using GET for simplicity as it works with plain strings
        result = await quick_safety_check(food_name=food_name)
        
        # Format response to match Dashboard expectation (data.safe)
        # Dashboard expects { data: { safety_result: { ... } }, safe: boolean }
        # The GET returns { safety: "Safe" | "Unsafe", ... }
        
        safety_val = str(result["safety"]).lower()
        is_safe = safety_val == "safe"
        is_caution = safety_val == "caution"
        
        return {
            "safe": is_safe or is_caution,
            "caution": is_caution,
            "data": {
                "safety_result": {
                    "safe": is_safe or is_caution,
                    "is_caution": is_caution,
                    "reason_bengali": result["explanation_bengali"],
                    "alternatives_bengali": result["alternatives"]
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick-check")
async def check_food_image_compatibility(
    image: UploadFile = File(...),
    user_id: str = Form("web")
):
    """
    Compatibility endpoint for Dashboard Image Check
    Delegates to Vision Service
    """
    try:
        contents = await image.read()
        result = await vision_service.analyze_food(contents)
        
        is_safe = result.get("pregnancy_safe", False)
        
        return {
            "safe": is_safe,
            "data": {
                "safety_result": {
                    "safe": is_safe,
                    "reason_bengali": result.get("recommendations", ""), 
                    "alternatives_bengali": [] # Vision might not give Alts
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
