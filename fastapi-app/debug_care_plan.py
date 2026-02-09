import asyncio
import sys
import os
import traceback
import json

sys.path.append(os.getcwd())

async def debug_care_plan():
    print("🔍 Debugging Care Plan Output...")
    try:
        from services.agent_tools import execute_tool
        
        profile = {
            "user_id": "debug_user",
            "name": "Debug Mom",
            "weeks_pregnant": 20,
            "conditions": []
        }
        
        print("▶️ Executing GET_CARE_PLAN...")
        message, data = await execute_tool("GET_CARE_PLAN", {"week": 20}, profile)
        
        print(f"✅ Message Length: {len(message)}")
        
        if data:
            print(f"✅ Data Keys: {list(data.keys())}")
            
            # Check critical fields
            print(f"👉 'week': {data.get('week')}")
            print(f"👉 'week_number': {data.get('week_number')}")
            print(f"👉 'baby_development_bengali': {data.get('baby_development_bengali') is not None}")
            print(f"👉 'weekly_checklist' count: {len(data.get('weekly_checklist', []))}")
            
            # Check for serialization issues (test dump)
            try:
                # Use default=str to handle dates like FastAPI would, but stricter
                json_str = json.dumps(data, default=str)
                print("✅ JSON Serialization: OK")
            except Exception as e:
                print(f"❌ JSON Serialization Failed: {e}")
        else:
            print("❌ DATA IS NONE!")

    except Exception as e:
        print(f"❌ Execution Failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_care_plan())
