"""
Voice Router with Health Check Integration
Provides voice transcription, text-to-speech, and context-aware health check.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
import tempfile, os, io, base64
from typing import Optional
from models import VoiceTranscriptionResponse, TextToSpeechRequest
from services.speech_service import SpeechService
from config import settings

router = APIRouter()
speech_service = SpeechService()


@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(None), audio: UploadFile = File(None)):
    """Basic audio transcription endpoint"""
    upload_file = file or audio
    if not upload_file:
        return VoiceTranscriptionResponse(success=False, error="No audio file provided")
    try:
        ext = ".webm" if "webm" in (upload_file.content_type or "") else ".wav"
        contents = await upload_file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as f:
            f.write(contents)
            temp_path = f.name
        try:
            transcription = await speech_service.transcribe_audio(temp_path)
            return VoiceTranscriptionResponse(
                success=True, 
                transcription=transcription, 
                language_detected=settings.speech_recognition_language, 
                confidence=1.0
            )
        finally:
            if os.path.exists(temp_path): 
                os.unlink(temp_path)
    except Exception as e:
        return VoiceTranscriptionResponse(success=False, error=str(e))


@router.post("/speak")
async def text_to_speech(request: TextToSpeechRequest):
    """Convert text to speech audio"""
    try:
        audio_data = await speech_service.text_to_speech(request.text, request.language)
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# VOICE HEALTH CHECK - Context-Aware AI Endpoint
# ============================================================

@router.post("/health-check")
async def voice_health_check(
    audio: UploadFile = File(None),
    file: UploadFile = File(None),
    user_id: str = Form(default="default_user")
):
    """
    🎤 Voice Health Check with FULL Patient Context
    
    This is the OMNISCIENT endpoint that:
    1. Transcribes user's voice input
    2. Retrieves COMPLETE patient history (emergencies, care plans, diet, documents)
    3. Sends to AI agent with full context
    4. Returns audio response
    
    The AI knows:
    - Past emergency situations
    - Current weekly care plan
    - Diet preferences and budget
    - Uploaded medical documents
    - Complete medical history
    """
    # Accept both 'audio' and 'file' field names
    upload_file = audio or file
    
    if not upload_file:
        return {
            "success": False,
            "error": "No audio file provided",
            "transcription": None,
            "response": None
        }
    
    temp_path = None
    try:
        # 1. Save uploaded audio to temp file
        ext = ".webm" if "webm" in (upload_file.content_type or "") else ".wav"
        contents = await upload_file.read()
        
        if len(contents) == 0:
            return {
                "success": False,
                "error": "Empty audio file",
                "transcription": None,
                "response": None
            }
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as f:
            f.write(contents)
            temp_path = f.name
        
        # 2. Transcribe audio
        transcription = await speech_service.transcribe_audio(temp_path)
        
        if not transcription or transcription == "Sorry, could not understand audio.":
            return {
                "success": False,
                "error": "Could not understand audio. Please speak clearly.",
                "transcription": transcription,
                "response": None
            }
        
        # 3. Get FULL patient context (NO circular import - using patient_data_service)
        # 3. Get initial patient context
        from services.patient_data_service import patient_data_service
        full_context = patient_data_service.get_full_context(user_id)
        
        # ============================================================
        # 4. AGENTIC TOOL EXECUTION (Draft 2: Execute BEFORE AI response)
        # ============================================================
        from services.agent_tools import detect_tool_from_query, execute_tool
        
        tool_executed = None
        tool_result = None
        tool_message = None
        
        # Detect intent from raw transcription
        tool_detected = detect_tool_from_query(transcription)
        
        if tool_detected:
            tool_name, tool_params = tool_detected
            tool_executed = tool_name
            print(f"🔧 Voice: Detected tool '{tool_name}' with params: {tool_params}")
            
            try:
                tool_message, tool_result = await execute_tool(
                    tool_name, 
                    tool_params, 
                    full_context
                )
                print(f"✅ Voice: Tool '{tool_name}' executed successfully")
                
                # CRITICAL: Reload context after tool execution to capture updates (e.g. Profile Update)
                if tool_name == "UPDATE_PROFILE":
                     print("🔄 Reloading context after profile update...")
                     full_context = patient_data_service.get_full_context(user_id)

            except Exception as tool_error:
                print(f"❌ Voice: Tool execution failed: {tool_error}")
                tool_message = " টুল চালাতে সমস্যা হয়েছে (" + str(tool_error) + ")"

        # 5. Call the omniscient AI agent (SKIP for emergency - show tool result only)
        from services.ai_agent import ask_janani_agent
        
        if tool_executed == "ACTIVATE_EMERGENCY":
            # [FIX 2] Skip AI call for emergency - user needs ACTION not conversation
            ai_response = tool_message or "🚑 জরুরি সেবা সক্রিয় হয়েছে! এম্বুলেন্স ডাকা হচ্ছে..."
        else:
            ai_response = await ask_janani_agent(
                query=transcription,
                state=full_context
            )
            
            # [FIX 1] PREPEND tool message (not append) so user sees action first
            if tool_message:
                ai_response = f"🤖 {tool_message}\n\n---\n{ai_response}"

        
        # 6. Generate audio response
        audio_response = None
        audio_base64 = None
        try:
            audio_response = await speech_service.text_to_speech(ai_response, language="bn")
            audio_base64 = base64.b64encode(audio_response).decode("utf-8")
        except Exception as tts_error:
            print(f"TTS failed (non-critical): {tts_error}")
            # Continue without audio - text response is more important
        
        # 7. Check if emergency was activated via tool
        emergency_activated = False
        emergency_redirect = None
        if tool_executed == "ACTIVATE_EMERGENCY" and tool_result:
            emergency_activated = tool_result.get("emergency_activated", False)
            emergency_redirect = tool_result.get("emergency_redirect", "http://localhost:8000/ar-dashboard")
        
        # 8. Return comprehensive response with tool results
        return {
            "success": True,
            "transcription": transcription,
            "response": ai_response,
            "audio_base64": audio_base64,
            # AGENTIC: Tool execution results
            "tool_executed": tool_executed,
            "tool_result": tool_result,
            # EMERGENCY: Redirect info for frontend
            "emergency_activated": emergency_activated,
            "emergency_redirect": emergency_redirect,
            # Context info
            "context_used": {
                "user_id": user_id,
                "weeks_pregnant": full_context.get("weeks_pregnant"),
                "conditions": full_context.get("conditions", []),
                "emergency_count": len(full_context.get("emergency_sessions", [])),
                "has_documents": len(full_context.get("uploaded_documents", [])) > 0,
                "emergency_summary": full_context.get("emergency_summary"),
                "care_plan_summary": full_context.get("care_plan_summary"),
                "diet_summary": full_context.get("diet_summary")
            }
        }
        
    except Exception as e:
        print(f"Voice health check error: {e}")
        return {
            "success": False,
            "error": str(e),
            "transcription": None,
            "response": None
        }
    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass