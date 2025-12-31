from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

from config import settings
from routers import voice, chat, vision, emergency, food, food_rag
from routers import recommendation_router, document_router, midwife_router
from routers import ar_labor_router, auth

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Digital Midwife - Bengali Maternal Health OS with WHO Guidelines",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

print(f"DEBUG: ELEVENLABS KEY: {settings.elevenlabs_api_key}")

# CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates - use absolute paths
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/_next", StaticFiles(directory=str(BASE_DIR / "static" / "_next")), name="next")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Include routers
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(vision.router, prefix="/api/vision", tags=["vision"])
app.include_router(emergency.router, prefix="/api/emergency", tags=["emergency"])
app.include_router(food.router, tags=["food"])
app.include_router(food_rag.router, tags=["food-rag"])
app.include_router(recommendation_router.router, tags=["recommendations"])
app.include_router(document_router.router, tags=["profile-documents"])
app.include_router(auth.router)

# Digital Midwife Core Modules
app.include_router(midwife_router.router, tags=["digital-midwife"])

# AR Emergency Labor Assistant (Offline-First)
app.include_router(ar_labor_router.router, tags=["ar-labor-assistant"])

@app.get("/")
async def home(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": settings.app_name
    })

from fastapi.responses import FileResponse
@app.get("/offline_rules.json")
async def offline_rules():
    """Serve offline rules for the frontend"""
    # Ensure the file exists
    path = BASE_DIR / "static" / "offline_rules.json"
    if not path.exists():
         # Fallback if not in static, try looking in root static (rare case)
         return {"error": "File not found"}
    return FileResponse(str(path))

@app.get("/ar-dashboard")
async def ar_dashboard_page(request: Request):
    """Serve the AR Emergency Dashboard with MediaPipe WASM integration"""
    return templates.TemplateResponse("ar_dashboard.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "apis_configured": {
            "deepseek": bool(settings.deepseek_api_key),
            "groq": bool(settings.groq_api_key),
            "elevenlabs": bool(settings.elevenlabs_api_key)
        }
    }

if __name__ == "__main__":
    # Change to the app directory for proper module resolution
    os.chdir(BASE_DIR)
    
    # Check for required API keys
    if not settings.deepseek_api_key or not settings.groq_api_key:
        print("Warning: API keys not configured!")
        print("Please set DEEPSEEK_API_KEY and GROQ_API_KEY in .env file")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
