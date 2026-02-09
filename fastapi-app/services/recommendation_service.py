"""
Patient-Centric Food Recommendation Service
Analyzes patient health profile and recommends optimal foods
"""
from typing import List, Dict, Optional
from datetime import datetime
import json

from models.recommendation_models import (
    PatientProfile, NutrientNeed, RecommendedFood, FoodToAvoid,
    ShoppingItem, FoodRecommendationRequest, FoodRecommendationResponse,
    FoodCheckRequest, FoodCheckResponse
)
from services.ai_service import AIService

class FoodRecommendationService:
    def __init__(self):
        # Initialize AI service for smart food analysis
        self.ai_service = AIService()
        
        # Sample patient profiles (in production, from database)
        self.patient_profiles: Dict[str, PatientProfile] = {
            "default_user": PatientProfile(
                user_id="default_user",
                name="Patient",
                trimester="second",
                week=20,
                age=25,
                weight_kg=55.0,
                conditions=["anemia"],
                allergies=[],
                medications=["iron_supplement", "folic_acid"],
                budget_weekly_bdt=1500.0
            )
        }
        
        # Nutrient requirements by condition
        self.condition_nutrient_needs = {
            "anemia": [
                NutrientNeed(nutrient="Iron", daily_requirement=27, unit="mg", priority="high", reason="Anemia treatment"),
                NutrientNeed(nutrient="Vitamin C", daily_requirement=85, unit="mg", priority="high", reason="Iron absorption"),
                NutrientNeed(nutrient="Folate", daily_requirement=600, unit="mcg", priority="high", reason="Red blood cell production")
            ],
            "gestational_diabetes": [
                NutrientNeed(nutrient="Fiber", daily_requirement=28, unit="g", priority="high", reason="Blood sugar control"),
                NutrientNeed(nutrient="Protein", daily_requirement=71, unit="g", priority="high", reason="Stable energy"),
                NutrientNeed(nutrient="Complex Carbs", daily_requirement=175, unit="g", priority="medium", reason="Slow release energy")
            ],
            "hypertension": [
                NutrientNeed(nutrient="Potassium", daily_requirement=2900, unit="mg", priority="high", reason="Blood pressure control"),
                NutrientNeed(nutrient="Magnesium", daily_requirement=350, unit="mg", priority="high", reason="Vascular health"),
                NutrientNeed(nutrient="Calcium", daily_requirement=1000, unit="mg", priority="medium", reason="Blood pressure regulation")
            ]
        }
        
        # Base pregnancy nutrients
        self.base_pregnancy_needs = [
            NutrientNeed(nutrient="Folate", daily_requirement=600, unit="mcg", priority="high", reason="Neural tube development"),
            NutrientNeed(nutrient="Iron", daily_requirement=27, unit="mg", priority="high", reason="Blood volume increase"),
            NutrientNeed(nutrient="Calcium", daily_requirement=1000, unit="mg", priority="high", reason="Baby bone development"),
            NutrientNeed(nutrient="Protein", daily_requirement=71, unit="g", priority="high", reason="Tissue growth"),
            NutrientNeed(nutrient="DHA", daily_requirement=200, unit="mg", priority="medium", reason="Brain development")
        ]
        
        # Food database with Bengali names
        self.food_database = [
            {
                "id": "spinach",
                "name_bengali": "Palong Shak",
                "name_english": "Spinach",
                "nutrients": ["Iron", "Folate", "Vitamin C", "Calcium"],
                "price_per_kg": 40,
                "unit": "bundle",
                "price_per_unit": 30,
                "good_for": ["anemia", "all_pregnancy"],
                "avoid_for": [],
                "daily_amount": "1 cup cooked",
                "weekly_quantity": 7,
                "cooking_tips": ["Lightly cook to reduce oxalates", "Pair with lemon for iron absorption"]
            },
            {
                "id": "eggs",
                "name_bengali": "Dim",
                "name_english": "Eggs",
                "nutrients": ["Protein", "Iron", "Choline", "Vitamin D"],
                "price_per_kg": 180,
                "unit": "piece",
                "price_per_unit": 12,
                "good_for": ["all_pregnancy", "anemia"],
                "avoid_for": [],
                "daily_amount": "2 eggs",
                "weekly_quantity": 14,
                "cooking_tips": ["Always cook thoroughly", "Avoid raw eggs"]
            },
            {
                "id": "small_fish",
                "name_bengali": "Choto Mach",
                "name_english": "Small Fish with bones",
                "nutrients": ["Calcium", "Protein", "Omega-3", "Iron"],
                "price_per_kg": 200,
                "unit": "kg",
                "price_per_unit": 200,
                "good_for": ["all_pregnancy", "anemia"],
                "avoid_for": [],
                "daily_amount": "100g",
                "weekly_quantity": 0.5,
                "cooking_tips": ["Cook with bones for calcium", "Fry or curry"]
            },
            {
                "id": "lentils",
                "name_bengali": "Mosur Dal",
                "name_english": "Red Lentils",
                "nutrients": ["Protein", "Iron", "Folate", "Fiber"],
                "price_per_kg": 120,
                "unit": "kg",
                "price_per_unit": 120,
                "good_for": ["all_pregnancy", "anemia", "gestational_diabetes"],
                "avoid_for": [],
                "daily_amount": "1 cup cooked",
                "weekly_quantity": 1,
                "cooking_tips": ["Soak before cooking", "Add turmeric for absorption"]
            },
            {
                "id": "banana",
                "name_bengali": "Kola",
                "name_english": "Banana",
                "nutrients": ["Potassium", "Vitamin B6", "Fiber"],
                "price_per_kg": 60,
                "unit": "dozen",
                "price_per_unit": 60,
                "good_for": ["hypertension", "morning_sickness"],
                "avoid_for": ["gestational_diabetes"],
                "daily_amount": "1 medium",
                "weekly_quantity": 1,
                "cooking_tips": ["Eat ripe for easier digestion"]
            },
            {
                "id": "milk",
                "name_bengali": "Dudh",
                "name_english": "Milk",
                "nutrients": ["Calcium", "Protein", "Vitamin D"],
                "price_per_kg": 80,
                "unit": "liter",
                "price_per_unit": 80,
                "good_for": ["all_pregnancy"],
                "avoid_for": ["lactose_intolerant"],
                "daily_amount": "2 cups",
                "weekly_quantity": 3.5,
                "cooking_tips": ["Boil before drinking", "Can add to tea/coffee"]
            },
            {
                "id": "orange",
                "name_bengali": "Komola",
                "name_english": "Orange",
                "nutrients": ["Vitamin C", "Folate", "Fiber"],
                "price_per_kg": 150,
                "unit": "kg",
                "price_per_unit": 150,
                "good_for": ["anemia", "all_pregnancy"],
                "avoid_for": [],
                "daily_amount": "1 medium",
                "weekly_quantity": 1,
                "cooking_tips": ["Eat fresh for maximum vitamin C", "Drink juice after meals"]
            },
            {
                "id": "chicken",
                "name_bengali": "Murgi",
                "name_english": "Chicken",
                "nutrients": ["Protein", "Iron", "B12", "Zinc"],
                "price_per_kg": 220,
                "unit": "kg",
                "price_per_unit": 220,
                "good_for": ["all_pregnancy", "anemia"],
                "avoid_for": [],
                "daily_amount": "100g",
                "weekly_quantity": 0.5,
                "cooking_tips": ["Cook thoroughly", "Remove skin to reduce fat"]
            },
            {
                "id": "brown_rice",
                "name_bengali": "Lal Chal",
                "name_english": "Brown Rice",
                "nutrients": ["Fiber", "Complex Carbs", "Magnesium"],
                "price_per_kg": 90,
                "unit": "kg",
                "price_per_unit": 90,
                "good_for": ["gestational_diabetes", "all_pregnancy"],
                "avoid_for": [],
                "daily_amount": "1 cup cooked",
                "weekly_quantity": 2,
                "cooking_tips": ["Soak 30 mins before cooking", "Better blood sugar control than white rice"]
            },
            {
                "id": "papaya_green",
                "name_bengali": "Kacha Pepe",
                "name_english": "Green Papaya",
                "nutrients": [],
                "price_per_kg": 40,
                "unit": "piece",
                "price_per_unit": 40,
                "good_for": [],
                "avoid_for": ["all_pregnancy"],
                "daily_amount": "AVOID",
                "weekly_quantity": 0,
                "cooking_tips": ["AVOID during pregnancy - can cause contractions"]
            },
            {
                "id": "mango",
                "name_bengali": "Aam",
                "name_english": "Mango",
                "nutrients": ["Vitamin A", "Vitamin C", "Fiber"],
                "price_per_kg": 150,
                "unit": "kg",
                "price_per_unit": 150,
                "good_for": ["all_pregnancy"],
                "avoid_for": ["gestational_diabetes"],
                "daily_amount": "1/2 cup",
                "weekly_quantity": 0.5,
                "cooking_tips": ["Limit if diabetic due to high sugar"]
            }
        ]
        
        # Foods to always avoid in pregnancy
        self.universal_avoid = [
            FoodToAvoid(name_bengali="Kacha Pepe", name_english="Green Papaya", reason="Can cause contractions", safe_alternative="Ripe papaya in moderation"),
            FoodToAvoid(name_bengali="Kacha Dim", name_english="Raw Eggs", reason="Salmonella risk", safe_alternative="Fully cooked eggs"),
            FoodToAvoid(name_bengali="Kacha Mach/Sushi", name_english="Raw Fish/Sushi", reason="Bacteria and parasites", safe_alternative="Cooked fish"),
            FoodToAvoid(name_bengali="Otyodhik Caffeine", name_english="Excess Caffeine", reason="Affects baby development", safe_alternative="Max 200mg/day (1 cup coffee)")
        ]
    
    def get_patient_profile(self, user_id: str) -> PatientProfile:
        """Get or create patient profile"""
        if user_id in self.patient_profiles:
            return self.patient_profiles[user_id]
        # Return default profile
        return self.patient_profiles["default_user"]
    
    def update_patient_profile(self, profile: PatientProfile):
        """Update patient profile"""
        self.patient_profiles[profile.user_id] = profile
    
    def calculate_nutrient_needs(self, profile: PatientProfile) -> List[NutrientNeed]:
        """Calculate nutrient needs based on patient conditions"""
        needs = list(self.base_pregnancy_needs)
        
        for condition in profile.conditions:
            if condition in self.condition_nutrient_needs:
                for need in self.condition_nutrient_needs[condition]:
                    # Check if already exists, update priority if higher
                    existing = next((n for n in needs if n.nutrient == need.nutrient), None)
                    if existing:
                        if need.priority == "high":
                            existing.priority = "high"
                            existing.daily_requirement = max(existing.daily_requirement, need.daily_requirement)
                    else:
                        needs.append(need)
        
        return needs
    
    def get_recommended_foods(self, profile: PatientProfile, budget: float) -> List[RecommendedFood]:
        """Get personalized food recommendations"""
        recommended = []
        total_cost = 0
        
        for food in self.food_database:
            # Skip if patient is allergic
            if any(allergy.lower() in food["name_english"].lower() for allergy in profile.allergies):
                continue
            
            # Skip if should avoid for patient's conditions
            should_avoid = False
            for condition in profile.conditions:
                if condition in food["avoid_for"]:
                    should_avoid = True
                    break
            
            if should_avoid or "all_pregnancy" in food["avoid_for"]:
                continue
            
            # Check if good for patient's conditions
            is_recommended = "all_pregnancy" in food["good_for"]
            for condition in profile.conditions:
                if condition in food["good_for"]:
                    is_recommended = True
                    break
            
            if is_recommended:
                weekly_cost = food["price_per_unit"] * food["weekly_quantity"]
                if total_cost + weekly_cost <= budget:
                    recommended.append(RecommendedFood(
                        id=food["id"],
                        name_bengali=food["name_bengali"],
                        name_english=food["name_english"],
                        why_recommended=f"Good source of {', '.join(food['nutrients'][:3])}",
                        nutrients_provided=food["nutrients"],
                        daily_amount=food["daily_amount"],
                        price_per_unit=food["price_per_unit"],
                        unit=food["unit"],
                        weekly_quantity=food["weekly_quantity"],
                        weekly_cost=weekly_cost,
                        cooking_tips=food["cooking_tips"]
                    ))
                    total_cost += weekly_cost
        
        return recommended
    
    def get_foods_to_avoid(self, profile: PatientProfile) -> List[FoodToAvoid]:
        """Get foods patient should avoid"""
        avoid_list = list(self.universal_avoid)
        
        for food in self.food_database:
            for condition in profile.conditions:
                if condition in food["avoid_for"]:
                    # Find alternative
                    alternative = "Consult doctor"
                    for alt_food in self.food_database:
                        if condition in alt_food["good_for"] and set(food["nutrients"]) & set(alt_food["nutrients"]):
                            alternative = alt_food["name_bengali"]
                            break
                    
                    avoid_list.append(FoodToAvoid(
                        name_bengali=food["name_bengali"],
                        name_english=food["name_english"],
                        reason=f"Not recommended for {condition}",
                        safe_alternative=alternative
                    ))
        
        # Add allergy-based avoidance
        for allergy in profile.allergies:
            for food in self.food_database:
                if allergy.lower() in food["name_english"].lower():
                    avoid_list.append(FoodToAvoid(
                        name_bengali=food["name_bengali"],
                        name_english=food["name_english"],
                        reason=f"Allergic to {allergy}",
                        safe_alternative="Avoid completely"
                    ))
        
        return avoid_list
    
    def generate_shopping_list(self, recommended_foods: List[RecommendedFood]) -> List[ShoppingItem]:
        """Generate weekly shopping list"""
        shopping = []
        for food in recommended_foods:
            shopping.append(ShoppingItem(
                name_bengali=food.name_bengali,
                name_english=food.name_english,
                quantity=f"{food.weekly_quantity} {food.unit}",
                estimated_price=food.weekly_cost
            ))
        return shopping
    
    async def get_recommendations(self, request: FoodRecommendationRequest) -> FoodRecommendationResponse:
        """Main method: Get personalized food recommendations"""
        profile = self.get_patient_profile(request.user_id)
        profile.budget_weekly_bdt = request.budget_weekly
        
        nutrient_needs = self.calculate_nutrient_needs(profile)
        recommended_foods = self.get_recommended_foods(profile, request.budget_weekly)
        foods_to_avoid = self.get_foods_to_avoid(profile)
        shopping_list = self.generate_shopping_list(recommended_foods)
        total_cost = sum(item.estimated_price for item in shopping_list)
        
        health_tips = [
            "Drink 8-10 glasses of water daily",
            "Cook food thoroughly",
            "Eat small frequent meals",
            "Eat Vitamin C with iron-rich foods"
        ]
        
        if "anemia" in profile.conditions:
            health_tips.append("Take iron tablets 2 hours before/after tea/coffee")
        
        if "gestational_diabetes" in profile.conditions:
            health_tips.append("Choose brown rice/wheat instead of white rice")
            health_tips.append("Limit sweet fruits")
        
        return FoodRecommendationResponse(
            patient_profile=profile,
            nutrient_needs=nutrient_needs,
            recommended_foods=recommended_foods,
            foods_to_avoid=foods_to_avoid,
            shopping_list=shopping_list,
            total_weekly_cost=total_cost,
            health_tips=health_tips
        )
    
    async def check_food_safety(self, request: FoodCheckRequest) -> FoodCheckResponse:
        """Check if specific food is safe for patient"""
        profile = self.get_patient_profile(request.user_id)
        food_input = request.food_name.lower().strip()
        
        # Bengali to English food mapping for better matching
        bengali_to_english = {
            "আম": "mango", "aam": "mango",
            "পেঁপে": "papaya", "পেপে": "papaya", "pepe": "papaya",
            "কলা": "banana", "kola": "banana",
            "দুধ": "milk", "dudh": "milk",
            "ডিম": "egg", "dim": "egg",
            "মাছ": "fish", "mach": "fish",
            "ডাল": "lentil", "dal": "lentil", "মসুর": "lentil",
            "পালং": "spinach", "palong": "spinach", "শাক": "spinach",
            "ভাত": "rice", "bhat": "rice",
            "কমলা": "orange", "komola": "orange",
            "আপেল": "apple", "apple": "apple",
            "মুরগি": "chicken", "murgi": "chicken",
            "গরু": "beef", "goru": "beef",
            "খাসি": "mutton", "khashi": "mutton",
            "আলু": "potato", "alu": "potato",
            "টমেটো": "tomato", "tomato": "tomato",
            "গাজর": "carrot", "gajor": "carrot",
            "শসা": "cucumber", "shasha": "cucumber",
            "দই": "yogurt", "doi": "yogurt", "curd": "yogurt",
            "চা": "tea", "cha": "tea",
            "কফি": "coffee", "coffee": "coffee",
            "রুটি": "bread", "ruti": "bread",
            "বিস্কুট": "biscuit", "biscuit": "biscuit",
            "চিনি": "sugar", "chini": "sugar",
            "লবণ": "salt", "lobon": "salt",
            "তেল": "oil", "tel": "oil",
            "ঘি": "ghee", "ghee": "ghee",
            "পনির": "cheese", "cheese": "cheese",
            "সবজি": "vegetable", "shobji": "vegetable",
            "ফল": "fruit", "fol": "fruit",
        }
        
        # Extract food name from sentence (remove common Bengali phrases)
        remove_phrases = [
            "খেতে পারবো", "খেতে পারব", "খেতে পারি", "খাওয়া যাবে", 
            "খেলে কি হবে", "খেতে চাই", "কি খেতে", "এটা কি", "কি",
            "can i eat", "is it safe", "should i eat", "can eat",
            "আমি", "আমার", "?", "।"
        ]
        
        extracted_food = food_input
        for phrase in remove_phrases:
            extracted_food = extracted_food.replace(phrase.lower(), "").strip()
        
        # Clean up extra spaces
        extracted_food = " ".join(extracted_food.split())
        
        # Try to find the food name in the input
        found_food = None
        matched_name = extracted_food
        
        # First, check if any Bengali keyword is in the input
        for bengali, english in bengali_to_english.items():
            if bengali in food_input or bengali in extracted_food:
                matched_name = english
                break
        
        # Search in food database
        for food in self.food_database:
            name_en = food["name_english"].lower()
            name_bn = food["name_bengali"].lower()
            
            # Check various matching conditions
            if (matched_name in name_en or 
                name_en in matched_name or
                matched_name in name_bn or
                name_bn in matched_name or
                extracted_food in name_en or
                extracted_food in name_bn or
                name_en in extracted_food or
                name_bn in extracted_food or
                food_input in name_bn or
                name_bn in food_input):
                found_food = food
                break
        
        if not found_food:
            # Use AI to analyze unknown food
            return await self._analyze_unknown_food_with_ai(extracted_food, profile)
        
        # Bengali condition names
        condition_bengali = {
            "gestational_diabetes": "ডায়াবেটিস",
            "anemia": "রক্তস্বল্পতা", 
            "hypertension": "উচ্চ রক্তচাপ",
            "morning_sickness": "বমি ভাব",
            "lactose_intolerant": "দুধে সমস্যা"
        }
        
        # Check if should avoid
        for condition in profile.conditions:
            if condition in found_food["avoid_for"]:
                # Find alternative
                alternative = None
                for alt_food in self.food_database:
                    if condition in alt_food["good_for"]:
                        alternative = alt_food["name_bengali"]
                        break
                
                cond_name = condition_bengali.get(condition, condition)
                return FoodCheckResponse(
                    food_name=found_food["name_bengali"],
                    is_safe=False,
                    safety_level="avoid",
                    reason=f"আপনার {cond_name} আছে, তাই {found_food['name_bengali']} কম খাওয়া ভালো।",
                    alternative=alternative,
                    tips=[f"এর বদলে {alternative} খেতে পারেন" if alternative else "ডাক্তারের পরামর্শ নিন"]
                )
        
        # Check allergies
        for allergy in profile.allergies:
            if allergy.lower() in found_food["name_english"].lower():
                return FoodCheckResponse(
                    food_name=found_food["name_bengali"],
                    is_safe=False,
                    safety_level="avoid",
                    reason=f"আপনার {allergy} এলার্জি আছে। এটা খাবেন না।",
                    alternative=None,
                    tips=["এই খাবার সম্পূর্ণ এড়িয়ে চলুন"]
                )
        
        # Check if universally avoided
        if "all_pregnancy" in found_food.get("avoid_for", []):
            return FoodCheckResponse(
                food_name=found_food["name_bengali"],
                is_safe=False,
                safety_level="avoid",
                reason=f"গর্ভাবস্থায় {found_food['name_bengali']} খাওয়া ঠিক নয়। এটা বাচ্চার ক্ষতি করতে পারে।",
                alternative=None,
                tips=found_food.get("cooking_tips", ["ডাক্তারের পরামর্শ নিন"])
            )
        
        # Food is safe - give encouraging Bengali response
        nutrients = found_food.get("nutrients", [])[:2]
        nutrient_bengali = {
            "Iron": "আয়রন", "Protein": "প্রোটিন", "Calcium": "ক্যালসিয়াম",
            "Folate": "ফোলেট", "Vitamin C": "ভিটামিন সি", "Fiber": "ফাইবার",
            "Potassium": "পটাশিয়াম", "Vitamin A": "ভিটামিন এ", "Vitamin D": "ভিটামিন ডি",
            "Omega-3": "ওমেগা-৩", "Choline": "কোলিন", "Vitamin B6": "ভিটামিন বি৬",
            "DHA": "ডিএইচএ", "Zinc": "জিংক", "Magnesium": "ম্যাগনেসিয়াম"
        }
        
        nutrient_text = " ও ".join([nutrient_bengali.get(n, n) for n in nutrients])
        
        # Add condition-specific benefit
        benefit_msg = ""
        for condition in profile.conditions:
            if condition == "anemia" and "Iron" in nutrients:
                benefit_msg = " এটা আপনার রক্তস্বল্পতার জন্য খুব ভালো!"
                break
            elif condition == "gestational_diabetes" and "Fiber" in nutrients:
                benefit_msg = " ফাইবার থাকায় সুগার কন্ট্রোলে সাহায্য করবে!"
                break
            elif condition == "hypertension" and "Potassium" in nutrients:
                benefit_msg = " পটাশিয়াম থাকায় রক্তচাপ নিয়ন্ত্রণে সাহায্য করবে!"
                break
        
        # Bengali cooking tips
        tips_bengali = []
        for tip in found_food.get("cooking_tips", []):
            # Keep tips or translate common ones
            if "cook" in tip.lower():
                tips_bengali.append("ভালো করে রান্না করে খাবেন")
            elif "lemon" in tip.lower() or "iron" in tip.lower():
                tips_bengali.append("লেবু দিয়ে খেলে আয়রন ভালো শোষণ হবে")
            elif "boil" in tip.lower():
                tips_bengali.append("ফুটিয়ে খাবেন")
            else:
                tips_bengali.append(tip)
        
        return FoodCheckResponse(
            food_name=found_food["name_bengali"],
            is_safe=True,
            safety_level="safe",
            reason=f"{found_food['name_bengali']} খেতে পারেন! এতে {nutrient_text} আছে।{benefit_msg}",
            alternative=None,
            tips=tips_bengali if tips_bengali else ["পরিমিত পরিমাণে খান"]
        )
    
    def get_conversational_response(self, food_name: str, profile: PatientProfile) -> dict:
        """
        Generate a simple conversational response about food safety.
        Returns Bengali-friendly response for pregnant mothers.
        """
        food_name_lower = food_name.lower()
        
        # Bengali food name mapping
        bengali_names = {
            "spinach": "পালং শাক", "palong": "পালং শাক",
            "egg": "ডিম", "dim": "ডিম", "eggs": "ডিম",
            "fish": "মাছ", "mach": "মাছ",
            "lentil": "ডাল", "dal": "ডাল", "lentils": "ডাল",
            "banana": "কলা", "kola": "কলা",
            "milk": "দুধ", "dudh": "দুধ",
            "orange": "কমলা", "komola": "কমলা",
            "rice": "ভাত", "bhat": "ভাত",
            "papaya": "পেঁপে", "pepe": "পেঁপে",
            "mango": "আম", "aam": "আম",
            "apple": "আপেল", "chicken": "মুরগি", "murgi": "মুরগি",
            "beef": "গরুর মাংস", "mutton": "খাসির মাংস",
            "potato": "আলু", "alu": "আলু",
            "tomato": "টমেটো", "carrot": "গাজর",
            "cucumber": "শসা", "shasha": "শসা",
            "yogurt": "দই", "doi": "দই", "curd": "দই"
        }
        
        # Get Bengali name
        food_bengali = None
        for key, bengali in bengali_names.items():
            if key in food_name_lower:
                food_bengali = bengali
                break
        
        # Find food in database
        found_food = None
        for food in self.food_database:
            if food_name_lower in food["name_english"].lower() or food_name_lower in food["name_bengali"].lower():
                found_food = food
                food_bengali = food["name_bengali"]
                break
        
        # Check for dangerous foods first
        dangerous_foods = ["papaya", "pepe", "raw", "kacha", "alcohol", "wine", "beer"]
        for danger in dangerous_foods:
            if danger in food_name_lower:
                return {
                    "is_safe": False,
                    "verdict": "❌ এটা এড়িয়ে চলুন",
                    "message": f"গর্ভাবস্থায় {food_bengali or food_name} খাওয়া ঠিক নয়। এটা বাচ্চার ক্ষতি করতে পারে।",
                    "tip": "ডাক্তারের পরামর্শ নিন",
                    "alternative": "পাকা পেঁপে অল্প খেতে পারেন" if "papaya" in food_name_lower else None,
                    "food_name": food_name,
                    "food_name_bengali": food_bengali
                }
        
        # Check patient conditions
        if found_food:
            for condition in profile.conditions:
                if condition in found_food.get("avoid_for", []):
                    # Find alternative
                    alt_bengali = None
                    for alt_food in self.food_database:
                        if condition in alt_food["good_for"]:
                            alt_bengali = alt_food["name_bengali"]
                            break
                    
                    condition_bengali = {
                        "gestational_diabetes": "ডায়াবেটিস",
                        "anemia": "রক্তস্বল্পতা",
                        "hypertension": "উচ্চ রক্তচাপ"
                    }.get(condition, condition)
                    
                    return {
                        "is_safe": False,
                        "verdict": "⚠️ সাবধান",
                        "message": f"আপনার {condition_bengali} আছে, তাই {food_bengali or food_name} কম খাওয়া ভালো।",
                        "tip": found_food["cooking_tips"][0] if found_food.get("cooking_tips") else None,
                        "alternative": f"এর বদলে {alt_bengali} খান" if alt_bengali else None,
                        "food_name": food_name,
                        "food_name_bengali": food_bengali
                    }
        
        # Check allergies
        for allergy in profile.allergies:
            if allergy.lower() in food_name_lower:
                return {
                    "is_safe": False,
                    "verdict": "❌ এটা খাবেন না",
                    "message": f"আপনার {allergy} এলার্জি আছে। এটা এড়িয়ে চলুন।",
                    "tip": None,
                    "alternative": None,
                    "food_name": food_name,
                    "food_name_bengali": food_bengali
                }
        
        # Food is safe - generate positive response
        if found_food:
            nutrients = found_food["nutrients"][:2]
            nutrient_bengali = {
                "Iron": "আয়রন", "Protein": "প্রোটিন", "Calcium": "ক্যালসিয়াম",
                "Folate": "ফোলেট", "Vitamin C": "ভিটামিন সি", "Fiber": "ফাইবার",
                "Potassium": "পটাশিয়াম", "Vitamin A": "ভিটামিন এ"
            }
            
            nutrient_text = " ও ".join([nutrient_bengali.get(n, n) for n in nutrients])
            
            # Condition-specific benefits
            benefit_msg = ""
            if "anemia" in profile.conditions and "Iron" in nutrients:
                benefit_msg = " এটা আপনার রক্তস্বল্পতার জন্য খুব ভালো!"
            elif "gestational_diabetes" in profile.conditions and "Fiber" in nutrients:
                benefit_msg = " ফাইবার থাকায় সুগার কন্ট্রোলে সাহায্য করবে!"
            
            tip = found_food["cooking_tips"][0] if found_food.get("cooking_tips") else None
            
            return {
                "is_safe": True,
                "verdict": "✅ হ্যাঁ, খেতে পারেন!",
                "message": f"{food_bengali or food_name} খেতে পারেন। এতে {nutrient_text} আছে।{benefit_msg}",
                "tip": tip,
                "alternative": None,
                "food_name": food_name,
                "food_name_bengali": food_bengali
            }
        
        # Unknown food - general safe response
        return {
            "is_safe": True,
            "verdict": "✅ সম্ভবত নিরাপদ",
            "message": f"{food_bengali or food_name} সাধারণত গর্ভাবস্থায় খাওয়া যায়। তবে পরিমিত খান।",
            "tip": "ভালো করে রান্না করে খাবেন",
            "alternative": None,
            "food_name": food_name,
            "food_name_bengali": food_bengali
        }
    
    async def _analyze_unknown_food_with_ai(self, food_name: str, profile: PatientProfile) -> FoodCheckResponse:
        """
        Use AI to analyze foods not in our database.
        Provides intelligent recommendations based on general nutritional knowledge.
        """
        # Build condition context
        conditions_text = ", ".join(profile.conditions) if profile.conditions else "none"
        allergies_text = ", ".join(profile.allergies) if profile.allergies else "none"
        
        prompt = f"""You are a maternal health nutrition expert. A pregnant woman in her {profile.trimester} trimester is asking if she can eat "{food_name}".

Her health conditions: {conditions_text}
Her allergies: {allergies_text}

Analyze this food for pregnancy safety. Respond in this EXACT JSON format only, no other text:
{{
    "is_safe": true/false,
    "safety_level": "safe" or "caution" or "avoid",
    "reason_bengali": "Bengali explanation in 1-2 sentences",
    "tip_bengali": "One practical tip in Bengali",
    "alternative_bengali": "Better alternative food name in Bengali if not safe, or null"
}}

Consider:
- Raw/undercooked risks
- High mercury fish
- Unpasteurized dairy
- Excess caffeine/sugar
- Processed foods
- Her specific conditions (diabetes=avoid sugar, anemia=need iron, hypertension=avoid salt)

Be helpful but cautious. If truly unsafe, say so clearly."""

        try:
            ai_response = await self.ai_service.get_response(
                message=prompt,
                conversation_history=[],
                is_emergency=False,
                user_context=None
            )
            
            # Parse AI response
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{[^{}]*\}', ai_response, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                
                return FoodCheckResponse(
                    food_name=food_name,
                    is_safe=result.get("is_safe", True),
                    safety_level=result.get("safety_level", "caution"),
                    reason=result.get("reason_bengali", f"{food_name} সম্পর্কে সতর্ক থাকুন।"),
                    alternative=result.get("alternative_bengali"),
                    tips=[result.get("tip_bengali", "পরিমিত পরিমাণে খান")]
                )
            else:
                # AI didn't return proper JSON, use fallback
                return self._get_smart_fallback_response(food_name, profile)
                
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._get_smart_fallback_response(food_name, profile)
    
    def _get_smart_fallback_response(self, food_name: str, profile: PatientProfile) -> FoodCheckResponse:
        """
        Smart fallback when AI is unavailable.
        Uses pattern matching for common food categories.
        """
        food_lower = food_name.lower()
        
        # Dangerous food patterns
        dangerous_patterns = {
            "raw": ("❌ কাঁচা খাবার গর্ভাবস্থায় এড়িয়ে চলুন।", False, "avoid"),
            "sushi": ("❌ কাঁচা মাছ গর্ভাবস্থায় নিরাপদ নয়।", False, "avoid"),
            "alcohol": ("❌ মদ গর্ভাবস্থায় সম্পূর্ণ নিষিদ্ধ।", False, "avoid"),
            "wine": ("❌ মদ গর্ভাবস্থায় সম্পূর্ণ নিষিদ্ধ।", False, "avoid"),
            "beer": ("❌ মদ গর্ভাবস্থায় সম্পূর্ণ নিষিদ্ধ।", False, "avoid"),
            "smoking": ("❌ ধূমপান গর্ভাবস্থায় সম্পূর্ণ নিষিদ্ধ।", False, "avoid"),
        }
        
        for pattern, (reason, is_safe, level) in dangerous_patterns.items():
            if pattern in food_lower:
                return FoodCheckResponse(
                    food_name=food_name,
                    is_safe=is_safe,
                    safety_level=level,
                    reason=reason,
                    alternative=None,
                    tips=["ডাক্তারের পরামর্শ নিন"]
                )
        
        # Processed/junk food patterns - caution
        caution_patterns = ["pizza", "পিজা", "burger", "বার্গার", "chips", "চিপস", 
                          "cake", "কেক", "ice cream", "আইসক্রিম", "chocolate", "চকলেট",
                          "soft drink", "কোলা", "cola", "pepsi", "sprite", "fanta",
                          "noodles", "নুডলস", "maggi", "ম্যাগি", "fried", "ভাজা",
                          "fast food", "ফাস্ট ফুড", "junk", "বিরিয়ানি", "biryani"]
        
        for pattern in caution_patterns:
            if pattern in food_lower:
                # Check for diabetes
                if "gestational_diabetes" in profile.conditions or "diabetes" in profile.conditions:
                    return FoodCheckResponse(
                        food_name=food_name,
                        is_safe=False,
                        safety_level="avoid",
                        reason=f"আপনার ডায়াবেটিস আছে। {food_name} এ চিনি ও কার্বস বেশি, এড়িয়ে চলুন।",
                        alternative="ঘরে তৈরি স্বাস্থ্যকর খাবার",
                        tips=["ঘরে তৈরি খাবার খান", "প্রসেসড ফুড এড়িয়ে চলুন"]
                    )
                # Check for hypertension
                if "hypertension" in profile.conditions:
                    return FoodCheckResponse(
                        food_name=food_name,
                        is_safe=False,
                        safety_level="caution",
                        reason=f"{food_name} এ লবণ বেশি থাকতে পারে। আপনার উচ্চ রক্তচাপের জন্য কম খান।",
                        alternative="কম লবণযুক্ত ঘরের খাবার",
                        tips=["লবণ কম খান", "প্রসেসড ফুড এড়িয়ে চলুন"]
                    )
                
                return FoodCheckResponse(
                    food_name=food_name,
                    is_safe=True,
                    safety_level="caution",
                    reason=f"{food_name} মাঝে মাঝে খেতে পারেন, তবে নিয়মিত নয়। ঘরের খাবার বেশি ভালো।",
                    alternative="ঘরে তৈরি স্বাস্থ্যকর খাবার",
                    tips=["মাঝে মাঝে অল্প পরিমাণে খেতে পারেন", "নিয়মিত খাবেন না"]
                )
        
        # Default - cautiously safe
        return FoodCheckResponse(
            food_name=food_name,
            is_safe=True,
            safety_level="caution",
            reason=f"{food_name} সাধারণত খাওয়া যায়। তবে পরিমিত পরিমাণে খান এবং তাজা/ভালো করে রান্না করা নিশ্চিত করুন।",
            alternative=None,
            tips=["পরিমিত পরিমাণে খান", "তাজা ও পরিষ্কার খাবার খান"]
        )

# Global instance
recommendation_service = FoodRecommendationService()
