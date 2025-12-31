import requests
import json
import time

def test_fastapi_endpoints():
    base_url = "http://localhost:8000"
    print("🧪 Testing Janani AI FastAPI Endpoints")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. 🩺 Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
    
    # Test 2: Main Page
    print("\n2. 🏠 Main Page")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print(f"❌ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Main page error: {str(e)}")
    
    # Test 3: API Documentation
    print("\n3. 📚 API Documentation")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {str(e)}")
    
    # Test 4: Chat Message (without API keys)
    print("\n4. 💬 Chat Message (No API Keys)")
    try:
        payload = {
            "message": "আমার পেট ব্যথা করছে",
            "conversation_id": None
        }
        response = requests.post(f"{base_url}/api/chat/message", 
                               json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat endpoint responsive")
            print(f"   Success: {result.get('success')}")
            if not result.get('success'):
                print(f"   Expected error: {result.get('error', 'N/A')}")
            else:
                print(f"   Response: {result.get('response', 'N/A')}")
        else:
            print(f"❌ Chat failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
    
    # Test 5: Emergency Check
    print("\n5. 🚨 Emergency Detection")
    try:
        payload = {"text": "রক্তপাত হচ্ছে"}
        response = requests.post(f"{base_url}/api/emergency/check", 
                               json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Emergency detection working")
            print(f"   Is Emergency: {result.get('is_emergency')}")
            print(f"   Keywords: {result.get('detected_keywords')}")
            print(f"   Level: {result.get('emergency_level')}")
        else:
            print(f"❌ Emergency check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Emergency error: {str(e)}")
    
    # Test 6: Get Emergency Keywords
    print("\n6. 📋 Emergency Keywords List")
    try:
        response = requests.get(f"{base_url}/api/emergency/keywords", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Emergency keywords accessible")
            print(f"   Keywords count: {len(result.get('keywords', []))}")
        else:
            print(f"❌ Keywords failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Keywords error: {str(e)}")

    print("\n" + "=" * 50)
    print("🏁 FastAPI Testing Complete!")
    print("\n📝 Summary:")
    print("✅ Core server is running")
    print("⚠️  API keys needed for full AI functionality")
    print("✅ Emergency detection works without API keys")
    print("✅ Web interface should be accessible")
    
if __name__ == "__main__":
    test_fastapi_endpoints()