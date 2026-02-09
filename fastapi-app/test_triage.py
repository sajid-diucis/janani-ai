import requests
import json

url = "http://localhost:8000/api/midwife/triage" # Correct Endpoint
headers = {"Content-Type": "application/json"}
payload = {
    "user_id": "test_script_user",
    "input_text": "Show me food for 2000 taka (anemia)", # Complex query
    "include_history": False
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    
    data = response.json()
    print("--- RESPONSE ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # Validation
    actions = data.get("actions", [])
    if "SHOW_FOOD_MENU" in actions:
        print("\n✅ SUCCESS: 'SHOW_FOOD_MENU' action found!")
    else:
        print("\n❌ RETURNED ACTIONS:", actions)
        print("Required Action 'SHOW_FOOD_MENU' MISSING.")

except Exception as e:
    print(f"Error: {e}")
