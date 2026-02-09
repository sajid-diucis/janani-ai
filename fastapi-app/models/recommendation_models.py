"""
Patient-Centric Food Recommendation Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class HealthConditionType(str, Enum):
    GESTATIONAL_DIABETES = "gestational_diabetes"
    ANEMIA = "anemia"
    HYPERTENSION = "hypertension"
    PREECLAMPSIA = "preeclampsia"
    THYROID = "thyroid"
    NAUSEA = "morning_sickness"
    NONE = "none"

class NutrientNeed(BaseModel):
    """Nutrient requirement for patient"""
    nutrient: str
    daily_requirement: float
    unit: str
    priority: str  # high, medium, low
    reason: str

class PatientProfile(BaseModel):
    """Complete patient health profile"""
    user_id: str
    name: str = "Patient"
    trimester: str = "second"
    week: int = 20
    age: int = 25
    weight_kg: float = 55.0
    conditions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    budget_weekly_bdt: float = 1500.0

class RecommendedFood(BaseModel):
    """Single food recommendation"""
    id: str
    name_bengali: str
    name_english: str
    why_recommended: str
    nutrients_provided: List[str]
    daily_amount: str
    price_per_unit: float
    unit: str
    weekly_quantity: float
    weekly_cost: float
    cooking_tips: List[str] = Field(default_factory=list)

class FoodToAvoid(BaseModel):
    """Food to avoid with reason"""
    name_bengali: str
    name_english: str
    reason: str
    safe_alternative: str

class DailyMealPlan(BaseModel):
    """Single day meal plan"""
    day: str
    breakfast: List[str]
    lunch: List[str]
    snacks: List[str]
    dinner: List[str]

class ShoppingItem(BaseModel):
    """Shopping list item"""
    name_bengali: str
    name_english: str
    quantity: str
    estimated_price: float

class FoodRecommendationRequest(BaseModel):
    """Request for personalized food recommendations"""
    user_id: str = "default_user"
    budget_weekly: float = Field(default=1500, description="Weekly budget in BDT")
    preferences: List[str] = Field(default_factory=list)

class FoodRecommendationResponse(BaseModel):
    """Complete personalized food recommendation response"""
    patient_profile: PatientProfile
    nutrient_needs: List[NutrientNeed]
    recommended_foods: List[RecommendedFood]
    foods_to_avoid: List[FoodToAvoid]
    weekly_meal_plan: Optional[List[DailyMealPlan]] = None
    shopping_list: List[ShoppingItem]
    total_weekly_cost: float
    health_tips: List[str]
    generated_at: datetime = Field(default_factory=datetime.now)

class FoodCheckRequest(BaseModel):
    """Check if specific food is safe for patient"""
    user_id: str = "default_user"
    food_name: str

class FoodCheckResponse(BaseModel):
    """Response for food safety check"""
    food_name: str
    is_safe: bool
    safety_level: str  # safe, caution, avoid
    reason: str
    alternative: Optional[str] = None
    tips: List[str] = Field(default_factory=list)

class ImageFoodCheckRequest(BaseModel):
    """Request for image-based food safety check"""
    patient_profile: PatientProfile
    additional_notes: Optional[str] = None

class ImageFoodCheckResponse(BaseModel):
    """Response for image-based food safety check"""
    success: bool
    food_name: Optional[str] = None
    is_safe: Optional[bool] = None
    safety_level: Optional[str] = None  # safe, caution, avoid
    calories: Optional[float] = None
    nutritional_benefits: List[str] = []
    warnings: List[str] = []
    reason: str = ""
    alternatives: List[str] = []
    tips: List[str] = []
    recommendations: str = ""
    confidence: float = Field(default=0.0, ge=0, le=1)
    error: Optional[str] = None
    audio_url: Optional[str] = None


class ConversationalFoodResponse(BaseModel):
    """
    Simple conversational response for food safety check.
    Designed for pregnant mothers who need quick, clear answers.
    """
    success: bool
    # The verdict emoji + text in Bengali
    verdict: str = ""  # e.g., "✅ হ্যাঁ, খেতে পারেন!" or "❌ এটা এড়িয়ে চলুন"
    # One-line conversational message in Bengali
    message: str = ""  # e.g., "এই ডাল আপনার জন্য খুবই ভালো। এতে আয়রন আছে।"
    # Single most important tip (optional)
    tip: Optional[str] = None  # e.g., "লেবু দিয়ে খেলে আরো ভালো শোষণ হবে"
    # Single best alternative if unsafe (optional)
    alternative: Optional[str] = None  # e.g., "এর বদলে মসুর ডাল খান"
    # Food name identified
    food_name: Optional[str] = None
    food_name_bengali: Optional[str] = None
    # Safety indicator for UI coloring
    is_safe: bool = True
    # Error message if failed
    error: Optional[str] = None
    # Audio URL for voice response
    audio_url: Optional[str] = None