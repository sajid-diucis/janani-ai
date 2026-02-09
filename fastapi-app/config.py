from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path

# Get the directory where config.py is located
BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Janani AI"
    app_version: str = "2.0.0"
    debug: bool = False

    # API Keys
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    gemini_base_url: str = Field(default="https://dev.onebrain.app/onebrain-api/v1", env="GEMINI_BASE_URL")
    gemini_model_id: str = "google/gemini-2.0-flash-exp:free"
    
    # OpenRouter API (Gemini)
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="google/gemini-2.0-flash-exp:free", env="OPENROUTER_MODEL")

    # Hugging Face Configuration
    hf_token: Optional[str] = None
    hf_image_model: str = "black-forest-labs/FLUX.1-dev"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # Service URLs
    dispatch_service_url: str = Field(default="http://127.0.0.1:8010", env="DISPATCH_SERVICE_URL")
    medimail_service_url: str = Field(default="http://127.0.0.1:8020", env="MEDIMAIL_SERVICE_URL")

    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_audio_types: list = ["audio/wav", "audio/mp3", "audio/m4a", "audio/ogg"]
    allowed_image_types: list = ["image/jpeg", "image/png", "image/jpg", "image/webp"]

    # Speech Configuration
    speech_recognition_language: str = "bn-BD"
    tts_language: str = "bn"

    # Emergency Keywords (Bengali)
    emergency_keywords: list = [
        "রকতপত", "রকতসরব", "খপস", "তবর বযথ",
        "জবর", "অজঞন", "শবসকষট", "বম", "মথবযথ"
    ]

    # ElevenLabs
    elevenlabs_api_key: Optional[str] = Field(None, env="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str = Field("cgSgspJ2msm6clMCkdW9", env="ELEVENLABS_VOICE_ID")
    elevenlabs_model_id: str = Field("eleven_multilingual_v2", env="ELEVENLABS_MODEL_ID")

    class Config:
        env_file = str(BASE_DIR / ".env")
        case_sensitive = False

# Global settings instance
settings = Settings()
