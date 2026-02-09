import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

AGENT_URL = "http://localhost:8001/execute"

async def delegate_to_agent(task_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delegates a task to the external Execution Agent running on port 8001.
    """
    payload = {
        "task_type": task_type,
        "parameters": params
    }
    
    print(f"🌉 BRIDGE: Delegating '{task_type}' to Agent at {AGENT_URL}...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(AGENT_URL, json=payload, timeout=10.0)
            
        if response.status_code == 200:
            result = response.json()
            print(f"✅ BRIDGE: Agent Success: {result}")
            return result
        else:
            error_msg = f"Agent returned status {response.status_code}: {response.text}"
            print(f"❌ BRIDGE: {error_msg}")
            return {"status": "error", "message": error_msg}
            
    except Exception as e:
        error_msg = f"Connection failed to Execution Agent: {str(e)}"
        print(f"❌ BRIDGE: {error_msg}")
        return {"status": "error", "message": error_msg}
