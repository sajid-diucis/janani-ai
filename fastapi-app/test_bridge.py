import asyncio
from services.execution_bridge import delegate_to_agent
from services.agent_tools import detect_tool_from_query

async def test_integration():
    print("🧪 TEST 1: Detect Booking Intent")
    query = "I want to book an appointment at Hatirjheel for 15 Jan"
    tool, params = detect_tool_from_query(query)
    print(f"Detected: {tool}, Params: {params}")
    
    if tool == "EXECUTE_EXTERNAL_TASK" and params["params"].get("location") == "hatirjheel":
        print("✅ Detection Success")
    else:
        print("❌ Detection Failed")
        return

    print("\n🧪 TEST 2: Delegate to Agent (Bridge)")
    result = await delegate_to_agent("appointment", params["params"])
    print(f"Agent Result: {result}")
    
    if result.get("status") == "success":
        print("✅ Bridge Success")
    else:
        print("❌ Bridge Failed")

if __name__ == "__main__":
    asyncio.run(test_integration())
