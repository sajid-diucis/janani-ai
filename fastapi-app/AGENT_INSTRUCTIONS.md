# FastAPI Application - Agent Startup Instructions

This document provides clear, machine-readable instructions for any agent to open, run, and verify the Janani AI FastAPI application.

## 1. Project Root
- **Directory**: `fastapi-app/`
- **Entry Point**: `main.py`
- **Configuration**: `config.py` (reads from `.env`)

## 2. Prerequisites
- **Python**: 3.10+ recommended
- **Environment**: Creating a virtual environment is best practice.

## 3. Server Environment Context (CRITICAL)
This application supports two distinct environments. Agents must match their actions to the active environment.

### 3.1 Windows (Local Development)
- **Status**: Default for local testing.
- **SQLite**: Uses the system's standard `sqlite3` library.
- **Dependencies**: `pysqlite3-binary` is **NOT** installed (skipped via `sys_platform` check).
- **Run Command**: `python main.py`

### 3.2 Linux (Cloud / Render)
- **Status**: Used for production deployment.
- **SQLite**: REQUIRES `pysqlite3-binary` to support ChromaDB (older system SQLite versions often fail).
- **Dependencies**: `pysqlite3-binary` is **AUTOMATICALLY** installed via `requirements.txt`.
- **Run Command**: `python main.py` (The code automatically detects `pysqlite3` and swaps it for `sqlite3`).

> [!IMPORTANT]
> Do NOT attempt to force install `pysqlite3-binary` on Windows. It will fail.
> Do NOT remove the `try-except` block for `pysqlite3` in `main.py`. It is the bridge between these two environments.

## 4. Setup Instructions

### Step 4.1: Install Dependencies
Run the following command in the `fastapi-app/` directory:
```bash
pip install -r requirements.txt
```

### Step 4.2: Environment Configuration
Ensure a `.env` file exists in the `fastapi-app/` directory with the following keys (see `.env.example`):
```ini
DEEPSEEK_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```
*Note: The app will start without these keys but AI features will be disabled/warned.*

## 5. Run Application
Start the server using the python executable directly to ensure path resolution works as designed in `main.py`:

```bash
python main.py
```

*Note: The application uses `uvicorn` internally but `python main.py` ensures the working directory is correctly set.*

## 6. Verification
- **Success Signal**: Look for `Application startup complete.` in the console output.
- **Local URL**: http://127.0.0.1:8000
- **Docs URL**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## 7. Directory Structure Overview
- `main.py`: Server entry point
- `routers/`: API route definitions
- `services/`: Business logic and AI services
- `templates/`: Jinja2 HTML templates
- `static/`: CSS, JS, and images
- `models/`: Pydantic data models
