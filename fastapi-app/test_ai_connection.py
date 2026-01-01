import asyncio
import os
import sys

# Mock sqlite for chroma if needed
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from config import settings
from services.ai_service import AIService

async def test():
    print(f"--- Configuration ---")
    print(f"DeepSeek Key Present: {bool(settings.deepseek_api_key)}")
    print(f"Gemini Key: {settings.gemini_api_key[:5] if settings.gemini_api_key else 'None'}...")
    print(f"Gemini Base URL: {settings.gemini_base_url}")
    print(f"Gemini Model: {settings.gemini_model_id}")
    print(f"---------------------")
    
    print("Initializing AIService...")
    ai = AIService()
    
    # Check clients
    print(f"Gemini Client: {ai.gemini_client}")
    print(f"DeepSeek Client: {ai.client}")
    
    print("\nAttempting 'get_response' call...")
    try:
        response = await ai.get_response(
            message="Hello, are you working?", 
            user_context={"user_id": "debug_local"}
        )
        print(f"\nResult: {response}")
        
    except Exception as e:
        print(f"\nFATAL ERROR in test: {e}")

if __name__ == "__main__":
    asyncio.run(test())
