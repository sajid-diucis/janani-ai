from fastapi import APIRouter, HTTPException, status
from models.auth_models import UserLogin, UserRegister, Token, UserProfile
import sqlite3
import hashlib
import uuid
from pathlib import Path

# Create a simple router
router = APIRouter(prefix="/api/auth", tags=["auth"])

# Setup SQLite DB path
DB_PATH = Path("users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            phone TEXT UNIQUE NOT NULL,
            pin_hash TEXT NOT NULL,
            name TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on import (simple approach for this script)
init_db()

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

@router.post("/register", response_model=Token)
async def register(user: UserRegister):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        user_id = str(uuid.uuid4())
        pin_hash = hash_pin(user.pin)
        
        cursor.execute(
            "INSERT INTO users (id, phone, pin_hash, name) VALUES (?, ?, ?, ?)",
            (user_id, user.phone, pin_hash, user.name)
        )
        conn.commit()
        
        return {
            "access_token": user_id, # In a real app this would be a JWT
            "token_type": "bearer",
            "user_id": user_id,
            "name": user.name
        }
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    finally:
        conn.close()

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    pin_hash = hash_pin(user.pin)
    
    cursor.execute(
        "SELECT id, name FROM users WHERE phone = ? AND pin_hash = ?",
        (user.phone, pin_hash)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result:
        user_id, name = result
        return {
            "access_token": user_id, # Simplified token
            "token_type": "bearer",
            "user_id": user_id,
            "name": name
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid phone or PIN")

@router.get("/me")
async def get_current_user(token: str): # Simplified, usually header injection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, phone, name FROM users WHERE id = ?", (token,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {"id": result[0], "phone": result[1], "name": result[2]}
    raise HTTPException(status_code=401, detail="Invalid token")
