"""
Digital Midwife API Router
Core Module APIs: Care Plan, Triage, Emergency Bridge
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
import os
import json

from models.care_models import (
    MaternalRiskProfile, WeeklyCarePlan, TriageResult, TriageRequest,
    GenerateCarePlanRequest, RiskAssessmentRequest, RiskAssessmentResponse,
    EmergencyBridgeRequest, EmergencyBridgeResponse, RiskLevel, Trimester
)
from pydantic import BaseModel
from typing import List
from services.care_plan_service import care_plan_service
from services.triage_service import triage_service
from services.emergency_bridge_service import emergency_bridge_service
from services.document_service import document_service
from services.ai_service import AIService

router = APIRouter(prefix="/api/midwife", tags=["Digital Midwife"])

# Initialize services
ai_service = AIService()

# Persistence configuration
PATIENT_DB_PATH = os.path.join("data", "patient_profiles.json")

def load_patient_profiles():
    """Load patient profiles from local disk"""
    if os.path.exists(PATIENT_DB_PATH):
        try:
            with open(PATIENT_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                profiles = {}
                for uid, p_dict in data.items():
                    try:
                        profiles[uid] = MaternalRiskProfile(**p_dict)
                    except Exception as e:
                        print(f"Error parsing profile for {uid}: {e}")
                return profiles
        except Exception as e:
            print(f"Error loading patient profiles: {e}")
    return {}

def save_patient_profiles():
    """Save patient profiles to local disk"""
    try:
        os.makedirs(os.path.dirname(PATIENT_DB_PATH), exist_ok=True)
        # Handle Pydantic serialization
        data = {}
        for uid, p in patient_profiles.items():
            try:
                # Try Pydantic V2 mode='json'
                data[uid] = p.model_dump(mode='json')
            except AttributeError:
                # Fallback to Pydantic V1
                import json as std_json
                data[uid] = std_json.loads(p.json())
        
        with open(PATIENT_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving patient profiles: {e}")

# In-memory patient profile store (initially loaded from disk)
patient_profiles = load_patient_profiles()

def get_augmented_profile(user_id: str) -> Optional[MaternalRiskProfile]:
    """Fetch profile and augment with document-extracted data if available"""
    profile = patient_profiles.get(user_id)
    
    # Get combined data from document service
    base_dict = profile.dict() if profile else {}
    combined_dict = document_service.get_combined_profile(user_id, base_dict)
    
    if not combined_dict:
        return None
        
    # Create or update profile object
    try:
        if profile:
            # Update existing object
            for key, val in combined_dict.items():
                if not key.startswith("_"):
                    setattr(profile, key, val)
            
            # Auto-calculate week from LMP (P0 Logic)
            calc_week = profile.calculate_week_from_lmp()
            if calc_week:
                profile.current_week = calc_week
                
            return profile
        else:
            # Create new from combined data
            # Ensure user_id is passed to constructor
            if "user_id" not in combined_dict:
                combined_dict["user_id"] = user_id
            new_profile = MaternalRiskProfile(**{k: v for k, v in combined_dict.items() if not k.startswith("_")})
            
            # Auto-calculate week from LMP
            calc_week = new_profile.calculate_week_from_lmp()
            if calc_week:
                new_profile.current_week = calc_week
                
            return new_profile
    except Exception as e:
        print(f"Augmentation error: {e}")
        return profile

def sync_document_data_to_profile(user_id: str):
    """
    Permanently merge document-extracted data into the patient's main profile (Upsert).
    This implements the 'Merge Logic' refinement.
    """
    profile = get_augmented_profile(user_id)
    if profile:
        # Save the combined result back to the main profile store
        patient_profiles[user_id] = profile
        save_patient_profiles()
        return True
    return False


# ==================== PATIENT PROFILE ====================

@router.post("/profile", response_model=dict)
async def create_or_update_profile(profile: MaternalRiskProfile):
    """
    👤 রোগীর প্রোফাইল তৈরি/আপডেট করুন
    
    Create or update maternal health profile for personalized care.
    """
    # Calculate BMI
    height_m = profile.height_cm / 100
    profile.bmi = round(profile.current_weight_kg / (height_m ** 2), 1)
    
    # Determine trimester from week
    if profile.current_week <= 12:
        profile.trimester = Trimester.FIRST
    elif profile.current_week <= 26:
        profile.trimester = Trimester.SECOND
    else:
        profile.trimester = Trimester.THIRD
    
    # Calculate initial risk level
    risk_factors = []
    
    if profile.age < 18:
        risk_factors.append("teenage_pregnancy")
    elif profile.age > 35:
        risk_factors.append("advanced_maternal_age")
    
    if profile.bmi < 18.5:
        risk_factors.append("underweight")
    elif profile.bmi > 30:
        risk_factors.append("obese")
    
    if profile.hemoglobin_level and profile.hemoglobin_level < 11:
        risk_factors.append("anemia")
        profile.active_red_flags.append("anemia")
    
    if profile.blood_pressure_systolic and profile.blood_pressure_systolic >= 140:
        risk_factors.append("hypertension")
        profile.active_red_flags.append("hypertension")
    
    if profile.fasting_blood_sugar and profile.fasting_blood_sugar > 95:
        risk_factors.append("gestational_diabetes")
        profile.active_red_flags.append("gestational_diabetes")
    
    # Determine overall risk
    if len(risk_factors) >= 3 or any(rf in ["hypertension", "gestational_diabetes"] for rf in risk_factors):
        profile.overall_risk_level = RiskLevel.HIGH
    elif len(risk_factors) >= 1:
        profile.overall_risk_level = RiskLevel.MODERATE
    else:
        profile.overall_risk_level = RiskLevel.LOW
    
    # Store profile
    patient_profiles[profile.user_id] = profile
    save_patient_profiles()
    
    return {
        "success": True,
        "message_bengali": "আপনার প্রোফাইল সেভ হয়েছে",
        "profile": profile.dict(),
        "risk_level": profile.overall_risk_level.value,
        "risk_factors": risk_factors
    }


@router.get("/profile/{user_id}", response_model=dict)
async def get_profile(user_id: str):
    """
    👤 রোগীর প্রোফাইল দেখুন
    """
    profile = get_augmented_profile(user_id)
    if not profile:
        return {
            "success": False,
            "message_bengali": "প্রোফাইল পাওয়া যায়নি",
            "profile": None
        }
    
    return {
        "success": True,
        "profile": profile.dict()
    }


# ==================== WEEKLY CARE PLAN ====================

@router.post("/care-plan", response_model=dict)
async def generate_care_plan(request: GenerateCarePlanRequest):
    """
    📅 সাপ্তাহিক কেয়ার প্ল্যান তৈরি করুন
    
    Generates personalized weekly care plan based on:
    - WHO Antenatal Care Guidelines
    - Patient's trimester and week
    - Risk profile (age, BMI, conditions)
    """
    profile = get_augmented_profile(request.user_id)
    
    if not profile:
        # Create default profile
        profile = MaternalRiskProfile(
            user_id=request.user_id,
            current_week=request.week_number or 20
        )
    
    week = request.week_number or profile.current_week
    
    # Generate care plan
    care_plan = care_plan_service.generate_weekly_plan(profile, week)
    
    care_plan_dict = care_plan.dict()
    
    # Expose nutrition focus directly (v2 sync)
    care_plan_dict["nutrition_focus"] = care_plan.nutrition_focus
    
    return {
        "success": True,
        "message_bengali": f"সপ্তাহ {week} এর কেয়ার প্ল্যান তৈরি হয়েছে",
        "care_plan": care_plan_dict
    }


@router.get("/care-plan/{user_id}/week/{week_number}", response_model=dict)
async def get_care_plan_for_week(user_id: str, week_number: int):
    """
    📅 নির্দিষ্ট সপ্তাহের কেয়ার প্ল্যান দেখুন
    """
    if week_number < 1 or week_number > 42:
        raise HTTPException(status_code=400, detail="Week must be between 1 and 42")
    
    profile = get_augmented_profile(user_id)
    if not profile:
        profile = MaternalRiskProfile(user_id=user_id, current_week=week_number)
    
    care_plan = care_plan_service.generate_weekly_plan(profile, week_number)
    
    return {
        "success": True,
        "care_plan": care_plan.dict()
    }


# ==================== VOICE TRIAGE ====================

@router.post("/triage", response_model=dict)
async def voice_triage(request: TriageRequest):
    """
    🎤 ভয়েস ট্রায়াজ - লক্ষণ বিশ্লেষণ
    
    Voice-first symptom triage that:
    - Supports Bangla regional dialects (Standard, Sylheti, Chittagonian)
    - Uses deterministic decision tree for red flag detection
    - Cross-references with patient history
    - Returns immediate action guidance
    
    Example inputs:
    - "আমার মাথা ব্যথা করছে"
    - "বাচ্চা নড়ছে না"
    - "রক্তপাত হচ্ছে"
    """
    profile = get_augmented_profile(request.user_id) if request.include_history else None
    
    input_text = request.input_text
    
    # TRANSLATION LAYER: Convert local dialect to English for better understanding
    # Only translate if text contains Bengali characters
    if any('\u0980' <= c <= '\u09ff' for c in input_text):
        translated_text = await ai_service.translate_to_english(input_text)
        print(f"TRIAGE TRANSLATION: {input_text} -> {translated_text}")
        # We append the translation to help the triage service (it handles English too)
        # But we keep original text for context if needed
        input_text = f"{input_text} ({translated_text})"
    
    result = await triage_service.process_symptom_report(
        user_id=request.user_id,
        input_text=input_text,
        patient_profile=profile,
        include_history=request.include_history
    )
    
    # NEW: Add significant triage concern to memories for AI context
    if profile and result.risk_level != RiskLevel.LOW:
        profile.recent_memories.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "context": f"ট্রায়াজে ধরা পড়েছে: {result.primary_concern_bengali}",
            "resolved": False
        })
        if len(profile.recent_memories) > 5:
            profile.recent_memories.pop(0)

    # Check if emergency bridge should be triggered
    if result.should_trigger_emergency:
        # Auto-trigger emergency bridge
        bridge_request = EmergencyBridgeRequest(
            user_id=request.user_id,
            trigger_source="voice_triage",
            detected_emergency=result.primary_concern,
            red_flags=result.detected_red_flags,
            patient_location=request.patient_location
        )
        bridge_response = await emergency_bridge_service.activate_emergency_bridge(bridge_request)
        
        return {
            "success": True,
            "triage_result": result.dict(),
            "emergency_activated": True,
            "emergency_bridge": bridge_response.dict()
        }
    
    # HYBRID MODEL: If deterministic result is LOW risk and generic/unclear, fallback to AI
    is_generic = result.primary_concern in ["Health concern", "কোনো নির্দিষ্ট লক্ষণ বোঝা যায়নি"]
    if result.risk_level == RiskLevel.LOW and is_generic:
        # Get AI response using the Apu persona logic
        ai_response = await ai_service.get_response(
            message=request.input_text,
            is_emergency=False,
            user_context={
                "current_week": profile.current_week if profile else 20,
                "blood_pressure": f"{profile.blood_pressure_systolic}/{profile.blood_pressure_diastolic}" if profile and profile.blood_pressure_systolic else "স্বাভাবিক",
                "recent_memories": profile.recent_memories if profile else []
            }
        )
        
        # Override deterministic response with AI empathy
        result.response_audio_text = ai_response
        result.immediate_action_bengali = ai_response # Display AI response as primary action
        
        # Save memory if emotional/medical concern detected
        if profile:
            await ai_service.extract_and_save_memory(request.user_id, request.input_text, profile)

    return {
        "success": True,
        "triage_result": result.dict(),
        "emergency_activated": False
    }


@router.post("/triage/quick", response_model=dict)
async def quick_symptom_check(symptom_text: str, user_id: str = "anonymous"):
    """
    ⚡ দ্রুত লক্ষণ চেক
    
    Quick symptom check without full profile.
    For rapid triage decisions.
    """
    result = await triage_service.process_symptom_report(
        user_id=user_id,
        input_text=symptom_text,
        patient_profile=None,
        include_history=False
    )
    
    return {
        "risk_level": result.risk_level.value,
        "concern_bengali": result.primary_concern_bengali,
        "action_bengali": result.immediate_action_bengali,
        "is_emergency": result.should_trigger_emergency,
        "voice_response": result.response_audio_text
    }


# ==================== EMERGENCY BRIDGE ====================

@router.post("/emergency/activate", response_model=dict)
async def activate_emergency(request: EmergencyBridgeRequest):
    """
    🚨 জরুরি সেবা সক্রিয় করুন
    
    Activates emergency bridge for critical situations:
    - Provides step-by-step emergency guidance
    - Connects to nearest hospital
    - Prepares AR guidance data
    """
    response = await emergency_bridge_service.activate_emergency_bridge(request)
    
    return {
        "success": True,
        "message_bengali": "জরুরি সেবা সক্রিয় হয়েছে",
        "emergency": response.dict()
    }


@router.get("/emergency/guidance/{guidance_type}", response_model=dict)
async def get_ar_guidance(guidance_type: str):
    """
    📱 AR গাইডেন্স ডেটা
    
    Get AR overlay data for MediaPipe integration.
    Types: hemorrhage_first_aid, eclampsia_position, breathing_exercise_1, etc.
    """
    ar_data = emergency_bridge_service.get_ar_guidance_data(guidance_type)
    
    if not ar_data:
        raise HTTPException(status_code=404, detail="Guidance type not found")
    
    return {
        "success": True,
        "guidance_type": guidance_type,
        "ar_data": ar_data
    }


@router.get("/emergency/labor/{stage}", response_model=dict)
async def get_labor_guidance(stage: str):
    """
    🤰 প্রসবকালীন গাইডেন্স
    
    Get guidance for labor stages: early_labor, active_labor, pushing
    """
    guidance = emergency_bridge_service.get_labor_stage_guidance(stage)
    
    if not guidance:
        raise HTTPException(status_code=404, detail="Labor stage not found")
    
    return {
        "success": True,
        "stage": stage,
        "guidance": guidance
    }


# ==================== RISK ASSESSMENT ====================

@router.post("/risk-assessment", response_model=dict)
async def assess_risk(request: RiskAssessmentRequest):
    """
    📊 ঝুঁকি মূল্যায়ন
    
    Comprehensive risk assessment based on:
    - Age and BMI
    - Blood pressure
    - Hemoglobin level
    - Blood sugar
    - Medical history
    """
    profile = patient_profiles.get(request.user_id)
    
    if not profile:
        return {
            "success": False,
            "message_bengali": "প্রথমে প্রোফাইল তৈরি করুন"
        }
    
    # Update vitals if provided
    if request.vitals:
        if "blood_pressure_systolic" in request.vitals:
            profile.blood_pressure_systolic = request.vitals["blood_pressure_systolic"]
        if "blood_pressure_diastolic" in request.vitals:
            profile.blood_pressure_diastolic = request.vitals["blood_pressure_diastolic"]
        if "hemoglobin" in request.vitals:
            profile.hemoglobin_level = request.vitals["hemoglobin"]
        if "blood_sugar" in request.vitals:
            profile.fasting_blood_sugar = request.vitals["blood_sugar"]
    
    # Recalculate risk
    risk_factors = []
    recommendations = []
    
    # Age risk
    if profile.age < 18:
        risk_factors.append({"factor": "teenage_pregnancy", "severity": "moderate", "bn": "কম বয়সে গর্ভধারণ"})
        recommendations.append("নিয়মিত চেকআপ করান")
    elif profile.age > 35:
        risk_factors.append({"factor": "advanced_age", "severity": "moderate", "bn": "বেশি বয়সে গর্ভধারণ"})
        recommendations.append("জেনেটিক টেস্ট করাতে পারেন")
    
    # BMI risk
    if profile.bmi < 18.5:
        risk_factors.append({"factor": "underweight", "severity": "moderate", "bn": "ওজন কম"})
        recommendations.append("পুষ্টিকর খাবার বেশি খান")
    elif profile.bmi > 30:
        risk_factors.append({"factor": "obesity", "severity": "high", "bn": "অতিরিক্ত ওজন"})
        recommendations.append("ওজন নিয়ন্ত্রণে রাখুন")
    
    # Blood pressure
    if profile.blood_pressure_systolic and profile.blood_pressure_systolic >= 140:
        risk_factors.append({"factor": "hypertension", "severity": "high", "bn": "উচ্চ রক্তচাপ"})
        recommendations.append("প্রি-এক্লাম্পসিয়ার লক্ষণ খেয়াল করুন")
        recommendations.append("লবণ কম খান")
    
    # Hemoglobin
    if profile.hemoglobin_level:
        if profile.hemoglobin_level < 7:
            risk_factors.append({"factor": "severe_anemia", "severity": "critical", "bn": "তীব্র রক্তস্বল্পতা"})
            recommendations.append("এখনই ডাক্তার দেখান, রক্ত লাগতে পারে")
        elif profile.hemoglobin_level < 11:
            risk_factors.append({"factor": "anemia", "severity": "moderate", "bn": "রক্তস্বল্পতা"})
            recommendations.append("আয়রন ট্যাবলেট নিয়মিত খান")
            recommendations.append("কচু শাক, কলিজা, খেজুর খান")
    
    # Blood sugar
    if profile.fasting_blood_sugar and profile.fasting_blood_sugar > 95:
        risk_factors.append({"factor": "gestational_diabetes", "severity": "high", "bn": "গর্ভকালীন ডায়াবেটিস"})
        recommendations.append("মিষ্টি এড়িয়ে চলুন")
        recommendations.append("নিয়মিত সুগার চেক করুন")
    
    # Determine overall risk
    severities = [rf["severity"] for rf in risk_factors]
    if "critical" in severities:
        overall_risk = RiskLevel.CRITICAL
    elif "high" in severities:
        overall_risk = RiskLevel.HIGH
    elif "moderate" in severities:
        overall_risk = RiskLevel.MODERATE
    else:
        overall_risk = RiskLevel.LOW
    
    profile.overall_risk_level = overall_risk
    patient_profiles[request.user_id] = profile
    
    return {
        "success": True,
        "overall_risk": overall_risk.value,
        "risk_factors": risk_factors,
        "recommendations_bengali": recommendations,
        "requires_immediate_attention": overall_risk == RiskLevel.CRITICAL,
        "message_bengali": _get_risk_message(overall_risk)
    }


def _get_risk_message(risk: RiskLevel) -> str:
    """Get Bengali message for risk level"""
    messages = {
        RiskLevel.LOW: "✅ আপনার ঝুঁকি কম। নিয়মিত চেকআপ চালিয়ে যান।",
        RiskLevel.MODERATE: "⚠️ কিছু বিষয়ে সতর্ক থাকুন। ডাক্তারের পরামর্শ মানুন।",
        RiskLevel.HIGH: "🔴 ঝুঁকি বেশি। নিয়মিত মনিটরিং দরকার।",
        RiskLevel.CRITICAL: "🚨 জরুরি! এখনই ডাক্তার দেখান।"
    }
    return messages.get(risk, messages[RiskLevel.LOW])


# ==================== OFFLINE SUPPORT ====================

@router.get("/offline/care-plans/{user_id}", response_model=dict)
async def get_offline_care_plans(user_id: str, weeks_ahead: int = 4):
    """
    📴 অফলাইন ব্যবহারের জন্য কেয়ার প্ল্যান ডাউনলোড করুন
    
    Download care plans for offline use.
    Can be synced via Firebase when 4G is detected.
    """
    profile = patient_profiles.get(user_id)
    if not profile:
        profile = MaternalRiskProfile(user_id=user_id, current_week=20)
    
    current_week = profile.current_week
    care_plans = []
    
    for week in range(current_week, min(current_week + weeks_ahead, 43)):
        plan = care_plan_service.generate_weekly_plan(profile, week)
        care_plans.append({
            "week": week,
            "plan": plan.dict()
        })
    
    return {
        "success": True,
        "message_bengali": f"পরবর্তী {weeks_ahead} সপ্তাহের প্ল্যান ডাউনলোড হয়েছে",
        "user_id": user_id,
        "current_week": current_week,
        "care_plans": care_plans,
        "downloaded_at": datetime.now().isoformat(),
        "offline_valid_until": (datetime.now().replace(day=datetime.now().day + 7)).isoformat()
    }


@router.get("/offline/emergency-protocols", response_model=dict)
async def get_offline_emergency_protocols():
    """
    📴 অফলাইন জরুরি প্রোটোকল
    
    Download all emergency protocols for offline use.
    Critical for low-internet zones.
    """
    protocols = emergency_bridge_service.emergency_protocols
    labor_guidance = emergency_bridge_service.labor_ar_guidance
    
    # Convert enum keys to strings
    protocols_dict = {k.value if hasattr(k, 'value') else str(k): v for k, v in protocols.items()}
    
    return {
        "success": True,
        "message_bengali": "জরুরি প্রোটোকল ডাউনলোড হয়েছে",
        "emergency_protocols": protocols_dict,
        "labor_guidance": labor_guidance,
        "emergency_contacts": emergency_bridge_service.emergency_contacts,
        "downloaded_at": datetime.now().isoformat()
    }
# ==================== HUMANIZATION ====================

class HumanizeCarePlanRequest(BaseModel):
    week_number: int
    summary_text: str
    checklist_items: List[str]

@router.post("/humanize-care-plan", response_model=dict)
async def humanize_care_plan(request: HumanizeCarePlanRequest):
    """
    Rewrite the care plan into a warm, empathetic speech script (Apu Persona)
    """
    
    system_prompt = """
    You are 'Janani Apu' (জননী আপু), a caring village sister.
    Rewrite the following pregnancy care plan summary into a warm, supportive Bengali speech script.

    INPUT DATA:
    - Week: {week}
    - Summary: {summary}
    - Required Actions: {checklist}

    YOUR GOAL:
    - Start with a warm greeting (e.g., "ও বোন," or "শোনো আপু,").
    - Explain the baby's growth simply.
    - Mention the mother's changes.
    - LIST the required actions gently but clearly as advice.
    - End with encouragement.

    RULES:
    - Speak ONLY in Bengali.
    - Use a conversational, spoken tone (not written/formal).
    - NO English words in the output script.
    - Make it sound like a voice message from a caring sister.
    """
    
    user_prompt = f"""
    Week: {request.week_number}
    Summary: {request.summary_text}
    Checklist: {', '.join(request.checklist_items)}
    """
    
    # Use the AI Service to generate the text
    # We construct a temporary message list here since get_response handles history internally usually
    # But for this specific rewriting task, we can use the client directly OR modify get_response to support this specific prompt.
    # To keep it clean and reuse the AIService logic (which handles model fallback), let's use get_response with a custom context override.
    
    custom_context = {
        "system_instruction": system_prompt.format(
            week=request.week_number,
            summary=request.summary_text,
            checklist=request.checklist_items
        ),
        "current_week": str(request.week_number)
    }
    
    humanized_text = await ai_service.get_response(
        message="Please rewrite this care plan for me.",
        user_context=custom_context,
        max_tokens=600
    )
    
    return {
        "audio_text": humanized_text
    }
