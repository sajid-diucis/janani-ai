import requests
import json

BASE_URL = "http://localhost:8000"

def verify_appointment_flow():
    print("\n🕵️ MANUAL VERIFY: Appointment Flow")
    print("-----------------------------------")
    payload = {
        "user_id": "manual_tester",
        "input_text": "I want to book an appointment at Hatirjheel for tomorrow",
        "include_history": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/midwife/triage", json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Check tool execution
        tool_executed = data.get("tool_executed") or data.get("data", {}).get("tool_executed")
        tool_data = data.get("tool_data") or data.get("data", {}).get("tool_data")
        
        print(f"Input: {payload['input_text']}")
        print(f"Tool Executed: {tool_executed}")
        
        if tool_executed == "EXECUTE_EXTERNAL_TASK":
            print("✅ Tool Detection: SUCCESS")
            # Check detailed result
            if tool_data and tool_data.get("status") == "success":
                res = tool_data.get("result", {})
                print(f"✅ Agent Execution: SUCCESS")
                print(f"   - Booking ID: {res.get('booking_id')}")
            else:
                print(f"❌ Agent Execution: FAILED")
                print(f"   - Tool Data: {tool_data}")
                print(f"   - Full Response Message: {data.get('message')}")
        else:
            print(f"❌ Tool Detection: FAILED (Got {tool_executed})")
            
    except Exception as e:
        print(f"❌ Request Failed: {e}")

def verify_emergency_flow():
    print("\n🕵️ MANUAL VERIFY: Emergency Flow")
    print("--------------------------------")
    # Note: Triage endpoint might not trigger TRIGGER_EMERGENCY directly if logic is in voice.py
    # But let's try the keyword "unconscious" which should hit ACTIVATE_EMERGENCY
    payload = {
        "user_id": "manual_tester",
        "input_text": "Help patient is unconscious at Hatirjheel",
        "include_history": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/midwife/triage", json=payload)
        response.raise_for_status()
        data = response.json()
        
        tool_executed = data.get("tool_executed") or data.get("data", {}).get("tool_executed")
        # In emergency tool, we don't return the agent result to frontend, 
        # we strictly return the redirect. But we can check if emergency was activated.
        
        print(f"Input: {payload['input_text']}")
        print(f"Tool Executed: {tool_executed}")
        
        if tool_executed == "ACTIVATE_EMERGENCY":
             print("✅ Emergency Detection: SUCCESS")
             # We rely on logs for the physical call side effect
             print("ℹ️ Check 'run_agent.py' logs for 'calling ambulance' message.")
        else:
             print(f"❌ Emergency Detection: FAILED (Got {tool_executed})")

    except Exception as e:
        print(f"❌ Request Failed: {e}")

if __name__ == "__main__":
    verify_appointment_flow()
    verify_emergency_flow()
