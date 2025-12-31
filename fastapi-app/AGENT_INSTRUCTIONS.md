# FastAPI Application - Agent Startup Instructions

This document provides clear, machine-readable instructions for any agent to open, run, and verify the Janani AI FastAPI application.

## 1. Project Root
- **Directory**: `fastapi-app/`
- **Entry Point**: `main.py`
- **Configuration**: `config.py` (reads from `.env`)

## 2. Prerequisites
- **Python**: 3.10+ recommended
- **Environment**: Creating a virtual environment is best practice.

## 3. Setup Instructions

### Step 3.1: Install Dependencies
Run the following command in the `fastapi-app/` directory:
```bash
pip install -r requirements.txt
```

### Step 3.2: Environment Configuration
Ensure a `.env` file exists in the `fastapi-app/` directory with the following keys (see `.env.example`):
```ini
DEEPSEEK_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```
*Note: The app will start without these keys but AI features will be disabled/warned.*

## 4. Run Application
Start the server using the python executable directly to ensure path resolution works as designed in `main.py`:

```bash
python main.py
```

*Note: The application uses `uvicorn` internally but `python main.py` ensures the working directory is correctly set.*

## 5. Verification
- **Success Signal**: Look for `Application startup complete.` in the console output.
- **Local URL**: http://127.0.0.1:8000
- **Docs URL**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## 6. Directory Structure Overview
- `main.py`: Server entry point
- `routers/`: API route definitions
- `services/`: Business logic and AI services
- `templates/`: Jinja2 HTML templates
- `static/`: CSS, JS, and images
- `models/`: Pydantic data models
