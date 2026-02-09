from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Add CORS for cross-origin requests from Port 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-Memory State ---
active_call = {
    "status": "IDLE",  # IDLE, RINGING, CONNECTED, ENDED
    "patient_name": None,
    "address": None,
    "condition": None
}

class CallRequest(BaseModel):
    patient_name: str
    address: str
    condition: str

# --- API Endpoints ---

@app.post("/api/incoming-call")
async def incoming_call(request: CallRequest):
    """Trigger an incoming call with patient details."""
    active_call["status"] = "RINGING"
    active_call["patient_name"] = request.patient_name
    active_call["address"] = request.address
    active_call["condition"] = request.condition
    return {"status": "success", "message": "Call started"}

@app.get("/api/call-status")
async def get_call_status():
    """Poll this endpoint to get current call state."""
    return active_call

@app.post("/api/accept-call")
async def accept_call():
    """Accept the call (Operator picks up)."""
    if active_call["status"] == "RINGING":
        active_call["status"] = "CONNECTED"
    return active_call

@app.post("/api/end-call")
async def end_call():
    """End the call."""
    active_call["status"] = "ENDED"
    # Reset details after a short delay in a real app, but here we keep them briefly
    return active_call

@app.post("/api/reset")
async def reset_call():
    """Reset to IDLE state."""
    active_call["status"] = "IDLE"
    active_call["patient_name"] = None
    active_call["address"] = None
    active_call["condition"] = None
    return active_call

# --- Frontend UI ---

@app.get("/", response_class=HTMLResponse)
async def phone_call_ui():
    return """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Emergency Dispatch (999)</title>
      <style>
        :root {
          color-scheme: dark;
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          min-height: 100vh;
          display: grid;
          place-items: center;
          background: radial-gradient(circle at top, #301b1b, #170b0b 60%);
          font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
          color: #f5f5f5;
        }
        .phone {
          width: min(360px, 92vw);
          aspect-ratio: 9 / 19.5;
          border-radius: 36px;
          background: linear-gradient(160deg, #361b1b, #200e0e 60%);
          padding: 28px 20px 30px;
          position: relative;
          overflow: hidden;
          box-shadow: 0 30px 80px rgba(0,0,0,0.55);
          border: 1px solid rgba(255,50,50,0.2);
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .status-bar {
          width: 100%;
          text-align: center;
          font-size: 0.95rem;
          letter-spacing: 0.12rem;
          text-transform: uppercase;
          color: #ff9b9b;
          font-weight: 800;
          margin-bottom: 20px;
        }
        .caller-info {
          text-align: center;
          width: 100%;
          flex-grow: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .caller-id {
          font-size: 2.5rem;
          font-weight: 900;
          color: #ff4b4b;
          margin: 0;
          line-height: 1.1;
        }
        .caller-subtitle {
          color: #eda6a6;
          font-size: 1.1rem;
          font-weight: 500;
          margin-top: 8px;
        }
        .patient-card {
            background: rgba(255, 50, 50, 0.15);
            border: 1px solid rgba(255, 100, 100, 0.3);
            border-radius: 12px;
            padding: 15px;
            margin-top: 20px;
            width: 100%;
            text-align: left;
            display: none; /* Hidden by default */
        }
        .patient-card h3 {
            margin: 0 0 5px 0;
            color: #ff9b9b;
            font-size: 0.9rem;
            text-transform: uppercase;
        }
        .patient-card p {
            margin: 0 0 10px 0;
            font-size: 0.95rem;
            line-height: 1.4;
        }
        .patient-card p:last-child {
            margin-bottom: 0;
        }
        
        .avatar-container {
          width: 140px;
          height: 140px;
          margin: 20px 0;
          border-radius: 50%;
          background: radial-gradient(circle at 30% 20%, #ff4e4e, #d32f2f 55%, #4f2323 70%);
          position: relative;
          box-shadow: 0 0 0 6px rgba(255, 78, 78, 0.12), 0 0 30px rgba(255, 78, 78, 0.4);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 3rem;
        }
        .ring {
          position: absolute;
          inset: -18px;
          border-radius: 50%;
          border: 2px solid rgba(255, 78, 78, 0.5);
          animation: pulse 1.0s ease-in-out infinite;
          opacity: 0; /* Hidden when not ringing */
        }
        .ring:nth-child(2) { animation-delay: 0.25s; }
        .ring:nth-child(3) { animation-delay: 0.5s; }
        
        .ringing .ring { opacity: 1; }
        
        @keyframes pulse {
          0% { transform: scale(0.75); opacity: 0.9; }
          80% { transform: scale(1.15); opacity: 0; }
          100% { opacity: 0; }
        }

        .ticker {
          margin-top: 10px;
          font-size: 1.2rem;
          color: #ffd166;
          letter-spacing: 0.08rem;
          font-weight: 700;
          height: 30px;
        }
        .ringing .ticker { animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.5; } }

        .call-actions {
          margin-top: auto;
          margin-bottom: 20px;
          display: flex;
          justify-content: center;
          gap: 20px;
          width: 100%;
        }
        .btn {
          width: 70px;
          height: 70px;
          border: none;
          border-radius: 50%;
          font-size: 1.5rem;
          color: #fff;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.2s;
        }
        .btn:active { transform: scale(0.95); }
        
        .decline {
          background: #ff4b4b;
          box-shadow: 0 5px 15px rgba(255,75,75,0.35);
        }
        .accept {
          background: #33d17a;
          box-shadow: 0 5px 15px rgba(51,209,122,0.35);
        }
        .ringing .accept {
            width: 80px;
            height: 80px;
            animation: shake 1.5s infinite;
        }
        @keyframes shake {
          0%, 100% { transform: rotate(0deg); }
          10%, 30%, 50%, 70%, 90% { transform: rotate(-5deg); }
          20%, 40%, 60%, 80% { transform: rotate(5deg); }
        }

        .footer {
          text-align: center;
          color: #8a93a4;
          font-size: 0.85rem;
          margin-bottom: 10px;
        }
        
        /* State Classes */
        .state-idle .avatar-container { filter: grayscale(1); opacity: 0.5; }
        .state-idle .ticker { display: none; }
        .state-idle .call-actions { display: none; }
        
        .state-connected .avatar-container { border-color: #33d17a; box-shadow: 0 0 30px rgba(51,209,122,0.3); background: radial-gradient(circle at 30% 20%, #33d17a, #1a9b5b 70%); }
        .state-connected .ring { display: none; }
        .state-connected .accept { display: none; }
        .state-connected .decline { width: 100%; border-radius: 12px; height: 50px; background: #ff4b4b; }
        .state-connected .ticker { color: #33d17a; }

      </style>
    </head>
    <body>
      <div class="phone" id="phoneBody">
        <div class="status-bar" id="statusBar">Emergency Dispatch</div>
        
        <div class="caller-info">
          <h1 class="caller-id" id="callerId">999</h1>
          <p class="caller-subtitle" id="callerSubtitle">Emergency Services</p>
          
          <div class="patient-card" id="patientCard">
             <h3>Incoming Patient Data</h3>
             <p><strong>Name:</strong> <span id="pName">--</span></p>
             <p><strong>Location:</strong> <span id="pAddr">--</span></p>
             <p><strong>Condition:</strong> <span id="pCond">--</span></p>
          </div>

          <div class="avatar-container">
            🚑
            <div class="ring"></div>
            <div class="ring"></div>
            <div class="ring"></div>
          </div>
          
          <div class="ticker" id="callTicker">CONNECTING...</div>
        </div>

        <div class="call-actions" id="actionButtons">
          <button class="btn decline" onclick="endCall()">✖</button>
          <button class="btn accept" onclick="acceptCall()">📞</button>
        </div>
        
        <div class="footer" id="footerText">System Ready</div>
      </div>

      <script>
        let currentStatus = "IDLE";

        async function pollStatus() {
            try {
                const res = await fetch('/api/call-status');
                const data = await res.json();
                updateUI(data);
            } catch (e) {
                console.error("Polling error", e);
            }
        }

        function updateUI(data) {
            const phone = document.getElementById('phoneBody');
            const callerId = document.getElementById('callerId');
            const subtitle = document.getElementById('callerSubtitle');
            const ticker = document.getElementById('callTicker');
            const patientCard = document.getElementById('patientCard');
            const footer = document.getElementById('footerText');
            
            // Avoid re-rendering if nothing changed (optional optimization, but simple reset is fine)
            
            // Remove all state classes
            phone.classList.remove('state-idle', 'state-connected', 'ringing');

            if (data.status === 'IDLE') {
                phone.classList.add('state-idle');
                callerId.innerText = "999";
                subtitle.innerText = "Emergency Services";
                patientCard.style.display = 'none';
                footer.innerText = "Waiting for calls...";
            } 
            else if (data.status === 'RINGING') {
                phone.classList.add('ringing');
                callerId.innerText = "INCOMING ALERT";
                subtitle.innerText = "Janani AI Referral";
                ticker.innerText = "SOS CALLING...";
                footer.innerText = "Swipe to answer";
                
                // Show Patient Data
                patientCard.style.display = 'block';
                document.getElementById('pName').innerText = data.patient_name || 'Unknown';
                document.getElementById('pAddr').innerText = data.address || 'Unknown';
                document.getElementById('pCond').innerText = data.condition || 'Unknown';
            }
            else if (data.status === 'CONNECTED') {
                phone.classList.add('state-connected');
                callerId.innerText = data.patient_name;
                subtitle.innerText = "Live Call Active";
                ticker.innerText = "00:01"; // Mock timer
                footer.innerText = "Secure Line Established";
                patientCard.style.display = 'block';
            }
        }

        async function acceptCall() {
            await fetch('/api/accept-call', { method: 'POST' });
        }

        async function endCall() {
            await fetch('/api/reset', { method: 'POST' }); // Reset to IDLE for demo loop
        }

        // Poll every 1 second
        setInterval(pollStatus, 1000);
        
        // Initial check
        pollStatus();
      </script>
    </body>
    </html>
    """
