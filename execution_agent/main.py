from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import os

app = FastAPI(title="Janani Execution Agent", version="1.0.0")

class AgentTask(BaseModel):
    task_type: str  # "appointment", "emergency_call"
    parameters: Dict[str, Any]

@app.get("/health")
async def health_check():
    return {"status": "online", "service": "Janani Execution Agent"}

@app.post("/execute")
async def execute_task(task: AgentTask):
    """
    Execute a task requested by the main Janani app.
    This is the "Brain" -> "Hand" interface.
    """
    print(f"🤖 AGENT RECEIVED TASK: {task.task_type} with params: {task.parameters}")
    
    if task.task_type == "appointment":
        # Import dynamically to avoid circular issues
        from execution_agent.skills import book_appointment
        
        try:
            result = book_appointment(task.parameters)
            return {
                "status": "success", 
                "message": f"Appointment confirmed for {result['hospital']['name']}",
                "result": result
            }
        except Exception as e:
            return {"status": "error", "message": f"Booking failed: {str(e)}"}
    
    elif task.task_type == "emergency_call":
        from execution_agent.skills import call_ambulance
        
        try:
            result = call_ambulance(task.parameters)
            return {
                "status": "success",
                "message": "Emergency call initiated",
                "result": result
            }
        except Exception as e:
            return {"status": "error", "message": f"Emergency call failed: {str(e)}"}
        
    else:
        raise HTTPException(status_code=400, detail=f"Unknown task type: {task.task_type}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
