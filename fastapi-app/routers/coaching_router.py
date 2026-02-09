from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path
from services.pose_analysis_service import pose_analysis_service
from services.coaching_service import coaching_service
from services.speech_service import speech_service
import json
import asyncio
import time

router = APIRouter(prefix="/ws/coaching", tags=["Coaching"])

@router.get("/demo", response_class=HTMLResponse)
async def get_demo_page():
    """Serve the Coaching Demo Page"""
    template_path = Path(__file__).parent.parent / "templates" / "coaching_demo.html"
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@router.websocket("/{user_id}")
async def coaching_websocket(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    # State Management
    history = []
    last_analysis_time = 0
    ANALYSIS_INTERVAL = 0.5  # 500ms throttling
    
    current_step = "Step 2: Uterine Massage" # Default/Mock for demo
    
    try:
        while True:
            # 1. Receive Landmarks
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            landmarks = payload.get("landmarks", [])
            user_voice = payload.get("voice_text", "")
            
            # Maintain 10-frame history
            history.append(landmarks)
            if len(history) > 10:
                history.pop(0)
            
            # 2. Throttling Logic
            now = time.time()
            if now - last_analysis_time < ANALYSIS_INTERVAL and not user_voice:
                # If voice is present, we skip throttling to respond immediately
                continue
                
            last_analysis_time = now
            
            # 3. Vision Analysis (Phase 1)
            visual_desc = pose_analysis_service.get_visual_description(
                landmarks, 
                history
            )
            
            # Send debug info back to client immediately
            await websocket.send_json({
                "type": "debug",
                "visual_desc": visual_desc
            })
            
            # 4. DeepSeek Reasoning (Phase 2)
            # Only trigger if there's a significant event or voice input
            # For this demo, we trigger on the interval
            
            advice = await coaching_service.get_coaching_advice(
                step=current_step,
                visual_description=visual_desc,
                user_voice_text=user_voice
            )
            
            # 5. Audio Streaming (Phase 3)
            # Send text metadata first
            await websocket.send_json({
                "type": "advice",
                "text": advice["text"],
                "tone": advice["tone"]
            })
            
            # Determine audio settings based on tone
            stability = 0.35 if advice["tone"] == "urgent" else 0.5
            style = 0.25 if advice["tone"] == "urgent" else 0.0
            
            # Stream audio chunks
            async for chunk in speech_service.stream_elevenlabs_audio(
                advice["text"], 
                stability=stability, 
                style=style
            ):
                # Send binary audio frame
                await websocket.send_bytes(chunk)
                
            # End of audio stream signal
            await websocket.send_text("END_AUDIO")

    except WebSocketDisconnect:
        print(f"Client #{user_id} disconnected")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        try:
            await websocket.close()
        except:
            pass
