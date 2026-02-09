import asyncio
import sys
import os
import traceback

# Add project root to path
sys.path.append(os.getcwd())

async def test_tools():
    print("🔄 Testing Imports...")
    try:
        from services.agent_tools import detect_tool_from_query, execute_tool
        print("✅ Imports Successful")
    except ImportError as e:
        print(f"❌ Import Failed: {e}")
        return
    except Exception as e:
        print(f"❌ General Error during Import: {e}")
        return

    print("\n🔄 Testing Tool Detection...")
    try:
        # Test Menu Detection
        query = "give me menu for 2000 taka"
        result = detect_tool_from_query(query)
        print(f"Query: '{query}' -> Detected: {result}")
        
        # Test Care Plan Detection
        query = "give me weekly plan"
        result = detect_tool_from_query(query)
        print(f"Query: '{query}' -> Detected: {result}")
        
    except Exception as e:
        print(f"❌ Detection Failed: {e}")
        traceback.print_exc()

    print("\n🔄 Testing Tool Execution...")
    try:
        # Mock Profile
        profile = {
            "user_id": "test_user",
            "name": "Test Mom",
            "trimester": "second", 
            "weeks_pregnant": 20,
            "conditions": []
        }
        
        # Test Menu Execution (Mock AI call or just see if it crashes before)
        print("▶️ Executing Menu Tool (may fail if AI not configured, but should trace)...")
        # We expect this might fail on AI call but we want to see if it IMPORTS correctly
        result = await execute_tool("GENERATE_FOOD_MENU", {"budget": 1000}, profile) 
        print(f"✅ Menu Tool Result: {str(result[0])[:50]}...")
        
        # Test Care Plan Execution
        print("▶️ Executing Care Plan Tool...")
        result = await execute_tool("GET_CARE_PLAN", {"week": 20}, profile)
        print(f"✅ Care Plan Result: {str(result[0])[:50]}...")
        
    except Exception as e:
        print(f"❌ Execution Failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tools())
