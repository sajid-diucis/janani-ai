
import urllib.request
import json
import ssl

def test_live_chat():
    url = "https://janani-ai.onrender.com/api/chat/message"
    payload = {
        "message": "Hello, is the AI working?",
        "user_context": {"user_id": "debug_script_001"},
        "conversation_id": "debug_session_001"
    }
    
    data = json.dumps(payload).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Janani-Debug-Script')
    
    # Context for SSL (ignore self-signed if needed, though Render has valid SSL)
    ctx = ssl.create_default_context()
    
    print(f"Sending request to {url}...")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
            status = response.status
            body = response.read().decode('utf-8')
            print(f"Status: {status}")
            try:
                json_body = json.loads(body)
                print(f"Response: {json.dumps(json_body, indent=2, ensure_ascii=False)}")
            except:
                print(f"Response (Raw): {body}")
            
    except urllib.request.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Reason: {e.reason}")
        print(f"Body: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_live_chat()
