"""
Digital Midwife - Weekly Care Plan Generator
Based on WHO Antenatal Care Recommendations (2016/2022)
"""
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta

from models.care_models import (
    WeeklyCarePlan, WeeklyCheckItem, NutritionGuideline,
    ExerciseRecommendation, WarningSign, MaternalRiskProfile,
    Trimester, RiskLevel
)


class WeeklyCarePlanService:
    """
    Generates personalized weekly care plans based on:
    - WHO Antenatal Care Guidelines
    - Patient's trimester and week
    - Risk profile (age, BMI, conditions)
    - Local context (Bangladesh)
    """
    
    def __init__(self):
        # WHO recommended ANC schedule (minimum 8 contacts)
        self.anc_schedule = {
            12: "১ম ANC ভিজিট",
            20: "২য় ANC ভিজিট", 
            26: "৩য় ANC ভিজিট",
            30: "৪র্থ ANC ভিজিট",
            34: "৫ম ANC ভিজিট",
            36: "৬ষ্ঠ ANC ভিজিট",
            38: "৭ম ANC ভিজিট",
            40: "৮ম ANC ভিজিট"
        }
        
        # Load WHO-based data
        self._load_weekly_development_data()
        self._load_nutrition_guidelines()
        self._load_warning_signs()
        self._load_exercise_guidelines()
    
    def _load_weekly_development_data(self):
        """Baby development and mother changes by week"""
        self.weekly_development = {
            # First Trimester
            4: {
                "baby": "ভ্রূণ এখন পোস্তদানার মতো ছোট। হৃদপিণ্ড তৈরি শুরু হয়েছে।",
                "mother": "পিরিয়ড মিস হয়েছে। হালকা ক্লান্তি ও বমি বমি ভাব হতে পারে।",
                "size": "পোস্তদানা"
            },
            8: {
                "baby": "বাচ্চা এখন রাস্পবেরির মতো। হাত-পা তৈরি হচ্ছে।",
                "mother": "সকালে বমি ভাব বেশি। স্তন ভারী লাগতে পারে।",
                "size": "রাস্পবেরি"
            },
            12: {
                "baby": "বাচ্চা এখন লেবুর মতো। সব অঙ্গ তৈরি হয়ে গেছে।",
                "mother": "বমি ভাব কমতে শুরু করবে। শক্তি ফিরে আসবে।",
                "size": "লেবু"
            },
            # Second Trimester
            16: {
                "baby": "বাচ্চা এখন আপেলের মতো। নড়াচড়া শুরু করেছে।",
                "mother": "পেট দেখা যাচ্ছে। শিশুর নড়াচড়া অনুভব হতে পারে।",
                "size": "আপেল"
            },
            20: {
                "baby": "বাচ্চা এখন কলার মতো। লিঙ্গ নির্ধারণ সম্ভব।",
                "mother": "নিয়মিত নড়াচড়া অনুভব হচ্ছে। পিঠে ব্যথা হতে পারে।",
                "size": "কলা"
            },
            24: {
                "baby": "বাচ্চা এখন ভুট্টার মতো। শ্রবণশক্তি তৈরি হয়েছে।",
                "mother": "পেট বড় হচ্ছে। পায়ে পানি জমতে পারে।",
                "size": "ভুট্টা"
            },
            # Third Trimester
            28: {
                "baby": "বাচ্চা এখন বেগুনের মতো। চোখ খুলতে পারছে।",
                "mother": "শ্বাসকষ্ট হতে পারে। ঘন ঘন প্রস্রাব।",
                "size": "বেগুন"
            },
            32: {
                "baby": "বাচ্চা এখন নারকেলের মতো। মাথা নিচে নামছে।",
                "mother": "পেট অনেক বড়। ঘুমাতে অসুবিধা হতে পারে।",
                "size": "নারকেল"
            },
            36: {
                "baby": "বাচ্চা এখন পেঁপের মতো। ফুসফুস প্রায় পূর্ণ।",
                "mother": "ব্র্যাক্সটন হিক্স সংকোচন হতে পারে।",
                "size": "পেঁপে"
            },
            40: {
                "baby": "বাচ্চা তরমুজের মতো বড়। জন্মের জন্য প্রস্তুত!",
                "mother": "প্রসব যেকোনো সময় হতে পারে। লক্ষণ দেখুন।",
                "size": "তরমুজ"
            }
        }
    
    def _load_nutrition_guidelines(self):
        """WHO nutrition guidelines for pregnancy"""
        self.nutrition_by_trimester = {
            Trimester.FIRST: {
                "focus": ["ফলিক এসিড", "আয়রন", "প্রোটিন"],
                "calories_extra": 0,  # No extra in first trimester
                "guidelines": [
                    NutritionGuideline(
                        nutrient="ফলিক এসিড",
                        daily_requirement=400,
                        unit="mcg",
                        food_sources_bengali=["পালং শাক", "ডাল", "কলিজা", "ডিম"],
                        importance_bengali="বাচ্চার মস্তিষ্ক ও মেরুদণ্ড সঠিকভাবে তৈরি হওয়ার জন্য",
                        deficiency_risk="নিউরাল টিউব ডিফেক্ট হতে পারে"
                    ),
                    NutritionGuideline(
                        nutrient="আয়রন",
                        daily_requirement=27,
                        unit="mg",
                        food_sources_bengali=["কচু শাক", "মাংস", "ডিম", "কলিজা", "খেজুর"],
                        importance_bengali="রক্তস্বল্পতা প্রতিরোধে",
                        deficiency_risk="রক্তস্বল্পতা, দুর্বলতা, কম ওজনের বাচ্চা"
                    )
                ]
            },
            Trimester.SECOND: {
                "focus": ["আয়রন", "ক্যালসিয়াম", "প্রোটিন", "ওমেগা-৩"],
                "calories_extra": 340,
                "guidelines": [
                    NutritionGuideline(
                        nutrient="ক্যালসিয়াম",
                        daily_requirement=1000,
                        unit="mg",
                        food_sources_bengali=["দুধ", "দই", "ছোট মাছ", "সজনে পাতা"],
                        importance_bengali="বাচ্চার হাড় ও দাঁত তৈরিতে",
                        deficiency_risk="মায়ের হাড় দুর্বল, বাচ্চার হাড় গঠনে সমস্যা"
                    ),
                    NutritionGuideline(
                        nutrient="প্রোটিন",
                        daily_requirement=71,
                        unit="g",
                        food_sources_bengali=["মাছ", "মাংস", "ডিম", "ডাল", "দুধ"],
                        importance_bengali="বাচ্চার শরীর গঠনে",
                        deficiency_risk="বাচ্চার বৃদ্ধি কম হতে পারে"
                    )
                ]
            },
            Trimester.THIRD: {
                "focus": ["আয়রন", "প্রোটিন", "ভিটামিন K", "ফাইবার"],
                "calories_extra": 450,
                "guidelines": [
                    NutritionGuideline(
                        nutrient="আয়রন",
                        daily_requirement=27,
                        unit="mg",
                        food_sources_bengali=["কচু শাক", "মাংস", "কলিজা", "খেজুর"],
                        importance_bengali="প্রসবের সময় রক্তক্ষরণ সামলাতে",
                        deficiency_risk="প্রসবে জটিলতা, অতিরিক্ত রক্তক্ষরণ"
                    ),
                    NutritionGuideline(
                        nutrient="ফাইবার",
                        daily_requirement=28,
                        unit="g",
                        food_sources_bengali=["শাকসবজি", "ফল", "লাল আটা", "ওটস"],
                        importance_bengali="কোষ্ঠকাঠিন্য প্রতিরোধে",
                        deficiency_risk="কোষ্ঠকাঠিন্য, পাইলস"
                    )
                ]
            }
        }
    
    def _load_warning_signs(self):
        """WHO danger signs in pregnancy"""
        self.warning_signs = {
            "always": [  # All trimesters
                WarningSign(
                    sign_bengali="যোনি থেকে রক্তপাত",
                    sign_english="Vaginal bleeding",
                    severity="severe",
                    action_required_bengali="সাথে সাথে হাসপাতালে যান",
                    is_emergency=True
                ),
                WarningSign(
                    sign_bengali="তীব্র মাথাব্যথা যা যাচ্ছে না",
                    sign_english="Severe persistent headache",
                    severity="severe",
                    action_required_bengali="রক্তচাপ মাপুন, ডাক্তার দেখান",
                    is_emergency=True
                ),
                WarningSign(
                    sign_bengali="চোখে ঝাপসা দেখা",
                    sign_english="Blurred vision",
                    severity="severe",
                    action_required_bengali="এটি প্রি-এক্লাম্পসিয়ার লক্ষণ। এখনই ডাক্তার দেখান",
                    is_emergency=True
                ),
                WarningSign(
                    sign_bengali="তীব্র পেটব্যথা",
                    sign_english="Severe abdominal pain",
                    severity="severe",
                    action_required_bengali="সাথে সাথে হাসপাতালে যান",
                    is_emergency=True
                ),
                WarningSign(
                    sign_bengali="জ্বর (১০০.৪°F এর বেশি)",
                    sign_english="High fever",
                    severity="moderate",
                    action_required_bengali="ডাক্তার দেখান। সংক্রমণ হতে পারে",
                    is_emergency=False
                ),
                WarningSign(
                    sign_bengali="প্রস্রাবে জ্বালাপোড়া",
                    sign_english="Burning urination",
                    severity="moderate",
                    action_required_bengali="UTI হতে পারে। ডাক্তার দেখান",
                    is_emergency=False
                )
            ],
            Trimester.THIRD: [
                WarningSign(
                    sign_bengali="পানি ভাঙা (জল আসা)",
                    sign_english="Water breaking",
                    severity="severe",
                    action_required_bengali="হাসপাতালে যান। প্রসব শুরু হতে পারে",
                    is_emergency=True
                ),
                WarningSign(
                    sign_bengali="বাচ্চার নড়াচড়া কমে যাওয়া",
                    sign_english="Reduced fetal movement",
                    severity="severe",
                    action_required_bengali="শুয়ে ১০টা নড়াচড়া গুনুন। কম হলে হাসপাতালে যান",
                    is_emergency=True
                ),
                WarningSign(
                    sign_bengali="নিয়মিত সংকোচন (৩৭ সপ্তাহের আগে)",
                    sign_english="Regular contractions before 37 weeks",
                    severity="severe",
                    action_required_bengali="প্রিম্যাচিউর প্রসবের লক্ষণ। হাসপাতালে যান",
                    is_emergency=True
                ),
                WarningSign(
                    sign_bengali="মুখ, হাত বা পায়ে ফুলে যাওয়া",
                    sign_english="Swelling of face/hands",
                    severity="moderate",
                    action_required_bengali="প্রি-এক্লাম্পসিয়ার লক্ষণ। রক্তচাপ মাপুন",
                    is_emergency=False
                )
            ]
        }
    
    def _load_exercise_guidelines(self):
        """Safe exercises by trimester"""
        self.exercises = {
            Trimester.FIRST: [
                ExerciseRecommendation(
                    exercise_bengali="হাঁটা",
                    exercise_english="Walking",
                    duration_minutes=30,
                    frequency_per_week=5,
                    benefits_bengali="রক্ত চলাচল ভালো হয়, মন ভালো থাকে",
                    precautions_bengali=["আরামদায়ক জুতা পরুন", "গরমে বেশিক্ষণ হাঁটবেন না"],
                    contraindications=["threatened_miscarriage", "heavy_bleeding"]
                ),
                ExerciseRecommendation(
                    exercise_bengali="হালকা স্ট্রেচিং",
                    exercise_english="Light stretching",
                    duration_minutes=15,
                    frequency_per_week=7,
                    benefits_bengali="শরীর নমনীয় থাকে, ব্যথা কম হয়",
                    precautions_bengali=["হঠাৎ করে ঝুঁকবেন না"],
                    contraindications=[]
                )
            ],
            Trimester.SECOND: [
                ExerciseRecommendation(
                    exercise_bengali="হাঁটা",
                    exercise_english="Walking",
                    duration_minutes=30,
                    frequency_per_week=5,
                    benefits_bengali="ওজন নিয়ন্ত্রণে থাকে, শক্তি বাড়ে",
                    precautions_bengali=["সমতল জায়গায় হাঁটুন"],
                    contraindications=["preterm_labor_risk"]
                ),
                ExerciseRecommendation(
                    exercise_bengali="সাঁতার",
                    exercise_english="Swimming",
                    duration_minutes=30,
                    frequency_per_week=3,
                    benefits_bengali="জয়েন্টে চাপ কম, পুরো শরীরের ব্যায়াম",
                    precautions_bengali=["পরিষ্কার পানিতে সাঁতার কাটুন"],
                    contraindications=["infection", "rom"]
                ),
                ExerciseRecommendation(
                    exercise_bengali="প্রেগনেন্সি যোগা",
                    exercise_english="Prenatal yoga",
                    duration_minutes=30,
                    frequency_per_week=3,
                    benefits_bengali="শ্বাস-প্রশ্বাস ভালো হয়, মানসিক শান্তি",
                    precautions_bengali=["চিত হয়ে শুয়ে ব্যায়াম করবেন না", "পেটে চাপ দেবেন না"],
                    contraindications=[]
                )
            ],
            Trimester.THIRD: [
                ExerciseRecommendation(
                    exercise_bengali="হালকা হাঁটা",
                    exercise_english="Light walking",
                    duration_minutes=20,
                    frequency_per_week=5,
                    benefits_bengali="প্রসবের জন্য শরীর প্রস্তুত হয়",
                    precautions_bengali=["ধীরে হাঁটুন", "কাছে থাকুন", "বিশ্রাম নিন"],
                    contraindications=["preterm_labor", "placenta_previa"]
                ),
                ExerciseRecommendation(
                    exercise_bengali="কেগেল ব্যায়াম",
                    exercise_english="Kegel exercises",
                    duration_minutes=10,
                    frequency_per_week=7,
                    benefits_bengali="প্রসবে সাহায্য করে, প্রস্রাব ধরে রাখতে সাহায্য করে",
                    precautions_bengali=[],
                    contraindications=[]
                ),
                ExerciseRecommendation(
                    exercise_bengali="শ্বাসের ব্যায়াম",
                    exercise_english="Breathing exercises",
                    duration_minutes=15,
                    frequency_per_week=7,
                    benefits_bengali="প্রসবের সময় কাজে লাগবে",
                    precautions_bengali=[],
                    contraindications=[]
                )
            ]
        }
    
    def _get_week_from_trimester(self, week: int) -> Trimester:
        """Determine trimester from week number"""
        if week <= 12:
            return Trimester.FIRST
        elif week <= 26:
            return Trimester.SECOND
        else:
            return Trimester.THIRD
    
    def _get_closest_development_week(self, week: int) -> int:
        """Get the closest week that has development data"""
        available_weeks = sorted(self.weekly_development.keys())
        for w in available_weeks:
            if w >= week:
                return w
        return available_weeks[-1]
    
    def _adjust_for_risk_profile(self, plan: WeeklyCarePlan, profile: MaternalRiskProfile) -> WeeklyCarePlan:
        """Adjust care plan based on patient's risk factors (Upgraded for P0 Models)"""
        
        # High-risk age adjustments
        if profile.age < 18 or profile.age > 35:
            plan.active_concerns.append("বয়স সংক্রান্ত ঝুঁকি")
            plan.weekly_checklist.append(
                WeeklyCheckItem(
                    item_id="age_risk_check",
                    title_bengali="অতিরিক্ত সতর্কতা",
                    title_english="Extra monitoring",
                    description_bengali="বয়সের কারণে অতিরিক্ত সতর্ক থাকুন। নিয়মিত চেকআপ করান।",
                    category="checkup",
                    priority="high"
                )
            )
        
        # BMI adjustments (Using dynamic property)
        bmi = profile.current_bmi or profile.bmi
        if bmi < 18.5:
            plan.active_concerns.append("কম ওজন")
            plan.nutrition_guidelines.append(
                NutritionGuideline(
                    nutrient="অতিরিক্ত ক্যালোরি",
                    daily_requirement=300,
                    unit="kcal extra",
                    food_sources_bengali=["ঘি", "বাদাম", "কলা", "দুধ"],
                    importance_bengali="ওজন বাড়ানোর জন্য",
                    deficiency_risk="কম ওজনের বাচ্চা হতে পারে"
                )
            )
        elif bmi > 30:
            plan.active_concerns.append("অতিরিক্ত ওজন")
            plan.self_care_tips_bengali.append("মিষ্টি ও ভাজাপোড়া কম খান")
            plan.self_care_tips_bengali.append("ডায়াবেটিস টেস্ট করান (OGTT)")
        
        # Risk level mapping for comparison
        risk_map = {
            RiskLevel.LOW: 1,
            RiskLevel.UNKNOWN: 1,
            RiskLevel.MODERATE: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        current_numeric = risk_map.get(plan.current_risk_level, 1)

        # Anemia check (Direct flag + legacy readings)
        if profile.has_anemia or (profile.hemoglobin_level and profile.hemoglobin_level < 11):
            if "রক্তস্বল্পতা" not in plan.active_concerns:
                plan.active_concerns.append("রক্তস্বল্পতা")
                if risk_map[RiskLevel.MODERATE] > current_numeric:
                    plan.current_risk_level = RiskLevel.MODERATE
                    current_numeric = risk_map[RiskLevel.MODERATE]
                
                plan.foods_to_emphasize.extend(["কচু শাক", "কলিজা", "খেজুর", "ডালিম", "ডিম"])
                plan.weekly_checklist.append(
                    WeeklyCheckItem(
                        item_id="iron_supplement",
                        title_bengali="আয়রন ট্যাবলেট ও ভিটামিন সি",
                        title_english="Iron & Vitamin C",
                        description_bengali="প্রতিদিন আয়রন ট্যাবলেট খান। লেবুর শরবত বা টক ফলের সাথে খেলে আয়রন ভালো শোষণ হয়।",
                        category="medication",
                        priority="high",
                        due_by="daily"
                    )
                )
        
        # Hypertension check (Direct flag + legacy readings)
        if profile.has_hypertension or (profile.blood_pressure_systolic and profile.blood_pressure_systolic >= 140):
            if "উচ্চ রক্তচাপ" not in plan.active_concerns:
                plan.active_concerns.append("উচ্চ রক্তচাপ")
                if risk_map[RiskLevel.HIGH] > current_numeric:
                    plan.current_risk_level = RiskLevel.HIGH
                    current_numeric = risk_map[RiskLevel.HIGH]

                plan.foods_to_avoid.extend(["কাঁচা লবণ", "আচার", "প্যাকেটজাত নোনতা খাবার"])
                plan.warning_signs.append(
                    WarningSign(
                        sign_bengali="মাথাব্যথা বা চোখে ঝাপসা দেখা",
                        sign_english="Headache or blurred vision",
                        severity="severe",
                        action_required_bengali="এখনই হাসপাতালে যান। এটি প্রি-এক্লাম্পসিয়ার লক্ষণ হতে পারে।",
                        is_emergency=True
                    )
                )
        
        # Diabetes check (Direct flag + legacy readings)
        if profile.has_gestational_diabetes or (profile.fasting_blood_sugar and profile.fasting_blood_sugar > 95):
            if "গর্ভকালীন ডায়াবেটিস" not in plan.active_concerns:
                plan.active_concerns.append("গর্ভকালীন ডায়াবেটিস")
                if risk_map[RiskLevel.HIGH] > current_numeric:
                    plan.current_risk_level = RiskLevel.HIGH
                    current_numeric = risk_map[RiskLevel.HIGH]

                plan.foods_to_avoid.extend(["চিনি", "মিষ্টি", "সাদা ভাত", "কোমল পানীয়", "মধু"])
                plan.foods_to_emphasize.extend(["লাল আটা", "সবুজ শাকসবজি", "শসা", "প্রোটিন"])
                plan.weekly_checklist.append(
                    WeeklyCheckItem(
                        item_id="sugar_track",
                        title_bengali="ব্লাড সুগার মাপুন",
                        title_english="Check blood sugar",
                        description_bengali="খালি পেটে এবং খাওয়ার ২ ঘণ্টা পর সুগার চেক করুন।",
                        category="checkup",
                        priority="high",
                        due_by="daily"
                    )
                )
        
        # Structured Medical Conditions (V2)
        for cond in profile.existing_conditions_v2:
            name_lower = cond.condition_name.lower()
            if any(x in name_lower for x in ["thyroid", "থাইরয়েড"]):
                plan.active_concerns.append("থাইরয়েড সমস্যা")
                plan.recommended_tests.append("সকালে খালি পেটে থাইরয়েড ওষুধ খাওয়া")
            
        # Legacy conditions fallback
        for condition in profile.existing_conditions:
            if condition.lower() in ["diabetes", "ডায়াবেটিস"] and "গর্ভকালীন ডায়াবেটিস" not in plan.active_concerns:
                plan.active_concerns.append("ডায়াবেটিস")
                if risk_map[RiskLevel.HIGH] > current_numeric:
                    plan.current_risk_level = RiskLevel.HIGH
                    current_numeric = risk_map[RiskLevel.HIGH]
            if condition.lower() in ["thyroid", "থাইরয়েড"] and "থাইরয়েড সমস্যা" not in plan.active_concerns:
                plan.active_concerns.append("থাইরয়েড সমস্যা")
        
        return plan
    
    def generate_weekly_plan(
        self, 
        profile: MaternalRiskProfile,
        week: Optional[int] = None
    ) -> WeeklyCarePlan:
        """
        Generate a personalized weekly care plan
        """
        current_week = week or profile.current_week
        trimester = self._get_week_from_trimester(current_week)
        
        # Get development data
        dev_week = self._get_closest_development_week(current_week)
        development = self.weekly_development.get(dev_week, self.weekly_development[20])
        
        # Get nutrition guidelines
        nutrition_data = self.nutrition_by_trimester.get(trimester, self.nutrition_by_trimester[Trimester.SECOND])
        
        # Build the care plan
        plan = WeeklyCarePlan(
            user_id=profile.user_id,
            week_number=current_week,
            trimester=trimester,
            
            # Overview
            week_title_bengali=f"সপ্তাহ {current_week}: আপনার ও বাচ্চার যত্ন",
            week_summary_bengali=f"আপনি এখন {current_week} সপ্তাহে আছেন। বাচ্চা এখন {development['size']}-এর মতো।",
            baby_development_bengali=development["baby"],
            mother_changes_bengali=development["mother"],
            
            # Risk
            current_risk_level=profile.overall_risk_level,
            active_concerns=[],
            
            # Nutrition
            nutrition_focus=nutrition_data["focus"],
            nutrition_guidelines=nutrition_data["guidelines"],
            foods_to_emphasize=[],
            foods_to_avoid=["কাঁচা মাছ/মাংস", "অপাস্তুরিত দুধ", "অতিরিক্ত ক্যাফেইন"],
            
            # Exercise
            exercise_recommendations=self.exercises.get(trimester, []),
            exercises_to_avoid=["ভারী জিনিস তোলা", "লাফানো", "পেটে চাপ দেওয়া ব্যায়াম"],
            
            # Medical
            recommended_tests=[],
            medications_reminders=["আয়রন ট্যাবলেট", "ফলিক এসিড", "ক্যালসিয়াম"],
            vaccination_due=[],
            
            # Warning signs
            warning_signs=self.warning_signs.get("always", []),
            
            # Tips
            self_care_tips_bengali=[
                "প্রচুর পানি পান করুন (৮-১০ গ্লাস)",
                "পর্যাপ্ত ঘুমান (৭-৯ ঘণ্টা)",
                "হালকা ব্যায়াম করুন",
                "মানসিক চাপ এড়িয়ে চলুন"
            ],
            partner_support_tips_bengali=[
                "ঘরের কাজে সাহায্য করুন",
                "ডাক্তারের কাছে সাথে যান",
                "তার কথা মনোযোগ দিয়ে শুনুন",
                "প্রশংসা করুন ও উৎসাহ দিন"
            ]
        )
        
        # Add trimester-specific warning signs
        trimester_warnings = self.warning_signs.get(trimester, [])
        plan.warning_signs.extend(trimester_warnings)
        
        # Check for ANC visit
        for anc_week, anc_name in self.anc_schedule.items():
            if current_week <= anc_week < current_week + 2:
                plan.next_anc_visit = f"{anc_name} (সপ্তাহ {anc_week})"
                plan.weekly_checklist.append(
                    WeeklyCheckItem(
                        item_id=f"anc_{anc_week}",
                        title_bengali=anc_name,
                        title_english=f"ANC Visit Week {anc_week}",
                        description_bengali=f"এই সপ্তাহে {anc_name}-এ যাওয়ার সময়। ডাক্তারের অ্যাপয়েন্টমেন্ট নিন।",
                        category="checkup",
                        priority="high",
                        due_by="this week"
                    )
                )
                break
        
        # Add week-specific tests
        if current_week in [11, 12, 13]:
            plan.recommended_tests.append("NT স্ক্যান (ডাউন সিনড্রোম স্ক্রিনিং)")
        if current_week in [18, 19, 20, 21, 22]:
            plan.recommended_tests.append("অ্যানোমালি স্ক্যান (বাচ্চার গঠন দেখা)")
        if current_week in [24, 25, 26, 27, 28]:
            plan.recommended_tests.append("OGTT (গর্ভকালীন ডায়াবেটিস টেস্ট)")
            plan.recommended_tests.append("হিমোগ্লোবিন টেস্ট")
        if current_week >= 36:
            plan.recommended_tests.append("GBS টেস্ট")
            plan.recommended_tests.append("NST (বাচ্চার হার্টবিট মনিটরিং)")
        
        # Add standard checklist items
        # Add standard checklist items - Logic Refined to be less generic
        base_checklist = []
        
        # Medication is always high priority if prescribed
        base_checklist.append(
            WeeklyCheckItem(
                item_id="folic_acid",
                title_bengali="মেডিসিন রুটিন মেনে চলুন",
                title_english="Follow medication routine",
                description_bengali="ডাক্তারের পরামর্শ অনুযায়ী আয়রন/ফলিক এসিড/ক্যালসিয়াম ঠিকমতো খাচ্ছেন তো?",
                category="medication",
                priority="high",
                due_by="daily"
            )
        )

        # Trimester specific advice instead of generic 'rest'
        if trimester == Trimester.FIRST:
             base_checklist.append(
                WeeklyCheckItem(
                    item_id="morning_sickness",
                    title_bengali="বমি ভাব কমানোর উপায়",
                    title_english="Reduce morning sickness",
                    description_bengali="অল্প অল্প করে বারবার খান। আদা চা বা শুকনো খাবার ট্রাই করুন।",
                    category="self_care",
                    priority="medium"
                )
            )
        elif trimester == Trimester.THIRD:
             base_checklist.append(
                WeeklyCheckItem(
                    item_id="movement_count",
                    title_bengali="বাচ্চার নড়াচড়া গুনুন",
                    title_english="Count fetal movement",
                    description_bengali="খাবার পর ১ ঘন্টায় কতবার বাচ্চা নড়ছে খেয়াল করুন।",
                    category="checkup",
                    priority="high",
                    due_by="daily"
                )
            )
        else:
            # Second trimester - generic but important
            base_checklist.append(
                WeeklyCheckItem(
                    item_id="water_intake",
                    title_bengali="পর্যাপ্ত পানি ও তরল",
                    title_english="Hydration",
                    description_bengali="ইউরিন ইনফেকশন এড়াতে প্রচুর পানি, ডাবের পানি বা জুস খান।",
                    category="nutrition",
                    priority="medium"
                )
            )

        plan.weekly_checklist.extend(base_checklist)
        
        # Adjust for patient's specific risk profile
        plan = self._adjust_for_risk_profile(plan, profile)
        
        return plan


# Global instance
care_plan_service = WeeklyCarePlanService()
