import asyncio
from services.agent_tools import detect_tool_from_query, execute_tool

async def test_emergency():
    # Test 1: Detection
    query = "আমার খুব রক্তপাত হচ্ছে জরুরি সাহায্য চাই"
    print(f"Query: {query}")
    tool_name, params = detect_tool_from_query(query)
    print(f"Detected: {tool_name}, Params: {params}")
    
    if tool_name == "ACTIVATE_EMERGENCY":
        print("✅ Detection passed")
    else:
        print("❌ Detection failed")
        
    # Test 2: Execution
    print("\nExecuting tool...")
    profile = {"user_id": "test_verification"}
    message, data = await execute_tool(tool_name, params, profile)
    
    print("\nResult Data:")
    print(data)
    
    if data and data.get("emergency_activated") and data.get("emergency_redirect") == "http://localhost:8000/ar-dashboard":
        print("✅ Execution passed: Correct redirect info returned")
    else:
        print("❌ Execution failed")

if __name__ == "__main__":
    asyncio.run(test_emergency())
