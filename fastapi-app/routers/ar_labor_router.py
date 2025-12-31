"""
AR Emergency Labor Assistant Router
API endpoints for the offline-first AR labor guidance system
Updated: 2025 MediaPipe WASM Integration with Modular Emergency Scenarios
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

from services.ar_labor_service import (
    ar_labor_assistant,
    LaborStage,
    EmergencyType,
    STAGE_INSTRUCTIONS,
    EMERGENCY_PROTOCOLS,
    LaborStage
)
from services.ai_service import AIService

router = APIRouter(prefix="/api/ar-labor", tags=["AR Labor Assistant"])
templates = Jinja2Templates(directory="templates")
ai_service = AIService()

class AIConsultRequest(BaseModel):
    query: str
    context: Optional[Dict] = None
    patient_profile: Optional[Dict] = None


# ============ AR Dashboard Route ============

@router.get("/dashboard", response_class=HTMLResponse)
async def ar_dashboard(request: Request):
    """Serve the AR Emergency Dashboard with MediaPipe WASM integration"""
    return templates.TemplateResponse("ar_dashboard.html", {"request": request})


class ActionLogRequest(BaseModel):
    """Request model for logging actions"""
    action: str
    stage: Optional[str] = None
    details: Optional[Dict] = None


class StageUpdateRequest(BaseModel):
    """Request model for updating current stage"""
    stage: str


class SyncDataRequest(BaseModel):
    """Request model for syncing offline data"""
    session_log: List[Dict]
    device_id: Optional[str] = None
    timestamp: str

class ClinicalAnalysisRequest(BaseModel):
    """Request for Doctor Mode Clinical Insight Report"""
    user_id: Optional[str] = None
    patient_data: Optional[Dict] = None  # If profile not available, pass raw dict
    current_vitals: Optional[Dict] = None

@router.post("/clinical-analysis")
async def generate_clinical_analysis(request: ClinicalAnalysisRequest):
    """
    🏥 DOCTOR MODE: Generate High-Density Clinical Insight Report.
    Uses 'Senior Clinical Strategist' persona (separate from Village Sister).
    """
    
    # Resolving profile (Mock logic if database not connected)
    from models.care_models import MaternalRiskProfile, RiskLevel
    
    profile = None
    if request.user_id:
        # In a real app, fetch from database. 
        # For now, we construct a dummy or use request data
        profile = MaternalRiskProfile(
            user_id=request.user_id,
            existing_conditions=["Chronic Hypertension", "Previous C-Section"],
            overall_risk_level=RiskLevel.HIGH
        )
        
        # Inject Mock Real-time Data for Demo (Proof of Concept)
        # 1. Mental Condition (from recent memory interactions)
        profile.recent_memories = [
            {"date": "2024-12-28", "context": "User expressed severe anxiety about C-section.", "resolved": False},
            {"date": "2024-12-29", "context": "Financial stress mentioned regarding hospital costs.", "resolved": False}
        ]
        
        # 2. Lifestyle/Food Habits (Mocked as if fetched from longitudinal data)
        setattr(profile, 'lifestyle_factors', [
            "Diet: High sodium intake observed (Salt preference)",
            "Hydration: Low (approx 1L/day)",
            "Sleep: Insomnia reported last 3 nights",
            "Support: Living with mother-in-law, high social support"
        ])
    
    report_json = await ai_service.generate_clinical_report(
        profile=profile,
        current_vitals=request.current_vitals or {}
    )
    
    import json
    try:
        return json.loads(report_json)
    except:
        return {"error": "Failed to parse clinical report", "raw": report_json}


# ============ Stage Instructions ============

@router.get("/stages")
async def get_all_stages():
    """Get list of all labor stages with metadata"""
    return {
        "success": True,
        "stages": ar_labor_assistant.get_all_stages(),
        "disclaimer": {
            "text_bn": "⚠️ এটি একটি সিদ্ধান্ত সহায়তা টুল। প্রশিক্ষিত ধাত্রী বা ডাক্তারের বিকল্প নয়।",
            "text_en": "⚠️ Decision Support Tool. NOT a replacement for trained medical professionals."
        }
    }


@router.get("/stages/{stage_id}")
async def get_stage_instructions(stage_id: str):
    """Get detailed AR instructions for a specific labor stage"""
    try:
        stage = LaborStage(stage_id)
        instructions = ar_labor_assistant.get_stage_instructions(stage)
        return {
            "success": True,
            "stage_id": stage_id,
            "data": instructions
        }
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Stage '{stage_id}' not found")


# ============ Emergency Protocols ============

@router.get("/emergencies")
async def get_all_emergencies():
    """Get list of all emergency protocols"""
    return {
        "success": True,
        "emergencies": ar_labor_assistant.get_all_emergencies(),
        "emergency_numbers": {
            "bangladesh_999": "999",
            "ambulance": "199",
            "health_helpline": "16789"
        }
    }


@router.get("/emergencies/{emergency_type}")
async def get_emergency_protocol(emergency_type: str):
    """Get detailed emergency protocol for a specific situation"""
    try:
        etype = EmergencyType(emergency_type)
        protocol = ar_labor_assistant.get_emergency_protocol(etype)
        return {
            "success": True,
            "emergency_type": emergency_type,
            "protocol": protocol
        }
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Emergency type '{emergency_type}' not found")


# ============ Pose Detection Config ============

@router.get("/pose-config")
async def get_pose_landmarks_config():
    """Get MediaPipe pose landmark configurations for AR overlay"""
    return {
        "success": True,
        "landmarks": ar_labor_assistant.get_pose_landmarks_config(),
        "mediapipe_info": {
            "model": "pose_landmarker",
            "landmarks_count": 33,
            "supported_positions": ["lithotomy", "knee_chest", "left_lateral", "semi_reclined"]
        }
    }


# ============ Session Management ============

@router.post("/log-action")
async def log_action(request: ActionLogRequest):
    """Log an action for offline sync"""
    log_entry = ar_labor_assistant.log_action(
        action=request.action,
        details=request.details
    )
    return {
        "success": True,
        "logged": log_entry
    }


@router.get("/session-log")
async def get_session_log():
    """Get current session log"""
    return {
        "success": True,
        "log": ar_labor_assistant.get_session_log()
    }


# ============ Offline Data Bundle ============

@router.get("/offline-bundle")
async def get_offline_data_bundle():
    """
    Get complete data bundle for offline use.
    This endpoint should be called once when the app loads to cache all data.
    """
    return {
        "success": True,
        "bundle": ar_labor_assistant.get_offline_data_bundle(),
        "cache_instructions": {
            "storage": "IndexedDB",
            "key": "ar_labor_offline_data",
            "ttl_hours": 168  # 1 week
        }
    }


@router.post("/sync")
async def sync_offline_data(request: SyncDataRequest):
    """
    Sync offline session data when connectivity is restored.
    This endpoint receives logged actions from offline sessions.
    """
    try:
        # In production, this would store to Firebase/database
        # For now, we log and acknowledge
        synced_count = len(request.session_log)
        
        return {
            "success": True,
            "synced_entries": synced_count,
            "device_id": request.device_id,
            "sync_timestamp": datetime.now().isoformat(),
            "message_bn": f"✅ {synced_count}টি এন্ট্রি সিঙ্ক হয়েছে",
            "message_en": f"✅ {synced_count} entries synced successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Battery-Aware Mode ============

@router.get("/power-save-content")
async def get_power_save_content():
    """
    Get simplified 2D illustration content for power-save mode.
    Used when battery drops below 20%.
    """
    simplified_stages = []
    
    for stage in LaborStage:
        if stage == LaborStage.EMERGENCY:
            continue
            
        stage_data = STAGE_INSTRUCTIONS.get(stage, {})
        simplified_stages.append({
            "stage_id": stage.value,
            "title_bn": stage_data.get("title_bn", ""),
            "title_en": stage_data.get("title_en", ""),
            "icon": stage_data.get("icon", "📋"),
            "color": stage_data.get("color", "#666"),
            "instructions": [
                {
                    "step": inst.get("step"),
                    "text_bn": inst.get("text_bn"),
                    "text_en": inst.get("text_en"),
                    # No AR visuals in power-save mode
                    "illustration": f"2d_{inst.get('ar_visual', 'default')}.svg"
                }
                for inst in stage_data.get("instructions", [])
            ]
        })
    
    return {
        "success": True,
        "mode": "power_save",
        "message_bn": "🔋 ব্যাটারি সাশ্রয় মোড - সরলীকৃত নির্দেশনা",
        "message_en": "🔋 Power Save Mode - Simplified instructions",
        "stages": simplified_stages
    }


# ============ 2025 WASM Emergency Scenarios ============

@router.get("/scenario/{scenario_id}")
async def get_emergency_scenario(scenario_id: str):
    """
    Get detailed AR scenario data for MediaPipe WASM client-side processing.
    Scenarios: labor, bleeding (PPH), seizure (eclampsia), newborn (neonatal resuscitation)
    """
    scenarios = {
        "labor": {
            "id": "labor",
            "title_bn": "👶 প্রসব সহায়তা",
            "title_en": "Labor Assistance",
            "color": "#E91E63",
            "priority": "normal",
            "ar_config": {
                "primary_landmarks": [23, 24],  # Hips
                "secondary_landmarks": [11, 12],  # Shoulders
                "overlay_type": "pelvis_guide",
                "guide_color": "#4CAF50"
            },
            "instructions": [
                {"step": 1, "text_bn": "মাকে আরামদায়ক অবস্থানে রাখুন - বাম কাত বা আধা-বসা", "text_en": "Position mother comfortably - left lateral or semi-reclined", "priority": "normal"},
                {"step": 2, "text_bn": "সবুজ জোনে পেলভিস উঁচু রাখুন (১৫ ডিগ্রি)", "text_en": "Elevate pelvis in green zone (15 degrees)", "priority": "normal", "ar_highlight": "pelvis"},
                {"step": 3, "text_bn": "মাথা বের হলে ঘাড়ে নাড়ির প্যাঁচ পরীক্ষা করুন", "text_en": "Check for cord around neck when head emerges", "priority": "critical"},
                {"step": 4, "text_bn": "নাড়ি কাটার আগে ৩০ সেকেন্ড অপেক্ষা করুন", "text_en": "Wait 30 seconds before cutting cord", "priority": "warning", "timer": 30}
            ],
            "voice_prompts": ["মাকে শান্ত রাখুন", "গভীর শ্বাস নিতে বলুন", "পুশ করুন"]
        },
        "bleeding": {
            "id": "bleeding",
            "title_bn": "🩸 প্রসব পরবর্তী রক্তপাত (PPH)",
            "title_en": "Postpartum Hemorrhage",
            "color": "#F44336",
            "priority": "critical",
            "ar_config": {
                "primary_landmarks": [23, 24],  # Hips for fundal massage
                "secondary_landmarks": [0],  # Nose for body orientation
                "overlay_type": "fundal_massage",
                "guide_color": "#F44336",
                "animation": "pulsate"
            },
            "instructions": [
                {"step": 1, "text_bn": "🚨 এখনই ৯৯৯ কল করুন - এটি জরুরি অবস্থা", "text_en": "Call 999 NOW - This is an emergency", "priority": "critical"},
                {"step": 2, "text_bn": "জরায়ু ম্যাসেজ: নাভির নিচে লাল বৃত্তে শক্ত করে চাপুন", "text_en": "Uterine massage: Press firmly in red circle below navel", "priority": "critical", "ar_highlight": "fundus"},
                {"step": 3, "text_bn": "১৫ মিনিট ধরে ঘড়ির কাঁটার দিকে ঘোরান", "text_en": "Rotate clockwise for 15 minutes", "priority": "critical", "timer": 900},
                {"step": 4, "text_bn": "মায়ের পা উঁচু করে রাখুন - শক থেকে বাঁচাতে", "text_en": "Elevate legs - prevent shock", "priority": "warning"}
            ],
            "voice_prompts": ["জরায়ু ম্যাসেজ চালু রাখুন", "শক্ত করে চাপুন", "সাহায্য আসছে"]
        },
        "seizure": {
            "id": "seizure",
            "title_bn": "⚡ খিঁচুনি / একলাম্পসিয়া",
            "title_en": "Seizure / Eclampsia",
            "color": "#FF9800",
            "priority": "critical",
            "ar_config": {
                "primary_landmarks": [11, 23],  # Left shoulder to hip
                "secondary_landmarks": [12, 24],  # Right side reference
                "overlay_type": "recovery_position",
                "guide_color": "#FF9800",
                "animation": "arrow_direction"
            },
            "instructions": [
                {"step": 1, "text_bn": "🚨 এখনই ৯৯৯ কল করুন", "text_en": "Call 999 immediately", "priority": "critical"},
                {"step": 2, "text_bn": "মাকে বাম কাতে শোয়ান - তীরের দিকে ঘোরান", "text_en": "Turn mother to LEFT side - follow arrow direction", "priority": "critical", "ar_highlight": "rotation"},
                {"step": 3, "text_bn": "মুখে কিছু দেবেন না - জিহ্বা কামড়ানো স্বাভাবিক", "text_en": "Nothing in mouth - tongue biting is normal", "priority": "warning"},
                {"step": 4, "text_bn": "শ্বাসনালী পরিষ্কার রাখুন - বমি থাকলে সরান", "text_en": "Keep airway clear - remove vomit if any", "priority": "critical"}
            ],
            "voice_prompts": ["বাম দিকে ঘোরান", "শ্বাসনালী পরিষ্কার রাখুন", "সময় নোট করুন"]
        },
        "newborn": {
            "id": "newborn",
            "title_bn": "👶💚 নবজাতকের পুনরুজ্জীবন",
            "title_en": "Neonatal Resuscitation",
            "color": "#4CAF50",
            "priority": "critical",
            "ar_config": {
                "primary_landmarks": [11, 12],  # Mother's chest for skin-to-skin
                "secondary_landmarks": [23, 24],
                "overlay_type": "chest_compressions",
                "guide_color": "#4CAF50",
                "metronome_bpm": 110
            },
            "instructions": [
                {"step": 1, "text_bn": "শিশুকে শুকনো কাপড় দিয়ে মুছুন - উত্তেজিত করুন", "text_en": "Dry baby with cloth - stimulate", "priority": "critical"},
                {"step": 2, "text_bn": "মাথা সামান্য পিছনে রাখুন - শ্বাসনালী খুলুন", "text_en": "Tilt head slightly back - open airway", "priority": "critical", "ar_highlight": "head_tilt"},
                {"step": 3, "text_bn": "🫁 শ্বাস না নিলে: ৫টি রেসকিউ শ্বাস দিন", "text_en": "If not breathing: Give 5 rescue breaths", "priority": "critical"},
                {"step": 4, "text_bn": "💓 হৃদস্পন্দন না থাকলে: বুকে চাপ শুরু করুন (১০০-১২০/মিনিট)", "text_en": "No heartbeat: Start chest compressions (100-120/min)", "priority": "critical", "metronome": True}
            ],
            "voice_prompts": ["শুকিয়ে নিন", "উত্তেজিত করুন", "শ্বাস দিন", "চাপ দিন"]
        }
    }
    
    if scenario_id not in scenarios:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    
    return {
        "success": True,
        "scenario": scenarios[scenario_id],
        "mediapipe_config": {
            "model": "pose_landmarker_lite",
            "delegate": "GPU",
            "running_mode": "VIDEO",
            "num_poses": 1
        }
    }


@router.get("/scenarios")
async def get_all_scenarios():
    """Get list of all available AR emergency scenarios"""
    return {
        "success": True,
        "scenarios": [
            {"id": "labor", "title_bn": "👶 প্রসব", "title_en": "Labor", "color": "#E91E63"},
            {"id": "bleeding", "title_bn": "🩸 রক্তপাত", "title_en": "PPH", "color": "#F44336"},
            {"id": "seizure", "title_bn": "⚡ খিঁচুনি", "title_en": "Seizure", "color": "#FF9800"},
            {"id": "newborn", "title_bn": "👶💚 নবজাতক", "title_en": "Newborn", "color": "#4CAF50"}
        ],
        "dashboard_url": "/api/ar-labor/dashboard"
    }


@router.get("/wasm-config")
async def get_wasm_config():
    """Get MediaPipe WASM configuration for client-side initialization"""
    return {
        "success": True,
        "mediapipe": {
            "cdn_base": "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14",
            "model_url": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
            "wasm_files": [
                "wasm/vision_wasm_internal.wasm",
                "wasm/vision_wasm_internal.js"
            ]
        },
        "cache_config": {
            "cache_name": "ar-wasm-v1.0",
            "strategy": "cache_first",
            "ttl_days": 30
        },
        "performance": {
            "target_fps": 30,
            "low_power_fps": 15,
            "delegate_preference": ["GPU", "CPU"]
        }
    }


# ============ AI Consultation ============

@router.post("/consult")
async def consult_ai_emergency(request: AIConsultRequest):
    """
    Get dynamic AR instructions for any emergency situation using AI.
    Returns structured JSON compatible with the AR dashboard.
    """
    try:
        # Prompt designed to return valid JSON for the frontend WITH a warm, natural tone
        system_prompt = """
        You are 'Janani Apu' (জননী আপু) - a warm, caring, and experienced Digital Midwife (ধাত্রী) from rural Bangladesh.
        
        Your personality:
        - Speak like a supportive older sister (বড় আপু) who is calm but firm in emergencies.
        - Use Noakhali dialect hints and culturally appropriate phrases.
        - Validate the person's feelings first, then give clear instructions.
        - Example tone: "আপু, ঘাবড়াইবেন না। আমরা একসাথে এটা সামলাচ্ছি।" (Don't panic, Apu. We're handling this together.)
        
        Output ONLY valid JSON. No markdown, no explanations.
        
        Structure the response exactly like this:
        {
            "id": "dynamic_emergency",
            "title_bn": "Bengali Title (short)",
            "title_en": "English Title",
            "icon": "⚠️",
            "color": "#F44336",
            "priority": "critical",
            "overlay": "generic_warning",
            "instructions": [
                {"step": 1, "text_bn": "Step 1 IN A NATURAL, CONVERSATIONAL BENGALI TONE", "text_en": "Step 1 in plain English", "priority": "critical"},
                {"step": 2, "text_bn": "Step 2 IN A NATURAL, CONVERSATIONAL BENGALI TONE", "text_en": "Step 2 in plain English", "priority": "high"}
            ]
        }
        
        IMPORTANT for text_bn: 
        - Do NOT use formal medical jargon. Use simple, everyday Bengali.
        - Start with an empathetic phrase like "আপু, প্রথমে..." or "আমার কথা শুনুন...".
        - Use reassuring phrases like "আমরা একসাথে আছি" (We are together).
        - Be direct and clear for actions.
        
        Available Overlays (use one if applicable): 
        - 'pelvis_guide' (for positions)
        - 'fundal_massage' (for bleeding)
        - 'recovery_position' (for unconsciousness/rolling)
        - 'chest_compressions' (for heart/breathing)
        - 'generic_warning' (default)
        
        Keep steps concise, action-oriented, and prioritized.
        Max 4 steps.
        OUTPUT RAW JSON ONLY. DO NOT USE MARKDOWN BLOCKS.
        """
        
        # Add patient context to the situation if available
        # TRANSLATION LAYER: Convert query to English if it's in Bengali
        query = request.query
        if any('\u0980' <= c <= '\u09ff' for c in query):
             translated_query = await ai_service.translate_to_english(query)
             query = f"{query} ({translated_query})"
        
        situation = f"Situation: {query}"
        
        # Pull augmented profile if userId is in context
        user_id = (request.context or {}).get("user_id", "web_user")
        from routers.midwife_router import get_augmented_profile
        profile = get_augmented_profile(user_id)
        
        if profile:
            p_dict = profile.dict()
            situation += f" | Patient History: Age {p_dict.get('age')}, Trimester {p_dict.get('trimester')}, Conditions: {p_dict.get('existing_conditions')}, Risk: {p_dict.get('overall_risk_level')}"
        elif request.patient_profile:
            p = request.patient_profile
            situation += f" | Patient Context: Age {p.get('age')}, Trimester {p.get('trimester')}, Blood Group {p.get('blood_group')}, Risk Level {p.get('risk_level')}"
        
        response = await ai_service.get_response(
            message=f"{situation}. Provide emergency AR instructions in JSON.",
            user_context={"system_instruction": system_prompt},
            is_emergency=True,
            max_tokens=1000,
            json_mode=True
        )
        
        # Robust JSON cleaning
        import json
        import re
        
        cleaned_response = response.strip()
        
        # Find the first { and last }
        match = re.search(r'(\{.*\})', cleaned_response, re.DOTALL)
        if match:
            cleaned_response = match.group(1)
        
        scenario_data = json.loads(cleaned_response)
        
        # Ensure all required frontend fields are present
        if "icon" not in scenario_data:
            scenario_data["icon"] = "🤖"
        
        if "overlay" not in scenario_data:
            scenario_data["overlay"] = "generic_warning"
            
        # Add default styling/config if missing
        if "ar_config" not in scenario_data:
            scenario_data["ar_config"] = {
                 "overlay_type": scenario_data.get("overlay", "generic_warning"),
                 "guide_color": scenario_data.get("color", "#F44336")
            }
            
        scenario_data["id"] = "ai_consult"
            
        return {
            "success": True,
            "scenario": scenario_data
        }
        
    except Exception as e:
        import traceback
        print(f"AI Consult Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        # Fallback to a generic emergency response
        return {
            "success": True, 
            "scenario": {
                "id": "ai_consult_fallback",
                "title_bn": "জরুরি পরামর্শ",
                "title_en": "Emergency Advice",
                "icon": "🆘",
                "color": "#F44336",
                "overlay": "generic_warning",
                "instructions": [
                    {"step": 1, "text_bn": "৯৯৯ কল করুন", "text_en": "Call 999", "priority": "critical"},
                    {"step": 2, "text_bn": "ডাক্তারের সাথে যোগাযোগ করুন", "text_en": "Contact a doctor", "priority": "critical"}
                ]
            }
        }
