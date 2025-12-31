from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import tempfile, os, io
from models import VoiceTranscriptionResponse, TextToSpeechRequest
from services.speech_service import SpeechService
from config import settings

router = APIRouter()
speech_service = SpeechService()

@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(None), audio: UploadFile = File(None)):
    # Accept both 'file' and 'audio' field names for compatibility
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
            return VoiceTranscriptionResponse(success=True, transcription=transcription, language_detected=settings.speech_recognition_language, confidence=1.0)
        finally:
            if os.path.exists(temp_path): os.unlink(temp_path)
    except Exception as e:
        return VoiceTranscriptionResponse(success=False, error=str(e))

@router.post("/speak")
async def text_to_speech(request: TextToSpeechRequest):
    try:
        audio_data = await speech_service.text_to_speech(request.text, request.language)
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))