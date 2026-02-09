"""
Janani AI - Omniscient Agent Architecture
FastAPI Entry Point with Agent Brain
"""

# Handle SQLite for ChromaDB (Render/Linux fix)
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import os
import base64
import tempfile
import json
import re
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from config import settings
from services.ai_agent import ask_janani_agent, ask_janani_agent_structured, PatientState
from services.ai_service import AIService

# ============================================================
# SHARED STATE MODULE (Avoids Circular Imports)
# Import IN_MEMORY_DB from shared module instead of defining here
# ============================================================
from services.patient_state import (
    IN_MEMORY_DB, 
    get_patient, 
    update_patient as update_patient_state_fn,
    record_emergency,
    record_care_plan,
    record_document_upload
)

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent




# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================
class AgentChatRequest(BaseModel):
    user_id: str = "default_user"
    query: Optional[str] = None
    image_base64: Optional[str] = None
    audio_base64: Optional[str] = None


class AgentChatResponse(BaseModel):
    response: str
    user_id: str
    context_used: bool = True
    tool_executed: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    action: Optional[str] = None
    transcription: Optional[str] = None
    audio_base64: Optional[str] = None
    emergency_activated: Optional[bool] = None
    emergency_redirect: Optional[str] = None


class UpdatePatientRequest(BaseModel):
    user_id: str
    updates: Dict[str, Any]

class CausalVitals(BaseModel):
    blood_pressure: str
    protein_urine: Optional[str] = None
    edema: Optional[str] = None
    headache: Optional[str] = None
    gestational_week: Optional[int] = None

class HistoryEntry(BaseModel):
    week: Optional[int] = None
    blood_pressure: Optional[str] = None
    symptoms: List[str] = []
    notes: Optional[str] = None

class BaselineVitals(BaseModel):
    blood_pressure: Optional[str] = None
    weight: Optional[str] = None

class CausalAnalysisRequest(BaseModel):
    patient_id: str
    current_vitals: CausalVitals
    patient_history: List[HistoryEntry] = []
    baseline_vitals: Optional[BaselineVitals] = None

class AssessRequest(BaseModel):
    patient_id: str
    current_vitals: CausalVitals


# ============================================================
# FASTAPI APP INITIALIZATION
# ============================================================
app = FastAPI(
    title="Janani AI - Omniscient Agent",
    description="Digital Midwife with Agent Brain Architecture",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
if (BASE_DIR / "static" / "_next").exists():
    app.mount("/_next", StaticFiles(directory=str(BASE_DIR / "static" / "_next")), name="next")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

ai_service = AIService()


# ============================================================
# AGENT ENDPOINTS (The New Architecture)
# ============================================================

@app.post("/api/agent/chat", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest):
    """
    🧠 THE OMNISCIENT AGENT ENDPOINT
    
    The Agent knows the patient's COMPLETE context before responding.
    This is the single entry point for all AI interactions.
    """
    # 1. Retrieve patient state from Master JSON
    user_id = request.user_id
    if user_id not in IN_MEMORY_DB:
        # Create new patient with defaults
        IN_MEMORY_DB[user_id] = {
            "user_id": user_id,
            "name": "Unknown",
            "weeks_pregnant": 20,
            "trimester": "2nd",
            "age": 0,
            "risks": [],
            "conditions": [],
            "last_symptoms": [],
            "recent_concerns": [],
            "blood_pressure": None,
            "hemoglobin": None,
            "last_checkup": None
        }
    
    from services.patient_data_service import patient_data_service
    from services.speech_service import speech_service
    full_context = patient_data_service.get_full_context(user_id)
    transcription = None
    query_text = (request.query or "").strip()
    if request.audio_base64:
        audio_payload = request.audio_base64
        if "base64," in audio_payload:
            audio_payload = audio_payload.split("base64,", 1)[1]
        try:
            audio_bytes = base64.b64decode(audio_payload)
        except Exception:
            audio_bytes = b""
        if audio_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name
            try:
                transcription = await speech_service.transcribe_audio(temp_path)
            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except Exception:
                        pass
        if not transcription or transcription == "Sorry, could not understand audio.":
            return AgentChatResponse(
                response="দুঃখিত, ভয়েস বুঝতে পারিনি। আবার বলুন।",
                user_id=user_id,
                context_used=True,
                transcription=transcription
            )
        query_text = transcription
    if not query_text:
        return AgentChatResponse(
            response="আপু, আমি শুনছি। আপনি কী জানতে চান বলুন।",
            user_id=user_id,
            context_used=True,
            transcription=transcription
        )
    tool_executed = None
    tool_result = None
    ai_result = ""
    action = "NONE"
    tool_message = None
    decision = await ask_janani_agent_structured(
        query=query_text,
        state=full_context,
        image_base64=request.image_base64
    )
    ai_result = (decision.get("response") or "").strip()
    action = decision.get("action") or "NONE"
    tool_call = (decision.get("tool_call") or "NONE").strip()
    tool_params = decision.get("tool_params") or {}
    emergency_confidence = float(decision.get("emergency_confidence") or 0.0)
    ql = query_text.lower()
    profile_keywords = [
        "আমার নাম", "নাম", "name is", "my name", "বয়স", "age",
        "সপ্তাহ", "week", "weeks", "pregnant", "গর্ভ", "trimester"
    ]
    has_profile_signal = any(k in ql for k in profile_keywords)
    if tool_call == "UPDATE_PROFILE" and not has_profile_signal:
        tool_call = "NONE"
        action = "NONE"
    if tool_call == "ACTIVATE_EMERGENCY" and emergency_confidence < 0.9:
        tool_call = "NONE"
        action = "NONE"
        if not ai_result:
            ai_result = "আপনার অবস্থা গুরুতর মনে হচ্ছে। আপনি কি জরুরি সেবা চালু করতে চান?"
        else:
            ai_result = f"{ai_result}\n\nআপনার অবস্থা গুরুতর মনে হচ্ছে। আপনি কি জরুরি সেবা চালু করতে চান?"
    if tool_call != "NONE":
        try:
            from services.agent_tools import execute_tool
            tool_executed = tool_call
            msg, res = await execute_tool(tool_call, tool_params, full_context)
            tool_message = msg
            tool_result = res
            if tool_executed == "UPDATE_PROFILE":
                full_context = patient_data_service.get_full_context(user_id)
        except Exception:
            tool_executed = None
    if not ai_result and tool_message:
        ai_result = tool_message
    if not ai_result:
        ai_result = "আপু, আমি আপনার কথা শুনছি। কী নিয়ে চিন্তা হচ্ছে বলুন, আমি পাশে আছি।"
    audio_response_base64 = None
    if request.audio_base64 and ai_result:
        try:
            audio_bytes = await speech_service.text_to_speech(ai_result, language="bn")
            audio_response_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        except Exception:
            audio_response_base64 = None
    emergency_activated = None
    emergency_redirect = None
    if tool_executed == "ACTIVATE_EMERGENCY" and tool_result:
        emergency_activated = tool_result.get("emergency_activated", False)
        emergency_redirect = tool_result.get("emergency_redirect", "http://localhost:8000/ar-dashboard")
    return AgentChatResponse(
        response=ai_result,
        user_id=user_id,
        context_used=True,
        tool_executed=tool_executed,
        tool_result=tool_result,
        action=action,
        transcription=transcription,
        audio_base64=audio_response_base64,
        emergency_activated=emergency_activated,
        emergency_redirect=emergency_redirect
    )


@app.post("/api/agent/chat-with-image")
async def agent_chat_with_image(
    user_id: str = Form(default="default_user"),
    query: str = Form(...),
    image: UploadFile = File(None)
):
    """
    🖼️ Agent Chat with Vision Support
    
    Upload an image (food, prescription, symptom) for analysis.
    """
    image_base64 = None
    
    if image:
        contents = await image.read()
        image_base64 = base64.b64encode(contents).decode("utf-8")
    
    # Get patient state
    if user_id not in IN_MEMORY_DB:
        IN_MEMORY_DB[user_id] = {
            "user_id": user_id,
            "name": "Unknown",
            "weeks_pregnant": 0,
            "risks": [],
            "conditions": [],
            "last_symptoms": [],
            "recent_concerns": []
        }
    
    patient_state = IN_MEMORY_DB[user_id]
    
    response = await ask_janani_agent(
        query=query,
        state=patient_state,
        image_base64=image_base64
    )
    
    return {"response": response, "user_id": user_id, "image_analyzed": image is not None}


@app.get("/api/agent/state/{user_id}")
async def get_patient_state(user_id: str):
    """
    📋 Get Patient's Complete State (Master JSON)
    """
    if user_id not in IN_MEMORY_DB:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return IN_MEMORY_DB[user_id]


@app.post("/api/agent/state/update")
async def update_patient_state(request: UpdatePatientRequest):
    """
    ✏️ Update Patient State
    
    Used by frontend to sync profile changes, symptoms, etc.
    """
    user_id = request.user_id
    
    if user_id not in IN_MEMORY_DB:
        IN_MEMORY_DB[user_id] = {
            "user_id": user_id,
            "name": "Unknown",
            "weeks_pregnant": 0,
            "risks": [],
            "conditions": [],
            "last_symptoms": [],
            "recent_concerns": []
        }
    
    # Merge updates into existing state
    IN_MEMORY_DB[user_id].update(request.updates)
    
    return {"message": "State updated", "state": IN_MEMORY_DB[user_id]}


@app.get("/api/agent/states")
async def list_all_states():
    """
    📊 List all patient states (Debug endpoint)
    """
    return {"patients": list(IN_MEMORY_DB.keys()), "count": len(IN_MEMORY_DB)}


def parse_blood_pressure(bp_value: Optional[str]) -> Optional[Dict[str, int]]:
    if not bp_value:
        return None
    matches = re.findall(r"\d+", bp_value)
    if len(matches) < 2:
        return None
    systolic = int(matches[0])
    diastolic = int(matches[1])
    return {"systolic": systolic, "diastolic": diastolic}


def is_severe_flag(value: Optional[str]) -> bool:
    if not value:
        return False
    normalized = value.strip().lower()
    severe_keywords = ["severe", "very", "+++","3+", "critical", "high", "yes"]
    return any(keyword in normalized for keyword in severe_keywords)


def extract_json_from_text(raw_text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(raw_text)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", raw_text)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except Exception:
            return None


@app.post("/api/assess")
async def assess_risk(request: AssessRequest):
    bp = parse_blood_pressure(request.current_vitals.blood_pressure)
    risk_level = "LOW RISK"
    action = "Routine monitoring"
    if bp:
        if bp["systolic"] >= 160 or bp["diastolic"] >= 110:
            risk_level = "CRITICAL RISK"
            action = "Immediate referral to emergency care"
        elif bp["systolic"] > 140 or bp["diastolic"] > 90:
            risk_level = "HIGH RISK"
            action = "Seek clinical evaluation within 24 hours"
    return {
        "patient_id": request.patient_id,
        "risk_level": risk_level,
        "immediate_action": action
    }


@app.post("/api/causal-analysis")
async def causal_analysis(request: CausalAnalysisRequest):
    if not ai_service.client:
        raise HTTPException(status_code=503, detail="DeepSeek API not configured.")
    bp = parse_blood_pressure(request.current_vitals.blood_pressure)
    is_emergency = False
    if bp and (bp["systolic"] > 160 or bp["diastolic"] > 110):
        is_emergency = True
    if is_severe_flag(request.current_vitals.headache) or is_severe_flag(request.current_vitals.edema) or is_severe_flag(request.current_vitals.protein_urine):
        is_emergency = True

    current_week = request.current_vitals.gestational_week
    history = request.patient_history or []
    filtered_history = history
    if is_emergency:
        if current_week is not None:
            filtered_history = [entry for entry in history if entry.week is not None and entry.week >= current_week - 4]
        else:
            filtered_history = history[-4:]

    payload = {
        "patient_id": request.patient_id,
        "mode": "EMERGENCY" if is_emergency else "ROUTINE",
        "current_vitals": request.current_vitals.dict(),
        "baseline_vitals": request.baseline_vitals.dict() if request.baseline_vitals else None,
        "patient_history": [entry.dict() for entry in filtered_history]
    }

    system_prompt = """
You are an expert obstetrician. Return ONLY valid JSON. No extra text.
Produce exactly a 5-step analysis with this schema:
{
  "patient_id": "string",
  "mode": "EMERGENCY" | "ROUTINE",
  "steps": [
    { "step": 1, "title": "Anomalies Detected", "findings": ["..."] },
    { "step": 2, "title": "Timeline of Symptoms", "timeline": ["week X: ..."] },
    { "step": 3, "title": "Physiological Mechanisms", "mechanisms": ["concise reasoning summary"] },
    { "step": 4, "title": "Differential Diagnosis", "diagnoses": [{"name": "string", "probability": 0.0, "rationale": "string"}] },
    { "step": 5, "title": "WHO-based Recommendation", "recommendation": {"summary": "string", "urgency": "string", "actions": ["..."]} }
  ]
}
"""

    response_text = await ai_service.get_response(
        message=json.dumps(payload, ensure_ascii=False),
        user_context={"system_instruction": system_prompt},
        json_mode=True,
        use_gemini=False,
        max_tokens=1200
    )

    if "AI সেবা কনফিগার করা হয়নি" in response_text or "কোনো AI সেবা" in response_text:
        raise HTTPException(status_code=503, detail="DeepSeek API unavailable.")

    parsed = extract_json_from_text(response_text)
    if not parsed or "steps" not in parsed or len(parsed.get("steps", [])) != 5:
        raise HTTPException(status_code=502, detail="DeepSeek returned invalid JSON for causal analysis.")

    return parsed


@app.get("/api/health")
async def api_health_check():
    deepseek_status = "not_configured"
    if ai_service.client:
        try:
            ping_response = await ai_service.get_response(
                message='{"ping":"ok"}',
                user_context={"system_instruction": "Return ONLY valid JSON with {\"status\":\"ok\"}."},
                json_mode=True,
                use_gemini=False,
                max_tokens=50
            )
            parsed = extract_json_from_text(ping_response)
            deepseek_status = "ok" if parsed and parsed.get("status") == "ok" else "degraded"
        except Exception:
            deepseek_status = "down"
    return {"status": "ok", "deepseek": deepseek_status}


# ============================================================
# LEGACY ROUTER IMPORTS (Preserved for backward compatibility)
# ============================================================
from routers import voice, chat, vision, emergency, food, food_rag
from routers import recommendation_router, document_router, midwife_router
from routers import ar_labor_router, auth, report_router, coaching_router

# Include legacy routers
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(vision.router, prefix="/api/vision", tags=["vision"])
app.include_router(emergency.router, prefix="/api/emergency", tags=["emergency"])
app.include_router(food.router, tags=["food"])
app.include_router(food_rag.router, tags=["food-rag"])
app.include_router(recommendation_router.router, tags=["recommendations"])
app.include_router(document_router.router, tags=["profile-documents"])
app.include_router(auth.router)
app.include_router(midwife_router.router, tags=["digital-midwife"])
app.include_router(ar_labor_router.router, tags=["ar-labor-assistant"])
app.include_router(report_router.router)
app.include_router(coaching_router.router)


# ============================================================
# WEB INTERFACE ROUTES
# ============================================================

@app.get("/")
async def home(request: Request):
    """Serve the main web interface"""
    response = templates.TemplateResponse("agent_demo.html", {
        "request": request,
        "app_name": settings.app_name
    })
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/ar-dashboard")
async def ar_dashboard_page(request: Request):
    """Serve the AR Emergency Dashboard"""
    return templates.TemplateResponse("ar_dashboard.html", {"request": request})


@app.get("/agent-demo")
async def agent_demo_page(request: Request):
    """Serve the Omniscient Agent Demo UI"""
    return templates.TemplateResponse("agent_demo.html", {"request": request})


@app.get("/offline_rules.json")
async def offline_rules():
    """Serve offline rules for the frontend"""
    path = BASE_DIR / "static" / "offline_rules.json"
    if not path.exists():
        return {"error": "File not found"}
    return FileResponse(str(path))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "Janani AI - Omniscient Agent",
        "version": "3.0.0",
        "architecture": "Agent Brain",
        "patients_in_memory": len(IN_MEMORY_DB),
        "apis_configured": {
            "gemini": bool(settings.gemini_api_key),
            "groq": bool(settings.groq_api_key),
            "elevenlabs": bool(settings.elevenlabs_api_key)
        }
    }


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    
    print("=" * 50)
    print("🧠 Janani AI - Omniscient Agent Architecture")
    print("=" * 50)
    print(f"📍 Base URL: http://localhost:{settings.port}")
    print(f"📚 API Docs: http://localhost:{settings.port}/docs")
    print(f"🧪 Agent Endpoint: POST /api/agent/chat")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
