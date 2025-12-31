# 🚀 Janani AI: Streamlit to FastAPI Migration Checklist

## 📊 Current App Analysis
- **Current Framework**: Streamlit
- **Total Lines**: 480 lines
- **Core Features**:
  - Voice Chat (Bengali Speech-to-Text + Text-to-Speech)
  - Emergency Warning System
  - Prescription Analysis (Image OCR)
  - Food Analysis (Image Recognition)
- **APIs Used**: DeepSeek, Groq, Google Speech Recognition, gTTS

---

## 🎯 Migration Strategy

### Phase 1: Backend API Development (FastAPI)
- [ ] **1.1 Project Structure Setup**
  - [ ] Create `main.py` for FastAPI app
  - [ ] Create `routers/` directory for API endpoints
  - [ ] Create `models/` directory for Pydantic models
  - [ ] Create `services/` directory for business logic
  - [ ] Create `utils/` directory for helper functions
  - [ ] Create `static/` directory for frontend assets
  - [ ] Create `templates/` directory for HTML templates

- [ ] **1.2 Dependencies & Requirements**
  - [ ] Add FastAPI to requirements.txt
  - [ ] Add uvicorn for ASGI server
  - [ ] Add python-multipart for file uploads
  - [ ] Add jinja2 for HTML templating (if needed)
  - [ ] Keep existing: openai, gtts, SpeechRecognition, Pillow, python-dotenv

- [ ] **1.3 Configuration Management**
  - [ ] Create `config.py` for settings management
  - [ ] Use Pydantic Settings for environment variables
  - [ ] Migrate API key management from Streamlit secrets

### Phase 2: API Endpoints Design

- [ ] **2.1 Voice Chat API**
  - [ ] `POST /api/voice/upload` - Upload audio file
  - [ ] `POST /api/voice/transcribe` - Convert speech to text
  - [ ] `POST /api/chat/message` - Send text message to AI
  - [ ] `GET /api/voice/speak/{text}` - Convert text to Bengali speech
  - [ ] Handle audio file formats (WAV, MP3, etc.)

- [ ] **2.2 Emergency Warning API**
  - [ ] `POST /api/emergency/check` - Check for emergency keywords
  - [ ] `GET /api/emergency/alerts` - Get emergency alert messages
  - [ ] Implement keyword detection logic

- [ ] **2.3 Image Analysis APIs**
  - [ ] `POST /api/prescription/analyze` - Analyze prescription image
  - [ ] `POST /api/food/analyze` - Analyze food image
  - [ ] Handle image upload and base64 encoding
  - [ ] Integrate with Groq Vision API

- [ ] **2.4 Health & Utility APIs**
  - [ ] `GET /api/health` - Health check endpoint
  - [ ] `GET /api/guidelines` - Get health guidelines
  - [ ] `POST /api/conversation/history` - Manage chat history

### Phase 3: Data Models (Pydantic)

- [ ] **3.1 Request Models**
  - [ ] `VoiceUploadRequest` - Audio file upload
  - [ ] `ChatMessageRequest` - Text chat message
  - [ ] `ImageAnalysisRequest` - Image upload for analysis
  - [ ] `EmergencyCheckRequest` - Emergency keyword check

- [ ] **3.2 Response Models**
  - [ ] `VoiceTranscriptionResponse` - Transcribed text
  - [ ] `ChatMessageResponse` - AI response with emergency flag
  - [ ] `PrescriptionAnalysisResponse` - Medicine analysis results
  - [ ] `FoodAnalysisResponse` - Food safety analysis
  - [ ] `EmergencyAlertResponse` - Emergency alert details

### Phase 4: Service Layer Migration

- [ ] **4.1 AI Service (`services/ai_service.py`)**
  - [ ] Migrate DeepSeek chat functionality
  - [ ] Implement conversation context management
  - [ ] Add emergency keyword detection logic
  - [ ] Create system prompt management

- [ ] **4.2 Speech Service (`services/speech_service.py`)**
  - [ ] Migrate Google Speech Recognition
  - [ ] Migrate gTTS functionality
  - [ ] Handle audio file processing
  - [ ] Add error handling for speech APIs

- [ ] **4.3 Vision Service (`services/vision_service.py`)**
  - [ ] Migrate Groq Vision API integration
  - [ ] Handle prescription OCR
  - [ ] Handle food image recognition
  - [ ] Add image preprocessing utilities

- [ ] **4.4 Health Guidelines Service (`services/guidelines_service.py`)**
  - [ ] Migrate health guidelines loading
  - [ ] Create guideline search functionality
  - [ ] Implement RAG context injection

### Phase 5: Frontend Options

#### Option A: Pure API (Recommended for mobile app integration)
- [ ] **5A.1 API Documentation**
  - [ ] Auto-generate OpenAPI/Swagger docs
  - [ ] Add comprehensive API examples
  - [ ] Create postman collection

#### Option B: Simple Web Frontend
- [ ] **5B.1 HTML Templates**
  - [ ] Create `index.html` with voice recorder
  - [ ] Create prescription upload interface
  - [ ] Create food analysis interface
  - [ ] Add Bengali language support

- [ ] **5B.2 JavaScript Frontend**
  - [ ] Implement Web Audio API for recording
  - [ ] Create AJAX calls to FastAPI endpoints
  - [ ] Handle file uploads
  - [ ] Add real-time audio playback

### Phase 6: Advanced Features

- [ ] **6.1 Authentication & Security**
  - [ ] Add API key authentication
  - [ ] Implement rate limiting
  - [ ] Add CORS configuration
  - [ ] Input validation and sanitization

- [ ] **6.2 Database Integration (Optional)**
  - [ ] Add SQLite/PostgreSQL for conversation history
  - [ ] User session management
  - [ ] Analytics and usage tracking

- [ ] **6.3 Performance Optimization**
  - [ ] Add Redis for caching
  - [ ] Implement async processing for long tasks
  - [ ] Add request/response compression
  - [ ] Background tasks for audio processing

- [ ] **6.4 Error Handling & Monitoring**
  - [ ] Comprehensive error handling
  - [ ] Logging configuration
  - [ ] Health check endpoints
  - [ ] Request validation

### Phase 7: Testing & Deployment

- [ ] **7.1 Testing**
  - [ ] Unit tests for services
  - [ ] API endpoint testing
  - [ ] Integration tests with external APIs
  - [ ] Load testing for audio/image processing

- [ ] **7.2 Docker Containerization**
  - [ ] Create Dockerfile
  - [ ] Docker-compose for development
  - [ ] Environment variable management

- [ ] **7.3 Deployment Options**
  - [ ] Local development setup
  - [ ] Railway/Render deployment
  - [ ] AWS/Google Cloud deployment
  - [ ] Kubernetes manifests (if needed)

---

## 📁 New Project Structure
```
janani-api/
├── main.py                 # FastAPI app entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── Dockerfile            # Docker configuration
├── routers/
│   ├── __init__.py
│   ├── voice.py          # Voice/speech endpoints
│   ├── chat.py           # Chat/AI endpoints
│   ├── vision.py         # Image analysis endpoints
│   └── emergency.py      # Emergency detection
├── models/
│   ├── __init__.py
│   ├── requests.py       # Request models
│   └── responses.py      # Response models
├── services/
│   ├── __init__.py
│   ├── ai_service.py     # DeepSeek integration
│   ├── speech_service.py # Speech processing
│   ├── vision_service.py # Image analysis
│   └── guidelines_service.py # Health guidelines
├── utils/
│   ├── __init__.py
│   ├── audio_utils.py    # Audio processing helpers
│   ├── image_utils.py    # Image processing helpers
│   └── emergency_utils.py # Emergency detection
├── static/               # Static files (if web frontend)
├── templates/           # HTML templates (if web frontend)
└── tests/
    ├── __init__.py
    ├── test_api.py      # API tests
    └── test_services.py # Service tests
```

---

## 🔧 Technical Decisions

### 1. **API vs Web App**
- **Recommendation**: Pure API first, web frontend optional
- **Reason**: Better for mobile app integration, scalability

### 2. **Audio Handling**
- **Approach**: File upload + processing endpoints
- **Formats**: Support WAV, MP3, M4A
- **Storage**: Temporary files, no persistent audio storage

### 3. **Image Processing**
- **Approach**: Base64 encoding or multipart upload
- **Validation**: File type, size limits
- **Processing**: Async for large images

### 4. **Session Management**
- **Approach**: Stateless API with conversation ID
- **Storage**: In-memory or Redis for development
- **History**: Optional database integration

---

## ⏱️ Estimated Timeline

- **Phase 1-2 (Setup + Basic APIs)**: 2-3 days
- **Phase 3-4 (Models + Services)**: 3-4 days  
- **Phase 5 (Frontend)**: 2-3 days (if web frontend)
- **Phase 6 (Advanced)**: 2-3 days
- **Phase 7 (Testing + Deployment)**: 1-2 days

**Total: 8-12 days**

---

## 🚀 Migration Benefits

1. **Better Mobile Integration**: APIs work with any frontend
2. **Scalability**: Handle multiple concurrent users
3. **Performance**: Async processing, better resource management
4. **Flexibility**: Separate frontend/backend development
5. **Production Ready**: Better error handling, monitoring
6. **Multi-Platform**: Can serve web, mobile, desktop apps

---

## 🎯 Next Steps

1. Review this checklist
2. Choose frontend approach (API-only vs Web)
3. Set up new project structure  
4. Start with Phase 1: Basic FastAPI setup
5. Migrate core voice chat functionality first
6. Add image analysis features
7. Implement emergency detection
8. Add frontend (if needed)
9. Deploy and test

---

Ready to start the migration? Let me know which approach you prefer!