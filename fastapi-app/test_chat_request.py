import requests
import json

url = "http://127.0.0.1:8000/api/agent/chat"
payload = {
    "user_id": "test_user",
    "query": "Hello, I am pregnant and have a headache.",
    "image_base64": None,
    "audio_base64": None
}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
