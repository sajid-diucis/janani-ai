# Test script for TRUE Agentic Workflow - Menu Generation
import requests
import json

API_URL = "http://localhost:8000/api/midwife/triage"

# Simulate user asking for food menu
payload = {
    "user_id": "user_123",
    "input_text": "আমাকে ২০০০ টাকার বাজেটে খাবারের তালিকা দেখাও",
    "include_history": True
}

print("📡 Sending request to Triage API...")
print(f"   Query: {payload['input_text']}")
print("-" * 50)

try:
    response = requests.post(API_URL, json=payload, timeout=120)
    data = response.json()
    
    print(f"\n✅ Response Status: {response.status_code}")
    
    # Check for tool execution
    tool_executed = data.get("tool_executed")
    tool_data = data.get("tool_data")
    
    if tool_executed:
        print(f"\n🔧 TOOL EXECUTED: {tool_executed}")
        
        if tool_data:
            print(f"   📊 Tool Data Keys: {list(tool_data.keys())}")
            
            # Show menu items if present
            menu_items = tool_data.get("menu_items", [])
            if menu_items:
                print(f"\n   🍽️ MENU ITEMS ({len(menu_items)} items):")
                for i, item in enumerate(menu_items[:3], 1):
                    name = item.get("name_bangla", item.get("name", "Unknown"))
                    price = item.get("price_bdt", 0)
                    print(f"      {i}. {name} - ৳{price}")
    else:
        print("\n⚠️ NO TOOL EXECUTED")
        print("   The system should have detected GENERATE_FOOD_MENU...")
    
    # Show message preview
    message = data.get("message", "")
    print(f"\n💬 Message Preview (first 300 chars):")
    print(f"   {message[:300]}...")
    
    print(f"\n📊 Risk Level: {data.get('risk_level', 'N/A')}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
