
import urllib.request
import json
import ssl

def check_health():
    url = "https://janani-ai.onrender.com/health"
    
    # Context for SSL
    ctx = ssl.create_default_context()
    
    print(f"Checking health at {url}...")
    try:
        with urllib.request.urlopen(url, context=ctx, timeout=30) as response:
            status = response.status
            body = response.read().decode('utf-8')
            print(f"Status: {status}")
            try:
                data = json.loads(body)
                print("Health Data:")
                print(json.dumps(data, indent=2))
            except:
                print(f"Raw Body: {body}")
            
    except Exception as e:
        print(f"Error checking health: {str(e)}")

if __name__ == "__main__":
    check_health()
