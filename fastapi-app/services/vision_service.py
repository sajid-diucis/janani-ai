from openai import OpenAI
import base64
from typing import Dict, Any
from config import settings

class VisionService:
    def __init__(self):
        self.groq_client = None
        if settings.groq_api_key:
            self.groq_client = OpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )

    async def analyze_prescription(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze prescription image using Groq Vision API"""
        try:
            if not self.groq_client:
                raise Exception("Vision API not available. API key not configured.")
            
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            prompt = """You are a pharmacist. Analyze this prescription and respond in Bengali:
1. Medicine names and doses
2. Is it safe during pregnancy?
3. Any warnings
4. General advice

Important: Only provide information, do not advise changing medicines."""
            
            response = self.groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ],
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content
            return {
                "medicines": [{"name": "Analysis complete", "dose": "See details"}],
                "safety_info": {"pregnancy_safe": None},
                "warnings": ["Do not change medicines without doctor advice"],
                "recommendations": analysis_text,
                "pregnancy_safe": None
            }
        except Exception as e:
            raise Exception(f"Prescription analysis error: {str(e)}")

    async def analyze_food(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze food image using Groq Vision API"""
        try:
            if not self.groq_client:
                raise Exception("Food Analysis API not available. API key not configured.")
            
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            prompt = """You are a nutritionist. Analyze this food and respond in Bengali:
1. Food name
2. Estimated calories
3. Is it safe for pregnant women?
4. Nutritional benefits
5. Any warnings

Give a concise and simple answer."""
            
            response = self.groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ],
                max_tokens=400
            )
            
            analysis_text = response.choices[0].message.content
            return {
                "food_name": "Food analysis complete",
                "calories": None,
                "pregnancy_safe": True,
                "nutritional_benefits": ["Nutritious food"],
                "warnings": [],
                "recommendations": analysis_text
            }
        except Exception as e:
            raise Exception(f"Food analysis error: {str(e)}")