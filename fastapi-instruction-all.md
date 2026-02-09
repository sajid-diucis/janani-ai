# 🏥 Janani AI - Full System Architecture & Instructions

This document provides a deep scan of the system components, their locations, ports, and opening structures.

## 🏗️ System Overview

Janani AI is a multi-service application consisting of a FastAPI backend, an Execution Agent, and a modern Next.js frontend.

---

## 1. 🚀 Backend: FastAPI Main Application
The central "brain" of Janani AI, handling AI logic, patient state management, and legacy API routes.

- **Location**: `fastapi-app/`
- **Entry Point**: [`main.py`](file:///c:/Users/User/Documents/buildathon/Janani/fastapi-app/main.py)
- **Primary Port**: `8000`
- **Docs**: `http://localhost:8000/docs`
- **How to Start**:
  ```bash
  cd fastapi-app
  python main.py
  ```
- **Key Directories**:
  - `routers/`: API endpoints (voice, chat, vision, etc.)
  - `services/`: Core logic (AI Agent, Speech, Triage, etc.)
  - `static/`: Static assets and served frontend build.
  - `models/`: Pydantic data models.

---

## 2. ⚡ Execution Agent
A secondary service handling specialized execution tasks.

- **Location**: `execution_agent/`
- **Entry Point**: [`run_agent.py`](file:///c:/Users/User/Documents/buildathon/Janani/execution_agent/run_agent.py)
- **Primary Port**: `8001`
- **How to Start**:
  ```bash
  cd execution_agent
  python run_agent.py
  ```
- **Note**: You might have seen references to `80001` - this is likely a combination of ports 8000 and 8001.

---

## 3. 🎨 Frontend: Next.js Web App
The user interface built with React and Next.js.

- **Location**: `frontend/`
- **Primary Port**: `3000` (Dev Mode)
- **How to Start**:
  ```bash
  cd frontend
  npm run dev
  ```
- **Build Output**: When built (`npm run build`), the static files are often copied to `fastapi-app/static/` to be served directly by FastAPI.

---

## 📂 File Map & Locations

| Component | Path | Description |
|-----------|------|-------------|
| **API Entry** | `fastapi-app/main.py` | FastAPI app initialization & routes |
| **Config** | `fastapi-app/config.py` | Environment & API settings |
| **Env Variables** | `fastapi-app/.env` | Secrets and API keys |
| **AI Brain** | `fastapi-app/services/ai_agent.py` | Omniscient Agent logic |
| **Patient State** | `fastapi-app/services/patient_state.py` | Memory & record management |
| **Demo Toggles** | `fastapi-app/config_demo.py` | Speed/Balanced/Full mode settings |
| **Exec Agent** | `execution_agent/main.py` | Core execution agent logic |
| **Frontend UI** | `frontend/app/` | Next.js App Router components |

---

## 🛠️ Connectivity & Integration

### API Flow
1. **Frontend (3000)** calls **FastAPI (8000)** for AI chat, transcription, and health records.
2. **FastAPI (8000)** may use the **Execution Agent (8001)** for specific automated tasks.
3. **FastAPI (8000)** integrates with external providers:
   - **Gemini**: For complex medical reasoning.
   - **Groq**: For fast vision analysis and transcription.
   - **DeepSeek**: For general chat logic.
   - **ElevenLabs**: For high-quality Bengali TTS.

### Shared Access
- **Static Assets**: Shared via `fastapi-app/static/`.
- **Database**: Uses `fastapi-app/users.db` (SQLite) for persistent storage.

---

## 📝 Usage Tips
- **Switching Modes**: Use `python switch_mode.py` in `fastapi-app/` to toggle between **SPEED**, **BALANCED**, and **FULL** demo versions.
- **Health Check**: Visit `http://localhost:8000/health` to verify if the server and API keys are correctly configured.
- **Logs**: If something fails, check the terminal where `main.py` is running for detailed traceback.
