"""
Multi-Stage RAG Pipeline for Food Analysis
Implements 4-stage architecture with ChromaDB
"""
import chromadb
from chromadb.config import Settings
from typing import Optional, List
import time
from pathlib import Path
import json

from models.food_models import (
    FoodAnalysisRequest, FoodAnalysisResponse,
    Stage1HealthContext, Stage2ReasoningResult,
    Stage3NutritionContext, Stage4FinalResponse,
    HealthProfile, FoodItem, SafetyLevel, TrimesterStage
)
from services.embeddings_service import embedding_service
from services.deepseek_service import deepseek_service
from services.document_service import document_service
from config import settings

class FoodRAGPipeline:
    def __init__(self):
        # Initialize ChromaDB
        db_path = Path(__file__).parent.parent / "data" / "chromadb"
        db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize collections
        self.health_profiles_collection = self.client.get_or_create_collection(
            name="health_profiles",
            metadata={"description": "Patient health profiles and medical history"}
        )
        
        self.food_knowledge_collection = self.client.get_or_create_collection(
            name="food_knowledge",
            metadata={"description": "Food safety, nutrition, and maternal health knowledge"}
        )
        
        self.medical_kb_collection = self.client.get_or_create_collection(
            name="medical_kb",
            metadata={"description": "Medical knowledge base for pregnancy"}
        )
        
        # In-memory storage with persistence
        self.health_db_path = Path(__file__).parent.parent / "data" / "food_health_profiles.json"
        self.health_profiles: dict[str, HealthProfile] = self._load_health_profiles()
        self.food_database: dict[str, FoodItem] = {}
        
        # Load initial food data
        self._load_initial_food_data()
    
    def _load_health_profiles(self) -> dict:
        """Load health profiles from JSON"""
        if hasattr(self, 'health_db_path') and self.health_db_path.exists():
            try:
                with open(self.health_db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {uid: HealthProfile(**p) for uid, p in data.items()}
            except Exception as e:
                print(f"Error loading food health profiles: {e}")
        return {}

    def _save_health_profiles(self):
        """Save health profiles to JSON"""
        try:
            self.health_db_path.parent.mkdir(parents=True, exist_ok=True)
            # Handle Pydantic serialization
            data = {}
            for uid, p in self.health_profiles.items():
                try:
                    data[uid] = p.model_dump(mode='json')
                except AttributeError:
                    import json as std_json
                    data[uid] = std_json.loads(p.json())
            
            with open(self.health_db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving food health profiles: {e}")

    def _load_initial_food_data(self):
        """Load sample food data into database"""
        # Sample data for common Bengali foods
        foods_data = [
            {
                "id": "food_001",
                "name_english": "Hilsa Fish",
                "name_bengali": "ইলিশ মাছ",
                "category": "seafood",
                "safety_first_trimester": "caution",
                "safety_second_trimester": "safe",
                "safety_third_trimester": "safe",
                "safety_postpartum": "safe",
                "reasons": {
                    "first": "High mercury risk in first trimester, consume in moderation",
                    "second": "Rich in omega-3, safe when cooked properly",
                    "third": "Excellent for baby brain development",
                    "postpartum": "Boosts lactation and recovery"
                },
                "benefits": ["Omega-3 fatty acids", "High protein", "Vitamin D", "Brain development"],
                "risks": ["Mercury content", "Allergies", "Must be fully cooked"],
                "alternatives": ["Rui fish (রুই)", "Katla fish (কাতলা)", "Salmon"],
                "cooking_tips": ["Cook thoroughly", "Avoid raw or undercooked", "Steam or bake preferred"],
                "avg_price_bdt": 1200.0,
                "nutrition": {
                    "calories": 310,
                    "protein": 22.0,
                    "carbohydrates": 0.0,
                    "fat": 24.0,
                    "fiber": 0.0,
                    "iron": 1.5,
                    "calcium": 40.0,
                    "folate": 15.0
                }
            },
            {
                "id": "food_002",
                "name_english": "Papaya",
                "name_bengali": "পেঁপে",
                "category": "fruits",
                "safety_first_trimester": "avoid",
                "safety_second_trimester": "caution",
                "safety_third_trimester": "caution",
                "safety_postpartum": "safe",
                "reasons": {
                    "first": "Raw/unripe papaya contains latex that can trigger contractions",
                    "second": "Only ripe papaya in small amounts, avoid unripe",
                    "third": "Only ripe papaya in small amounts",
                    "postpartum": "Excellent for digestion and lactation"
                },
                "benefits": ["Vitamin C", "Fiber", "Digestive enzymes", "Folate"],
                "risks": ["Latex in unripe papaya", "May cause contractions", "Allergic reactions"],
                "alternatives": ["Mango (আম)", "Banana (কলা)", "Orange (কমলা)"],
                "cooking_tips": ["Only eat fully ripe", "Avoid raw/green papaya", "Remove seeds"],
                "avg_price_bdt": 60.0,
                "nutrition": {
                    "calories": 43,
                    "protein": 0.5,
                    "carbohydrates": 11.0,
                    "fat": 0.3,
                    "fiber": 1.7,
                    "vitamin_c": 60.9,
                    "folate": 37.0
                }
            },
            {
                "id": "food_003",
                "name_english": "Spinach",
                "name_bengali": "পালং শাক",
                "category": "vegetables",
                "safety_first_trimester": "safe",
                "safety_second_trimester": "safe",
                "safety_third_trimester": "safe",
                "safety_postpartum": "safe",
                "reasons": {
                    "first": "Excellent source of folate for neural development",
                    "second": "Prevents anemia with high iron content",
                    "third": "Supports healthy blood and bones",
                    "postpartum": "Boosts milk production and recovery"
                },
                "benefits": ["High folate", "Iron", "Calcium", "Vitamin K", "Prevents anemia"],
                "risks": ["Oxalates (cook to reduce)", "Kidney stones risk if excessive"],
                "alternatives": ["Kale (কালে)", "Red amaranth (লাল শাক)", "Fenugreek (মেথি)"],
                "cooking_tips": ["Lightly cook to reduce oxalates", "Pair with vitamin C for iron absorption"],
                "avg_price_bdt": 40.0,
                "nutrition": {
                    "calories": 23,
                    "protein": 2.9,
                    "carbohydrates": 3.6,
                    "fat": 0.4,
                    "fiber": 2.2,
                    "iron": 2.7,
                    "calcium": 99.0,
                    "folate": 194.0
                }
            },
            {
                "id": "food_004",
                "name_english": "Green Tea",
                "name_bengali": "সবুজ চা",
                "category": "beverages",
                "safety_first_trimester": "caution",
                "safety_second_trimester": "caution",
                "safety_third_trimester": "caution",
                "safety_postpartum": "caution",
                "reasons": {
                    "first": "Limit to 1 cup/day due to caffeine",
                    "second": "Caffeine can affect iron absorption",
                    "third": "May interfere with folic acid absorption",
                    "postpartum": "Can reduce breast milk iron content"
                },
                "benefits": ["Antioxidants", "May reduce nausea in small amounts"],
                "risks": ["Caffeine content", "Reduces iron absorption", "Affects folate"],
                "alternatives": ["Ginger tea (আদা চা)", "Herbal tea (ভেষজ চা)", "Warm milk (গরম দুধ)"],
                "cooking_tips": ["Max 1 cup per day", "Don't drink with meals", "Weak brew only"],
                "avg_price_bdt": 200.0,
                "nutrition": {
                    "calories": 2,
                    "protein": 0.2,
                    "carbohydrates": 0.0,
                    "fat": 0.0,
                    "fiber": 0.0
                }
            }
        ]
        
        # Load foods into memory and ChromaDB
        for food_data in foods_data:
            # Convert to FoodItem
            food_item = FoodItem(**food_data)
            
            # Generate embedding
            embedding_text = f"{food_item.name_bengali} {food_item.name_english} {food_item.category} {' '.join(food_item.benefits)}"
            food_item.embedding = embedding_service.embed_text(embedding_text)
            
            # Store in memory
            self.food_database[food_item.id] = food_item
            
            # Store in ChromaDB
            self.food_knowledge_collection.add(
                ids=[food_item.id],
                embeddings=[food_item.embedding],
                metadatas=[{
                    "name_english": food_item.name_english,
                    "name_bengali": food_item.name_bengali,
                    "category": food_item.category,
                }],
                documents=[embedding_text]
            )
    
    async def analyze_food(self, request: FoodAnalysisRequest) -> FoodAnalysisResponse:
        """
        Complete 4-stage RAG pipeline
        """
        start_time = time.time()
        
        # Stage 1: Health Profile RAG
        stage1_context = await self._stage1_health_profile_rag(request.user_id, request.trimester)
        
        # Stage 2: AI Reasoning (LLM-1)
        stage2_reasoning = await self._stage2_ai_reasoning(request, stage1_context)
        
        # Stage 3: Nutrition Data RAG
        stage3_nutrition = await self._stage3_nutrition_rag(request.food_name, stage2_reasoning)
        
        # Stage 4: Final Decision (LLM-2)
        stage4_final = await self._stage4_final_decision(
            request, stage1_context, stage2_reasoning, stage3_nutrition
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return FoodAnalysisResponse(
            query=request.food_name,
            stage1_health_context=stage1_context,
            stage2_reasoning=stage2_reasoning,
            stage3_nutrition=stage3_nutrition,
            stage4_final=stage4_final,
            processing_time_ms=processing_time
        )
    
    async def _stage1_health_profile_rag(
        self, user_id: Optional[str], trimester: Optional[TrimesterStage]
    ) -> Optional[Stage1HealthContext]:
        """
        Stage 1: Retrieve health profile from vector database
        """
        if not user_id:
            return None
        
        # 1. Get food-specific profile (manual entry)
        profile = self.health_profiles.get(user_id)
        
        if not profile:
            # Create default profile if not exists
            profile = HealthProfile(
                user_id=user_id,
                trimester=trimester,
                age=28,
                weight_kg=60.0,
                height_cm=160.0,
                conditions=[],
                allergies=[],
                medications=[],
                dietary_restrictions=[]
            )
            self.health_profiles[user_id] = profile
        
        # 2. Augment with Medical Document Data (Unified RAG)
        # Convert food-specific profile to dict for merging
        base_dict = {
            "name": "মা",
            "age": profile.age,
            "current_weight_kg": profile.weight_kg,
            "height_cm": profile.height_cm,
            "trimester": profile.trimester.value if profile.trimester else "second",
            "existing_conditions": [c.condition_name for c in profile.conditions],
            "allergies": profile.allergies,
            "current_medications": profile.medications
        }
        
        augmented = document_service.get_combined_profile(user_id, base_dict)
        
        return Stage1HealthContext(
            user_id=user_id,
            trimester=trimester or profile.trimester,
            relevant_conditions=augmented.get("existing_conditions", []),
            relevant_allergies=augmented.get("allergies", []),
            relevant_restrictions=profile.dietary_restrictions, # Primarily from manual entry
            confidence_score=0.98 if augmented.get("_is_augmented_by_doc") else 0.95
        )
    
    async def _stage2_ai_reasoning(
        self, request: FoodAnalysisRequest, health_context: Optional[Stage1HealthContext]
    ) -> Stage2ReasoningResult:
        """
        Stage 2: AI reasoning using LLM-1 (DeepSeek)
        """
        # Build reasoning prompt
        prompt = f"""You are a maternal health AI assistant analyzing a food safety query.

Query: "{request.food_name}"
"""
        
        if health_context:
            prompt += f"""
Patient Context:
- Trimester: {health_context.trimester}
- Medical Conditions: {', '.join(health_context.relevant_conditions) or 'None'}
- Allergies: {', '.join(health_context.relevant_allergies) or 'None'}
- Dietary Restrictions: {', '.join(health_context.relevant_restrictions) or 'None'}
"""
        
        prompt += """
Analyze this query and provide:
1. Intent (safety_check, nutrition_query, or alternative_search)
2. Risk factors to consider
3. Key concerns for this food
4. Whether to check nutrition data
5. Whether to suggest alternatives

Respond in JSON format only:
{
  "intent": "safety_check",
  "risk_factors": ["list of risk factors"],
  "key_concerns": ["list of concerns"],
  "should_check_nutrition": true,
  "should_suggest_alternatives": false
}
"""
        
        # Call DeepSeek
        response = await deepseek_service.chat(prompt, temperature=0.3)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            import json
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                response_data = json.loads(response[json_start:json_end])
            else:
                raise ValueError("No JSON found in response")
            
            return Stage2ReasoningResult(**response_data)
        except Exception as e:
            # Fallback
            return Stage2ReasoningResult(
                intent="safety_check",
                risk_factors=["Unknown food"],
                key_concerns=["Need more information"],
                should_check_nutrition=True,
                should_suggest_alternatives=True
            )
    
    async def _stage3_nutrition_rag(
        self, food_name: str, reasoning: Stage2ReasoningResult
    ) -> Stage3NutritionContext:
        """
        Stage 3: Retrieve nutrition data from ChromaDB
        """
        # Generate query embedding
        query_embedding = embedding_service.embed_text(food_name)
        
        # Search ChromaDB
        results = self.food_knowledge_collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        # Get primary food with loose threshold since hashes are random but consistent
        # For hash-based embeddings, L2 distance 0 means exact match.
        # But since we repeat hashes, let's just use string match or very close distance.
        if results['ids'] and results['ids'][0]:
            dist = results['distances'][0][0] if results['distances'] else 100.0
            primary_food_id = results['ids'][0][0]
            primary_food = self.food_database.get(primary_food_id)
            
            # If distance is too high (not a match in our hash space), treat as unknown
            # Standard random hash similarity is low. 0.01 is a safe 'near match' threshold for deterministic hashes.
            if dist > 0.1:
                primary_food = None
        else:
            primary_food = None
        
        # Get similar foods
        similar_foods = []
        if primary_food and results['ids'] and len(results['ids'][0]) > 1:
            for i, food_id in enumerate(results['ids'][0][1:]):
                if results['distances'][0][i+1] < 0.2 and food_id in self.food_database:
                    similar_foods.append(self.food_database[food_id])
        
        # Knowledge graph insights
        kg_insights = [
            "খাদ্যটি গর্ভকালীন সময়ে নিরাপদ কি না তা যাচাই করা হচ্ছে।",
            "ডাক্তারের পরামর্শ নেওয়া সবসময়ই উত্তম।"
        ]
        
        if not primary_food:
            # Create default food item
            primary_food = FoodItem(
                id="unknown",
                name_english=food_name,
                name_bengali=food_name,
                category="vegetables",
                safety_first_trimester="caution",
                safety_second_trimester="caution",
                safety_third_trimester="caution",
                safety_postpartum="safe",
                reasons={},
                benefits=["Consult with healthcare provider"],
                risks=["Unknown food - seek medical advice"],
                alternatives=[],
                cooking_tips=["Ensure proper cooking"],
                nutrition={
                    "calories": 0,
                    "protein": 0,
                    "carbohydrates": 0,
                    "fat": 0,
                    "fiber": 0
                }
            )
        
        return Stage3NutritionContext(
            food_data=primary_food,
            similar_foods=similar_foods,
            knowledge_graph_insights=kg_insights
        )
    
    async def _stage4_final_decision(
        self,
        request: FoodAnalysisRequest,
        health_context: Optional[Stage1HealthContext],
        reasoning: Stage2ReasoningResult,
        nutrition: Stage3NutritionContext
    ) -> Stage4FinalResponse:
        """
        Stage 4: Generate final decision using LLM-2 (DeepSeek)
        """
        food_data = nutrition.food_data
        is_known = food_data.id != "unknown"
        trimester = request.trimester or (health_context.trimester if health_context else None)
        
        # Determine initial safety from DB if known
        if is_known:
            if trimester == TrimesterStage.FIRST:
                safety_decision = food_data.safety_first_trimester
                safety_reason = food_data.reasons.get("first", "")
            elif trimester == TrimesterStage.SECOND:
                safety_decision = food_data.safety_second_trimester
                safety_reason = food_data.reasons.get("second", "")
            elif trimester == TrimesterStage.THIRD:
                safety_decision = food_data.safety_third_trimester
                safety_reason = food_data.reasons.get("third", "")
            elif trimester == TrimesterStage.POSTPARTUM:
                safety_decision = food_data.safety_postpartum
                safety_reason = food_data.reasons.get("postpartum", "")
            else:
                safety_decision = SafetyLevel.CAUTION
                safety_reason = "ত্রৈমাসিক তথ্য পাওয়া যায়নি।"
        else:
            # For unknown foods, let LLM decide in Stage 4
            safety_decision = None 
            safety_reason = "Information being verified by AI..."

        # Build comprehensive prompt
        prompt = f"""Generate a detailed safety assessment in Bengali.
        
REQUESTED FOOD: {request.food_name}
TRIMESTER: {trimester}

DATABASE STATUS: {"KNOWN" if is_known else "UNKNOWN TO LOCAL DATABASE"}
"""
        if is_known:
            prompt += f"""
DB INFO:
- Food Name: {food_data.name_bengali}
- Safety: {safety_decision}
- Why: {safety_reason}
- Benefits: {', '.join(food_data.benefits)}
- Risks: {', '.join(food_data.risks)}
- Seasonality: {"Seasonal" if food_data.is_seasonal else "Year-round"} (Months: {food_data.seasonality_months})
- Preparation Req: {food_data.preparation_notes}
"""
        else:
            prompt += """
ACTION: Use your internal medical knowledge to analyze this food's safety for a pregnant woman in the specified trimester.
"""

        prompt += """
Respond with a caring Bengali explanation (100 words).
Also, you MUST finish your response with a JSON-style block at the bottom (for parsing):
DECISION: [safe/caution/avoid]
"""
        
        raw_response = await deepseek_service.chat(prompt, temperature=0.5)
        
        # Extract decision from LLM if unknown
        final_safety = safety_decision
        if not is_known:
            if "DECISION: safe" in raw_response.lower(): final_safety = SafetyLevel.SAFE
            elif "DECISION: avoid" in raw_response.lower(): final_safety = SafetyLevel.AVOID
            else: final_safety = SafetyLevel.CAUTION
        
        explanation_bengali = raw_response.split("DECISION:")[0].strip()
        
        return Stage4FinalResponse(
            safety_decision=final_safety or SafetyLevel.CAUTION,
            confidence=0.95 if is_known else 0.85,
            explanation_bengali=explanation_bengali,
            explanation_english=f"Analyzed {request.food_name} for {trimester} trimester. Result: {final_safety}",
            benefits=food_data.benefits if is_known else ["Nutritional value"],
            risks=food_data.risks if is_known else ["Allergy potential"],
            alternatives=food_data.alternatives if is_known else [],
            cooking_recommendations=food_data.cooking_tips if is_known else ["Wash thoroughly"],
            nutrition_info=food_data.nutrition if is_known and request.include_nutrition else None,
            price_info=food_data.avg_price_bdt if is_known else 0,
            preparation_notes=food_data.preparation_notes if is_known else None,
            is_seasonal=food_data.is_seasonal if is_known else True,
            seasonality_months=food_data.seasonality_months if is_known else []
        )
    
    def add_health_profile(self, profile: HealthProfile):
        """Add or update health profile"""
        self.health_profiles[profile.user_id] = profile
        self._save_health_profiles()
        
        # Store in ChromaDB
        profile_text = f"""
User: {profile.user_id}
Trimester: {profile.trimester}
Conditions: {', '.join([c.condition_name for c in profile.conditions])}
Allergies: {', '.join(profile.allergies)}
Medications: {', '.join(profile.medications)}
Restrictions: {', '.join(profile.dietary_restrictions)}
"""
        
        embedding = embedding_service.embed_text(profile_text)
        
        self.health_profiles_collection.upsert(
            ids=[profile.user_id],
            embeddings=[embedding],
            documents=[profile_text],
            metadatas=[{"user_id": profile.user_id}]
        )

# Global instance
food_rag_pipeline = FoodRAGPipeline()
