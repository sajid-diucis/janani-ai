from config import settings
import os

print("--- LOADED CONFIGURATION ---")
print(f"GEMINI_API_KEY: {settings.gemini_api_key}")
print(f"GEMINI_BASE_URL: {settings.gemini_base_url}")
print(f"DEEPSEEK_API_KEY: {settings.deepseek_api_key}")
print(f"Environment File: {settings.Config.env_file}")
print(f"Does .env exist? {os.path.exists(settings.Config.env_file)}")
