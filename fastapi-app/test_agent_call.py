import asyncio
from services.execution_bridge import delegate_to_agent

async def test_emergency_call():
    print("🧪 TEST 3: Trigger Emergency Call via Bridge")
    
    params = {
        "location": "Hatirjheel Lake",
        "condition": "Severe Bleeding",
        "phone": "+8801700000000"
    }
    
    result = await delegate_to_agent("emergency_call", params)
    print(f"Agent Result: {result}")
    
    if result.get("status") == "success":
        print("✅ Emergency Call Bridge Success")
    else:
        print("❌ Emergency Call Bridge Failed")

if __name__ == "__main__":
    asyncio.run(test_emergency_call())
