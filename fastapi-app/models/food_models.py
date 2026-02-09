"""
Food Database Models and Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class SafetyLevel(str, Enum):
    SAFE = "safe"
    SAFE_MODERATE = "safe_moderate"  # OK in moderation
    CAUTION = "caution"
    AVOID = "avoid"

class LocalizedResponse(BaseModel):
    """Multilingual response container (P2 Refinement)"""
    bn: str
    en: str
    audio_url_bn: Optional[str] = None

class TrimesterStage(str, Enum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    POSTPARTUM = "postpartum"

class FoodCategory(str, Enum):
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    GRAINS = "grains"
    PROTEINS = "proteins"
    DAIRY = "dairy"
    SEAFOOD = "seafood"
    SPICES = "spices"
    BEVERAGES = "beverages"
    SWEETS = "sweets"

# === Request Models ===

class FoodAnalysisRequest(BaseModel):
    """Main food analysis request"""
    food_name: str = Field(..., description="Name of food in Bengali or English")
    trimester: Optional[TrimesterStage] = None
    user_id: Optional[str] = None
    include_alternatives: bool = True
    include_nutrition: bool = True

class HealthDocumentUpload(BaseModel):
    """Health document upload for profile"""
    user_id: str
    document_type: str = Field(..., description="prescription, lab_report, medical_history")
    content: str

# === Food Data Models ===

class NutritionInfo(BaseModel):
    """Nutritional information per 100g"""
    calories: float
    protein: float
    carbohydrates: float
    fat: float
    fiber: float
    iron: Optional[float] = None
    calcium: Optional[float] = None
    folate: Optional[float] = None
    vitamin_a: Optional[float] = None
    vitamin_c: Optional[float] = None

class FoodRecommendation(BaseModel):
    """Specific recommendation for a food item (P0/P1 Refinement)"""
    food_id: str
    safe_portion_size: str  # e.g., "1 cup", "100g"
    max_daily_servings: int = 1
    interactions: List[str] = Field(default_factory=list) # e.g. "Do not combine with iron supplements"
    localized_advice: LocalizedResponse

class FoodItem(BaseModel):
    """Complete food item data"""
    id: str
    name_english: str
    name_bengali: str
    bengali_synonyms: List[str] = Field(default_factory=list)
    category: FoodCategory
    nutrition: NutritionInfo
    safety_first_trimester: SafetyLevel
    safety_second_trimester: SafetyLevel
    safety_third_trimester: SafetyLevel
    safety_postpartum: SafetyLevel
    reasons: Dict[str, str] = Field(default_factory=dict, description="Safety reasons per stage")
    benefits: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    alternatives: List[str] = Field(default_factory=list)
    cooking_tips: List[str] = Field(default_factory=list)
    preparation_notes: Optional[str] = None # e.g. "Do not eat raw", "Wash with salt water"
    is_seasonal: bool = True
    seasonality_months: List[int] = Field(default_factory=list) # 1-12
    avg_price_bdt: Optional[float] = None
    embedding: Optional[List[float]] = None

# === Health Profile Models ===

class HealthCondition(BaseModel):
    """Medical condition"""
    condition_name: str
    severity: str  # mild, moderate, severe
    diagnosed_date: Optional[datetime] = None
    restrictions: List[str] = Field(default_factory=list)

class HealthProfile(BaseModel):
    """Patient health profile"""
    user_id: str
    trimester: Optional[TrimesterStage] = None
    age: int
    weight_kg: float
    height_cm: float
    conditions: List[HealthCondition] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# === RAG Response Models ===

class Stage1HealthContext(BaseModel):
    """Stage 1: Retrieved health context"""
    user_id: str
    trimester: Optional[TrimesterStage]
    relevant_conditions: List[str]
    relevant_allergies: List[str]
    relevant_restrictions: List[str]
    confidence_score: float

class Stage2ReasoningResult(BaseModel):
    """Stage 2: AI reasoning output"""
    intent: str  # safety_check, nutrition_query, alternative_search
    risk_factors: List[str]
    key_concerns: List[str]
    should_check_nutrition: bool
    should_suggest_alternatives: bool

class Stage3NutritionContext(BaseModel):
    """Stage 3: Nutrition data retrieval"""
    food_data: FoodItem
    similar_foods: List[FoodItem] = Field(default_factory=list)
    knowledge_graph_insights: List[str] = Field(default_factory=list)

class Stage4FinalResponse(BaseModel):
    """Stage 4: Final decision output"""
    safety_decision: SafetyLevel
    confidence: float
    explanation_bengali: str
    explanation_english: str
    benefits: List[str]
    risks: List[str]
    alternatives: List[str]
    cooking_recommendations: List[str]
    nutrition_info: Optional[NutritionInfo] = None
    price_info: Optional[float] = None
    preparation_notes: Optional[str] = None
    is_seasonal: bool = True
    seasonality_months: List[int] = Field(default_factory=list)

# === Complete Pipeline Response ===

class FoodAnalysisResponse(BaseModel):
    """Complete multi-stage RAG response"""
    query: str
    stage1_health_context: Optional[Stage1HealthContext] = None
    stage2_reasoning: Stage2ReasoningResult
    stage3_nutrition: Stage3NutritionContext
    stage4_final: Stage4FinalResponse
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.now)

# === Visual Menu Generation Models ===

class MenuPlanItem(BaseModel):
    """Single item in a generated menu"""
    name_bengali: str = Field(..., description="Dish name in Bengali")
    name_english: str = Field(..., description="Dish name in English")
    calories: int = Field(..., description="Estimated calories per serving")
    protein_g: float = Field(..., description="Estimated protein grams")
    price_bdt: int = Field(..., description="Estimated market price in BDT")
    image_prompt: str = Field(..., description="Detailed prompt for generating food image")
    image_url: Optional[str] = Field(None, description="Generated image URL")
    benefits_key: str = Field(..., description="Key health benefit (1-2 words)")
    recipe_bengali: Optional[str] = Field(None, description="Detailed recipe in Bengali")
    audio_script_bengali: Optional[str] = Field(None, description="Script for audio playback in Noakhali style")
    phase: int = Field(1, description="Loading phase (1, 2, or 3)")
    
class MenuPlanResponse(BaseModel):
    """Full visual menu plan"""
    title_bengali: str
    total_calories: int
    total_price_bdt: int
    items: List[MenuPlanItem]
    health_tip: str
    phase: int = Field(1, description="Current loading phase")
    confidence_score: float
