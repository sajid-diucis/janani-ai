import asyncio
import sys
import os
import traceback

# Add project root to path
sys.path.append(os.getcwd())

async def test_profile_update():
    print("🔄 Testing Profile Update...")
    try:
        from services.agent_tools import execute_tool
        
        # 1. Create a clean user for testing
        user_id = "test_profile_user"
        profile = {
            "user_id": user_id,
            "name": "Old Name",
            "weeks_pregnant": 20,
            "age": 25
        }
        
        # 2. Execute Update Tool (Change name and week)
        params = {"name": "New Name", "week": "30 সপ্তাহ", "age": 30}
        print(f"▶️ Executing Update with: {params}")
        
        message, data = await execute_tool("UPDATE_PROFILE", params, profile)
        
        print(f"✅ Result Message: {message[:50]}...")
        print(f"✅ Result Data: {data}")
        
        # 3. Verify Data matches expectation
        expected = {"name": "New Name", "weeks_pregnant": 30, "age": 30}
        
        match = True
        for k, v in expected.items():
            if data.get(k) != v:
                # Trimester is auto-calculated, so check raw fields
                if k not in data:
                     print(f"❌ Missing key: {k}")
                     match = False
                elif data[k] != v:
                     print(f"❌ Mismatch {k}: expected {v}, got {data[k]}")
                     match = False
        
        if match:
            print("✅ Profile Update Verification Passed!")
        
        # 4. Verify Persistence (Indirectly via what function it calls)
        from services.patient_state import IN_MEMORY_DB
        # Since execute_tool modifies state via update_patient...
        # But wait, update_patient modifies IN_MEMORY_DB using the *passed* user_id key?
        
        # The profile passed to execute_tool is just a dict.
        # But update_patient(user_id, updates) updates the global IN_MEMORY_DB.
        
        saved_profile = IN_MEMORY_DB.get(user_id)
        if saved_profile and saved_profile.get("name") == "New Name":
             print("✅ Persistence Verification Passed (In-Memory)!")
        else:
             print(f"❌ Persistence Failed! DB has: {saved_profile}")

    except Exception as e:
        print(f"❌ Test Failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_profile_update())
