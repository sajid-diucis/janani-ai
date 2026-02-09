import os
import asyncio
from openai import AsyncOpenAI
from config import settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_deepseek():
    print(f"\n--- Checking DeepSeek API ---")
    api_key = settings.deepseek_api_key or os.getenv("DEEPSEEK_API_KEY")
    base_url = settings.deepseek_base_url or os.getenv("DEEPSEEK_BASE_URL")
    
    print(f"Base URL: {base_url}")
    print(f"API Key present: {'Yes' if api_key else 'No'}")

    if not api_key:
        print("❌ DeepSeek API Key missing!")
        return

    client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=10.0)
    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print(f"✅ DeepSeek Response (deepseek-chat): {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ DeepSeek Connection Failed: {e}")


async def check_gemini():
    print(f"\n--- Checking Gemini API (via Proxy) ---")
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    base_url = settings.gemini_base_url or os.getenv("GEMINI_BASE_URL")
    model = settings.gemini_model_id or "google/gemini-2.5-flash"

    print(f"Base URL: {base_url}")
    print(f"Model ID: {model}")
    print(f"API Key present: {'Yes' if api_key else 'No'}")

    if not api_key:
        print("❌ Gemini API Key missing!")
        return

    client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=10.0)
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print(f"✅ Gemini Response ({model}): {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Gemini Connection Failed: {e}")

async def check_groq():
    print(f"\n--- Checking Groq API ---")
    api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
    
    print(f"API Key present: {'Yes' if api_key else 'No'}")

    if not api_key:
        print("❌ Groq API Key missing!")
        return

    client = AsyncOpenAI(
        api_key=api_key, 
        base_url="https://api.groq.com/openai/v1",
        timeout=10.0
    )
    try:
        response = await client.chat.completions.create(
            model="llama-3.2-11b-vision-preview", # Using a known Groq model
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print(f"✅ Groq Response (llama-3.2): {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Groq Connection Failed: {e}")


async def main():
    print("\n🚀 STARTING DIAGNOSTIC 🚀")
    
    # 1. DeepSeek
    print("\n-------------------------------------------")
    await check_deepseek()
    
    # 2. Gemini
    print("\n-------------------------------------------")
    await check_gemini()
    
    # 3. Groq
    print("\n-------------------------------------------")
    await check_groq()
    
    print("\n✅ DIAGNOSTIC COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())

