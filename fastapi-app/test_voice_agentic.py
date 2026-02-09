"""
Test Voice-Triggered Agentic Features
Proves that voice commands trigger internal tool execution
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_tool_detection():
    """Test that detect_tool_from_query works correctly"""
    print("=" * 60)
    print("🔧 TESTING TOOL DETECTION")
    print("=" * 60)
    
    # Import the detection function
    import sys
    sys.path.insert(0, ".")
    from services.agent_tools import detect_tool_from_query
    
    test_cases = [
        # Menu detection
        ("আমাকে একটা মেনু দাও", "", "GENERATE_FOOD_MENU"),
        ("500 টাকার বাজেটে মেনু দাও", "", "GENERATE_FOOD_MENU"),
        ("give me a food menu", "", "GENERATE_FOOD_MENU"),
        
        # Care plan detection
        ("এই সপ্তাহের কেয়ার প্ল্যান দাও", "", "GET_CARE_PLAN"),
        ("কী করব আজ?", "", "GET_CARE_PLAN"),
        ("what should I do this week", "", "GET_CARE_PLAN"),
        
        # Food safety detection
        ("আমি কি আম খেতে পারি?", "", "CHECK_FOOD_SAFETY"),
        ("মাছ নিরাপদ কি আমার জন্য?", "", "CHECK_FOOD_SAFETY"),
        ("can I eat mango", "", "CHECK_FOOD_SAFETY"),
        
        # Profile update detection
        ("আমার নাম রাহিমা", "", "UPDATE_PROFILE"),
        ("20 সপ্তাহ চলছে", "", "UPDATE_PROFILE"),
        ("my name is Rahima", "", "UPDATE_PROFILE"),
        ("বয়স 25", "", "UPDATE_PROFILE"),
        
        # No tool (general question)
        ("আমার কেমন লাগছে?", "", None),
        ("hello", "", None),
    ]
    
    passed = 0
    failed = 0
    
    for query, response, expected in test_cases:
        result = detect_tool_from_query(query, response)
        tool_name = result[0] if result else None
        
        if tool_name == expected:
            status = "✅"
            passed += 1
        else:
            status = "❌"
            failed += 1
        
        print(f"{status} Query: '{query[:30]}...' → {tool_name} (expected: {expected})")
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_tool_execution():
    """Test that tools actually execute and return results"""
    print("\n" + "=" * 60)
    print("⚡ TESTING TOOL EXECUTION")
    print("=" * 60)
    
    import sys
    sys.path.insert(0, ".")
    from services.agent_tools import execute_tool
    import asyncio
    
    # Create a mock profile
    profile = {
        "user_id": "test_agentic",
        "name": "Test User",
        "weeks_pregnant": 28,
        "trimester": "third",
        "age": 25,
        "conditions": ["mild_anemia"]
    }
    
    async def run_tests():
        # Test menu generation
        print("\n1. Testing GENERATE_FOOD_MENU...")
        try:
            msg, data = await execute_tool("GENERATE_FOOD_MENU", {"budget": 500}, profile)
            if data and "menu_items" in data:
                print(f"   ✅ Menu generated: {len(data.get('menu_items', []))} items")
            else:
                print(f"   ⚠️ Menu returned but no items: {msg[:100]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test care plan
        print("\n2. Testing GET_CARE_PLAN...")
        try:
            msg, data = await execute_tool("GET_CARE_PLAN", {"week": 28}, profile)
            if data:
                print(f"   ✅ Care plan generated for week {data.get('week', '?')}")
            else:
                print(f"   ⚠️ Care plan returned but no data: {msg[:100]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test profile update
        print("\n3. Testing UPDATE_PROFILE...")
        try:
            msg, data = await execute_tool("UPDATE_PROFILE", {"name": "রাহিমা", "week": 32}, profile)
            if data:
                print(f"   ✅ Profile updated: {data.get('name', '?')}, week {data.get('weeks_pregnant', '?')}")
            else:
                print(f"   ⚠️ Profile returned but no data: {msg[:100]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    asyncio.run(run_tests())


def main():
    print("\n🚀 Voice-Triggered Agentic Features Test\n")
    
    test_tool_detection()
    test_tool_execution()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print("""
Voice Health Check now supports:

1. 🍽️  GENERATE_FOOD_MENU
   - Say: "আমাকে একটা মেনু দাও" or "500 টাকার বাজেটে মেনু দাও"
   - Returns: menu_items[] in tool_result

2. 📅  GET_CARE_PLAN
   - Say: "এই সপ্তাহের কেয়ার প্ল্যান দাও" or "কী করব?"
   - Returns: care plan in tool_result

3. 🥗  CHECK_FOOD_SAFETY
   - Say: "আমি কি আম খেতে পারি?" or "মাছ নিরাপদ?"
   - Returns: safety decision in tool_result

4. 👤  UPDATE_PROFILE
   - Say: "আমার নাম রাহিমা, 25 সপ্তাহ চলছে"
   - Returns: updated profile in tool_result
    """)


if __name__ == "__main__":
    main()
