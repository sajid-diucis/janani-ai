from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import uuid
from datetime import datetime

from models import ChatMessageRequest, ChatMessageResponse
from services.ai_service import AIService
from services.speech_service import SpeechService
from services.emergency_service import EmergencyService
from services.who_guard_service import who_guard
from config import settings

router = APIRouter()
ai_service = AIService()
speech_service = SpeechService()
emergency_service = EmergencyService()

# In-memory conversation storage (use Redis/DB in production)
conversations = {}

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest, background_tasks: BackgroundTasks):
    """Send message to AI and get response"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get or create conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # 1. NEW: Get Patient Profile for Memory & Context
        user_id = request.user_context.get("user_id", "web_user") if request.user_context else "web_user"
        from routers.midwife_router import get_augmented_profile
        profile = get_augmented_profile(user_id)
        
        # Check for emergency keywords
        emergency_check = await emergency_service.check_emergency(request.message)
        
        # Get AI response with context and Memory Rule
        conversation_history = conversations[conversation_id]
        ai_response = await ai_service.get_response(
            message=request.message,
            conversation_history=conversation_history,
            is_emergency=emergency_check.is_emergency,
            user_context=profile.dict() if profile else request.user_context
        )
        
        # WHO Guard validation and annotation
        guard_result = who_guard.validate_response(ai_response)
        annotated_response = ai_response
        if not guard_result['valid']:
            # Prepend warning and guideline annotation
            annotated_response = (
                "⚠️ This response may not fully align with WHO guidelines.\n" +
                ai_response +
                "\n\nWHO Guideline(s):\n- " + "\n- ".join(guard_result['annotations'])
            )
        elif guard_result['annotations']:
            # Append guideline annotation
            annotated_response = ai_response + "\n\nWHO Guideline(s):\n- " + "\n- ".join(guard_result['annotations'])
        
        # Update conversation history
        conversations[conversation_id].extend([
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": annotated_response}
        ])
        
        # 2. NEW: Extract and Save Memory for the "Memory Rule"
        if profile:
            background_tasks.add_task(
                ai_service.extract_and_save_memory, 
                user_id, 
                request.message, 
                profile
            )
        
        # Keep only last 8 messages (4 exchanges)
        if len(conversations[conversation_id]) > 8:
            conversations[conversation_id] = conversations[conversation_id][-8:]
        
        # Generate audio response in background
        audio_url = None
        if annotated_response:
            # TODO: Generate audio and save to static folder
            # background_tasks.add_task(generate_audio_response, annotated_response, conversation_id)
            audio_url = f"/api/voice/speak"  # Will be handled by TTS endpoint
        
        return ChatMessageResponse(
            success=True,
            response=annotated_response,
            conversation_id=conversation_id,
            is_emergency=emergency_check.is_emergency,
            emergency_level=emergency_check.emergency_level,
            timestamp=datetime.now(),
            audio_url=audio_url
        )
        
    except Exception as e:
        return ChatMessageResponse(
            success=False,
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            is_emergency=False,
            timestamp=datetime.now(),
            error=str(e)
        )

@router.get("/history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Get conversation history"""
    return {
        "conversation_id": conversation_id,
        "messages": conversations.get(conversation_id, [])
    }

@router.delete("/history/{conversation_id}")
async def clear_conversation_history(conversation_id: str):
    """Clear conversation history"""
    if conversation_id in conversations:
        del conversations[conversation_id]
    return {"message": "Conversation history cleared"}