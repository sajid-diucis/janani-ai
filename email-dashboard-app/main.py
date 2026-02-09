import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

app = FastAPI(title="Doctor's Email Dashboard")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Templates
templates = Jinja2Templates(directory="templates")

# In-memory Email Store
class Email(BaseModel):
    id: str
    sender: str
    subject: str
    timestamp: str
    body: str # HTML content
    is_read: bool = False
    priority: str = "normal"
    attachments: List[str] = []

inbox: List[Email] = []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/api/receive-email")
async def receive_email(email_data: Dict[str, Any]):
    try:
        new_email = Email(
            id=f"msg_{len(inbox) + 1}_{int(datetime.now().timestamp())}",
            sender=email_data.get("sender", "Janani AI System"),
            subject=email_data.get("subject", "New Patient Report"),
            timestamp=datetime.now().strftime("%I:%M %p"),
            body=email_data.get("body", "<p>No content</p>"),
            priority=email_data.get("priority", "normal"),
            is_read=False
        )
        inbox.insert(0, new_email) # Add to top
        return {"status": "received", "id": new_email.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inbox")
async def get_inbox():
    return inbox

@app.post("/api/inbox/{email_id}/read")
async def mark_read(email_id: str):
    for email in inbox:
        if email.id == email_id:
            email.is_read = True
            return {"status": "updated"}
    raise HTTPException(status_code=404, detail="Email not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8020, reload=True)
