"""
Shared Patient State Module
Avoids circular imports by centralizing IN_MEMORY_DB here.
All routers and services should import from here, NOT from main.py.
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Persistence file path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PATIENT_STATE_FILE = os.path.join(DATA_DIR, "patient_states.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def _load_states() -> Dict[str, Dict[str, Any]]:
    """Load patient states from JSON file"""
    if os.path.exists(PATIENT_STATE_FILE):
        try:
            with open(PATIENT_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading patient states: {e}")
    return {}


def _save_states(states: Dict[str, Dict[str, Any]]):
    """Save patient states to JSON file"""
    try:
        with open(PATIENT_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(states, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving patient states: {e}")


# ============================================================
# IN-MEMORY DATABASE (Master JSON)
# This is the "Omniscient State" - The Agent knows everything
# ============================================================
# Load from persistent storage on startup
IN_MEMORY_DB: Dict[str, Dict[str, Any]] = _load_states()

# Demo patient for testing (only add if not already in persisted data)
if "user_123" not in IN_MEMORY_DB:
    IN_MEMORY_DB["user_123"] = {
        "user_id": "user_123",
        "name": "রাহিমা",
        "name_english": "Rahima",
        "age": 28,
        "weeks_pregnant": 34,
        "trimester": "third",
        "location": "নোয়াখালী",
        "blood_group": "O+",
        "risks": ["previous_anemia", "low_blood_pressure_history"],
        "conditions": ["mild_anemia"],
        "medical_history": [
            "Week 20: Mild Anemia detected (Hemoglobin 10.2)",
            "Week 28: History of low blood pressure episodes",
            "Week 32: Complained of occasional dizziness"
        ],
        "last_symptoms": ["ঝাপসা দেখা", "মাথা ব্যথা"],
        "recent_concerns": [
            "ঝাপসা দেখছি আজকে সকাল থেকে",
            "মাথা ব্যথা করছে"
        ],
        "blood_pressure": "140/95",
        "hemoglobin": 10.8,
        "last_checkup": "2026-01-05",
        "last_meal": "ভাত আর আলু ভর্তা",
        "emergency_contact": "স্বামী - করিম (01712345678)",
        # NEW: Historical data tracking
        "emergency_sessions": [],
        "care_plan_history": [],
        "food_preferences": {
            "dietary_restrictions": [],
            "budget": 500,
            "last_menu_generated": None
        },
        "uploaded_documents": []
    }
    _save_states(IN_MEMORY_DB)


def create_default_patient(user_id: str) -> Dict[str, Any]:
    """Create a new patient with default values including history fields"""
    return {
        "user_id": user_id,
        "name": "Unknown",
        "weeks_pregnant": 0,
        "trimester": "unknown",
        "age": 0,
        "risks": [],
        "conditions": [],
        "last_symptoms": [],
        "recent_concerns": [],
        "blood_pressure": None,
        "hemoglobin": None,
        "last_checkup": None,
        # Historical data tracking
        "emergency_sessions": [],
        "care_plan_history": [],
        "food_preferences": {
            "dietary_restrictions": [],
            "budget": 500,
            "last_menu_generated": None
        },
        "uploaded_documents": []
    }


def get_patient(user_id: str) -> Dict[str, Any]:
    """
    Get patient state by user_id.
    Creates a new patient if not found.
    """
    if user_id not in IN_MEMORY_DB:
        IN_MEMORY_DB[user_id] = create_default_patient(user_id)
        _save_states(IN_MEMORY_DB)
    return IN_MEMORY_DB[user_id]


def update_patient(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update patient state.
    Automatically persists changes to JSON file.
    """
    patient = get_patient(user_id)
    patient.update(updates)
    _save_states(IN_MEMORY_DB)
    return patient


def record_emergency(user_id: str, emergency_type: str, severity: str, actions_taken: List[str] = None):
    """
    Record an emergency event in patient's history.
    All events are remembered (as per user requirement).
    """
    patient = get_patient(user_id)
    if "emergency_sessions" not in patient:
        patient["emergency_sessions"] = []
    
    patient["emergency_sessions"].append({
        "timestamp": datetime.now().isoformat(),
        "type": emergency_type,
        "severity": severity,
        "actions_taken": actions_taken or []
    })
    _save_states(IN_MEMORY_DB)


def record_care_plan(user_id: str, week: int, plan_summary: Dict[str, Any]):
    """
    Record a generated care plan in patient's history.
    """
    patient = get_patient(user_id)
    if "care_plan_history" not in patient:
        patient["care_plan_history"] = []
    
    patient["care_plan_history"].append({
        "week": week,
        "generated_at": datetime.now().isoformat(),
        **plan_summary
    })
    _save_states(IN_MEMORY_DB)


def record_document_upload(user_id: str, filename: str, extracted_data: Dict[str, Any]):
    """
    Record an uploaded document in patient's history.
    """
    patient = get_patient(user_id)
    if "uploaded_documents" not in patient:
        patient["uploaded_documents"] = []
    
    patient["uploaded_documents"].append({
        "filename": filename,
        "uploaded_at": datetime.now().isoformat(),
        "extracted_data": extracted_data
    })
    _save_states(IN_MEMORY_DB)


def update_food_preferences(user_id: str, budget: int = None, restrictions: List[str] = None):
    """
    Update patient's food preferences.
    """
    patient = get_patient(user_id)
    if "food_preferences" not in patient:
        patient["food_preferences"] = {"dietary_restrictions": [], "budget": 500}
    
    if budget is not None:
        patient["food_preferences"]["budget"] = budget
    if restrictions is not None:
        patient["food_preferences"]["dietary_restrictions"] = restrictions
    patient["food_preferences"]["last_menu_generated"] = datetime.now().isoformat()
    
    _save_states(IN_MEMORY_DB)


def get_all_patients() -> Dict[str, Dict[str, Any]]:
    """Get all patient states (for debugging)"""
    return IN_MEMORY_DB
