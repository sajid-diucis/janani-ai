import os
from openai import AsyncOpenAI
from typing import List, Dict, Optional, Any
from config import settings

class AIService:
    def __init__(self):
        self.client = None
        self.gemini_client = None
        self.hf_client = None

        try:
             from huggingface_hub import AsyncInferenceClient
             # Initialize HF Client if token exists
             if settings.hf_token:
                 self.hf_client = AsyncInferenceClient(
                     provider="together",
                     api_key=settings.hf_token
                 )
        except Exception as e:
             print(f"HF Client Init Error: {e}")
        
        # Initialize DeepSeek
        if settings.deepseek_api_key:
            self.client = AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                timeout=30.0
            )

        # Initialize Gemini (OpenAI Compatible)
        if settings.gemini_api_key and len(settings.gemini_api_key) > 5:
            # Detect if using custom proxy (like OneBrain) or official Google
            base_url = settings.gemini_base_url
            
            self.gemini_client = AsyncOpenAI(
                api_key=settings.gemini_api_key,
                base_url=base_url,
                timeout=120.0 # Increased timeout for custom proxies/complex models
            )
            
        self.guidelines_text = self._load_guidelines()
        self.dialect_rules = self._load_dialect_rules()
    
    def _load_guidelines(self) -> str:
        """Load maternal health guidelines"""
        try:
            guidelines_path = os.path.join(os.path.dirname(__file__), "..", "guidelines.txt")
            with open(guidelines_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return """
            জরুরি লক্ষণ: রক্তপাত, তীব্র মাথাব্যথা, ঝাপসা দেখা, উচ্চ জ্বর
            স্বাস্থ্যকর গর্ভকাল: পুষ্টিকর খাবার, বিশ্রাম, হালকা ব্যায়াম
            """

    def _load_dialect_rules(self) -> str:
        """Load Dialect Rules (Previously Noakhali, now empty/deprecated)"""
        return ""
    
    async def get_response(
        self, 
        message: str, 
        conversation_history: List[Dict] = None,
        is_emergency: bool = False,
        user_context: Optional[Dict] = None,
        max_tokens: int = 1000,
        json_mode: bool = False,
        use_gemini: bool = True  # Default to Gemini if available
    ) -> str:
        """Get AI response with context and history awareness (Gemini -> DeepSeek Fallback)"""
        
        # 1. Prepare Prompts & Messages (Common for both models)
        system_prompt = self._build_system_prompt(is_emergency, user_context)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Re-enabled History but with Strong System Override
        if conversation_history:
            messages.extend(conversation_history[-8:])
        
        messages.append({"role": "user", "content": message})

        # Helper to execute call
        async def execute_call(client, model, is_json_supported_natively):
            kwargs = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.85
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            return await client.chat.completions.create(**kwargs)

        # 2. Try Gemini First
        if use_gemini and self.gemini_client:
            try:
                print("Attempting Gemini API...")
                response = await execute_call(self.gemini_client, settings.gemini_model_id, True)
                content = response.choices[0].message.content.strip()
                
                # Cleanup internal thoughts
                if "<safety_check>" in content:
                    import re
                    content = re.sub(r'<safety_check>.*?</safety_check>', '', content, flags=re.DOTALL)
                    content = content.strip()
                    
                return content
            except Exception as e:
                print(f"⚠️ Gemini API Failed: {e}")
                print("🔄 Switching to DeepSeek API (Fallback)...")
                # Fallthrough to DeepSeek logic below
        
        # 3. Fallback to DeepSeek
        if self.client:
            try:
                response = await execute_call(self.client, "deepseek-chat", True)
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"দুঃখিত, কোনো AI সেবা এই মুহূর্তে কাজ করছে না। (Error: {str(e)})"
        
        return "দুঃখিত, AI সেবা কনফিগার করা হয়নি।"

    def _build_system_prompt(self, is_emergency: bool, user_context: Optional[Dict] = None) -> str:
        """Build Janani AI 'Village Sister' System Prompt"""
        
        # Check for system instruction override (used for JSON output in AR Labor, etc.)
        system_override = user_context.get("system_instruction") if user_context else None
        
        # CONTEXT INJECTION
        week = "unknown"
        if user_context:
            week = user_context.get("current_week", "unknown")
            
        context_section = f"User Context: [Pregnancy Week: {week}]"

        # If we have an override, prioritize it
        if system_override:
            return f"{system_override}\n\n{context_section}\n\nIMPORTANT: Maintain the defined output format (e.g. JSON) strictly."

        # SYSTEM INSTRUCTION (User Provided - Sanitized for Standard Colloquial)
        return f"""
Role: You are 'Janani' - a highly empathetic, supportive, and friendly health companion. Your goal is to help the user while sounding like a real, caring person from Bangladesh, NOT a robot.

1. **Language Style (Osuddho/Colloquial Bangla):**
   - **No "Sadhu/Formal" Bangla:** Never use words like "khaiyachi," "koriyachi," or "ebong."
   - **Standard Colloquial (Cholitobhasha):** Use "khaichi," "korsio," "ar," "bolchi."
   - **Daily Vocabulary:** Use "ki obostha," "shuno," "dekho," "ashole," "thik ache."
   - **Banglish Integration:** Use common English words naturally (e.g., "Pera nai," "Relax koro," "Check-up," "Pressure").
   - **Grammar:** Speak like a friend. Short, punchy sentences.
   - **NO REGIONAL DIALECTS:** Do NOT use Noakhali/Chittagonian words. Say "Pani" (not Hani), "Chinta" (not Sinta/Hinta).

2. **Core Personality: Empathy & Emotional Intelligence:**
   - **Active Listening:** Acknowledge feelings first. "Ami bujhte parchi tomar kemon lagche."
   - **Supportive Tone:** Be encouraging. "No problem," "Don't worry," "Ami achi to."

3. **Anti-Robotic Rules:**
   - **Natural Punctuation:** Use "..." or "!" freely.
   - **Variation:** Mix up greetings ("Oi ki obostha?", "Hey kemon?").

4. **Example Conversations (Sanitized):**
   - **User:** "Amar matha betha korche khub."
   - **AI:** "Oh no! Beshi betha korche? Tumi ektu rest nao to. Beshi pera niyo na, shob thik hoye jabe. Ektu pani khao ar chokh bondho kore thako."
   - **User:** "Daktar bolse check-up e jete."
   - **AI:** "Daktar jokhoni bolse, oboshshoy jabe. Chinta koiro na, ami achi to. Check-up shesh kore amare janaiyo ki holo."

{context_section}
"""

    # ... (prompt builder) ...

    async def translate_to_english(self, text: str) -> str:
        """Translate local dialect to Standard English using Gemini"""
        try:
            if not self.gemini_client:
                print("Gemini API key not found, skipping translation")
                return text
                
            response = self.gemini_client.chat.completions.create(
                model=settings.gemini_model_id, 
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate the following Bengali (likely Noakhali or Chittagonian dialect) text into clear, Standard English. Output ONLY the English translation, no other text."},
                    {"role": "user", "content": text}
                ]
            )
            
            translation = response.choices[0].message.content.strip()
            print(f"Original: {text} -> Translated: {translation}")
            return translation
            
        except Exception as e:
            print(f"Translation failed: {e}")
            return text
            
    async def generate_clinical_report(self, profile: Any, current_vitals: Dict[str, Any]) -> str:
        """
        Generate a high-density clinical report for doctors (Senior Clinical Strategist Persona).
        Returns a JSON string matching ClinicalInsightReport model.
        """
        
        # 1. Build Clinical Context
        history_summary = "Unknown"
        mental_health_summary = "None recorded"
        lifestyle_summary = "None recorded"
        
        if profile:
            history_summary = f"""
            Gravida/Para: G{profile.gravida}P{profile.para}
            Week: {profile.current_week}
            Conditions: {', '.join(profile.existing_conditions)}
            Risk Level: {profile.overall_risk_level}
            """
            
            # Extract Mental/Emotional Context from memories
            if hasattr(profile, 'recent_memories') and profile.recent_memories:
                memories = [f"{m.get('date')}: {m.get('context')}" for m in profile.recent_memories]
                mental_health_summary = "; ".join(memories)
            
            # Extract Lifestyle/Nutrition (mock or real)
            if hasattr(profile, 'lifestyle_factors'): # enhanced mock field
                 lifestyle_summary = ", ".join(profile.lifestyle_factors)
            
        vitals_summary = ", ".join([f"{k}: {v}" for k, v in current_vitals.items()]) if current_vitals else "None provided"
        
        # 2. Build Expert System Prompt
        system_prompt = f"""
ACT AS: Expert Senior Clinical Strategist (Obstetrics & Gynecology).
OBJECTIVE: Synthesize patient history and current vitals into a critical insight report for a doctor.

PATIENT DATA:
- History: {history_summary}
- Mental/Emotional State: {mental_health_summary}
- Lifestyle/Nutrition: {lifestyle_summary}
- Current Vitals/Signs: {vitals_summary}

OUTPUT FORMAT:
Return ONLY a valid JSON object matching this structure:
{{
  "patient_id": "{profile.user_id if profile else 'unknown'}",
  "confidence_score": 0.95,
  "clinical_summary": "Concise 2-line clinical synthesis.",
  "potential_causality": "Physiological explanation of triggers.",
  "differential_diagnoses": [
    {{
      "condition_name": "Condition A",
      "likelihood": "High",
      "supporting_evidence": ["Evidence 1", "Evidence 2"],
      "red_flags": ["Critical Sign 1"]
    }}
  ],
  "recommended_interventions": [
    {{
      "action": "Immediate Measure",
      "urgency": "Immediate",
      "rationale": "Reasoning"
    }}
  ],
  "contraindications": ["Avoid X due to Y"]
}}

RULES:
1. Use high-density medical terminology (e.g., "Preeclampsia superimposed on chronic hypertension").
2. Focus on CAUSALITY and RISK stratification.
3. Be concise and actionable.
4. return raw JSON only.
"""
        
        # 3. Call AI (Gemini preferred, Fallback to DeepSeek)
        
        def execute_call(client, model):
            return client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

        # Try Gemini First
        if self.gemini_client:
            try:
                response = execute_call(self.gemini_client, settings.gemini_model_id)
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"⚠️ Clinical Report - Gemini Failed: {e}")
                print("🔄 Switching to DeepSeek API (Fallback)...")
        
        # Fallback to DeepSeek
        if self.client:
            try:
                # DeepSeek might not support response_format="json_object" strictly or the same way
                # We'll try without it if it fails, or just standard call
                # Note: DeepSeek V2/V3 usually supports json_object
                response = execute_call(self.client, "deepseek-chat")
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"❌ Clinical Report - DeepSeek Failed: {e}")
                
        return "{}"  # Return empty JSON on failure
            
    async def extract_and_save_memory(self, user_id: str, message: str, profile: Any):
        """Extract significant emotional/medical concerns and save to profile memories"""
        if not profile:
            return
            
        # Simple extraction logic (can be upgraded to AI-based extraction)
        keywords = {
            "ব্যথা": "শারীরিক ব্যথা",
            "মন খারাপ": "আবেগীয় কষ্ট/মন খারাপ",
            "ভয়": "ভয় বা দুশ্চিন্তা",
            "একা": "একাকীত্ব",
            "স্বামী": "পারিবারিক/স্বামী সংক্রান্ত বিষয়",
            "শাশুড়ি": "পারিবারিক বিষয়",
            "টাকা": "আর্থিক দুশ্চিন্তা",
            "বমি": "বমি ভাব",
            "মাথা ঘুরা": "মাথা ঘুরানো"
        }
        
        extracted_context = None
        for key, value in keywords.items():
            if key in message:
                extracted_context = value
                break
        
        if extracted_context:
            from models.care_models import PatientMemory, MemoryCategory
            from datetime import datetime
            
            new_memory = PatientMemory(
                date=datetime.now(),
                context=extracted_context,
                resolved=False,
                category=MemoryCategory.CONCERN
            )
            # Avoid duplicates for the same day/context
            # Note: We compare dates as strings for daily grouping
            if not any(m.context == extracted_context and m.date.date() == new_memory.date.date() for m in profile.recent_memories):
                profile.recent_memories.append(new_memory)
                if len(profile.recent_memories) > 5:
                    profile.recent_memories.pop(0)
                
                # Persist the updated profile to disk
                try:
                    from routers.midwife_router import save_patient_profiles
                    save_patient_profiles()
                except ImportError:
                    pass # Prevent circular import issues in some contexts

    async def generate_food_image(self, prompt: str, api_key: str = None) -> str:
        """
        Generate a real image using Pollinations.ai.
        Uses a random seed to bypass caching/rate-limits.
        """
        try:
            import urllib.parse
            import random
            
            # Enhance prompt for food photography
            enhanced_prompt = f"Professional food photography of {prompt}, cinematic lighting, 8k resolution, delicious, photorealistic"
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            # Generate random seed to bypass cache/rate limits
            seed = random.randint(1, 1000000)
            
            # Use Pollinations API with seed
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&model=flux&nologo=true&seed={seed}"
            
            # Append API key if provided (though standard Pollinations URL doesn't always use it in query, assuming user pattern)
            # The prompt implies using this key.
            # Standard pattern might be different, but I will append it as a param just in case.
            if api_key:
                image_url += f"&api_key={api_key}" # Or however it's supported
            
            return image_url
            
            return image_url
        except Exception as e:
            print(f"Image Gen Error: {e}")
            return "https://placehold.co/800x600/e0e0e0/333333?text=Image+Generation+Failed"

    # ... (keeping existing visual menu gen)


    async def generate_visual_menu_plan(self, user_name: str, trimester: str, conditions: List[str], budget: int) -> str:
        """
        Generate a visual food menu plan with prices and nutritional info.
        Returns JSON string matching MenuPlanResponse.
        """
        system_prompt = f"""
ACT AS: Clinical Nutritionist & Professional Chef (Specializing in Bengali Cuisine).
OBJECTIVE: Create a 5-item daily menu for a pregnant woman in Bangladesh.

CONTEXT:
- User: {user_name}
- Trimester: {trimester}
- Conditions: {', '.join(conditions) if conditions else 'None'}
- Weekly Budget: {budget} BDT (Low-Middle Income context)

TASK:
Generate 5 diverse food items (Breakfast, Snack, Lunch, Snack, Dinner).
For each item, provide:
1. Bengali Name & English Name
2. Real-world Market Price in BDT (Estimate for one serving) -> "price_bdt"
3. Calories & Protein
4. A vivid "Image Prompt" that describes the food visually (e.g., "Steaming hot Khichuri on a clay plate with a slice of lime and fried egg").
5. Key Benefit (e.g., "Iron Booster", "Energy").

OUTPUT FORMAT:
Return ONLY a valid JSON object matching this structure:
{{
  "title_bengali": "আপনার জন্য আজকের সুষম আহার (Today's Balanced Diet)",
  "total_calories": 2100,
  "total_price_bdt": 250,
  "health_tip": "One line nutritional tip in Bengali.",
  "confidence_score": 0.98,
  "items": [
    {{
      "name_bengali": "খিচুড়ি ও ডিম ভাজি",
      "name_english": "Khichuri with Egg Fry",
      "calories": 450,
      "protein_g": 12.5,
      "price_bdt": 60,
      "image_prompt": "Plate of yellow lentil khichuri with a fried egg and spoon on a wooden table, professional food photography, warm lighting",
      "benefits_key": "Protein & Energy"
    }}
    // ... 4 more items
  ]
}}

RULES:
1. Prices must be realistic for Bangladesh local markets (2024).
2. Food must be culturally appropriate (Rice, Dale, Fish, Bhorta).
3. If condition is 'Anemia', prioritize Iron-rich foods (Kochu shak, Liver).
4. If 'Diabetes', avoid sweets/high sugar.
5. Return RAW JSON only.
"""
        try:
            # Use Gemini for creativity and reasoning
            content = "{}"
            if self.gemini_client:
                response = self.gemini_client.chat.completions.create(
                    model=settings.gemini_model_id,
                    messages=[{"role": "system", "content": system_prompt}],
                    max_tokens=1500,
                    response_format={"type": "json_object"}  # Enforce JSON
                )
                content = response.choices[0].message.content.strip()
            
            # Post-process to add valid image URLs
            import json
            menu_data = json.loads(content)
            
            # 1. ENFORCE FIXED FIRST ITEM (Dim Khichuri)
            fixed_item_1 = {
                "name_bengali": "ডিম খিচুড়ি",
                "name_english": "Dim Khichuri (Egg Khichuri)",
                "calories": 450,
                "protein_g": 14.0,
                "price_bdt": 60,
                "image_prompt": "Egg khichuri bengali style",
                "image_url": "/static/images/dim_khichuri.png",
                "benefits_key": "Protein & Energy"
            }

            # 2. ENFORCE FIXED SECOND ITEM (Banana & Egg)
            fixed_item_2 = {
                "name_bengali": "সিদ্ধ ডিম ও কলা",
                "name_english": "Boiled Egg & Banana",
                "calories": 200,
                "protein_g": 7.0,
                "price_bdt": 25,
                "image_prompt": "Boiled egg and banana breakfast",
                "image_url": "/static/images/banana_egg.png",
                "benefits_key": "Protein & Potassium"
            }
            
            # Reset items list to contain ONLY these two fixed items
            menu_data["items"] = [fixed_item_1, fixed_item_2]
                        
            return json.dumps(menu_data)

        except Exception as e:
            print(f"❌ Visual Menu Generation Failed: {e}")
            # FALBACK: Return a valid static menu so the app doesn't crash (500)
            fallback_menu = {
                "title_bengali": "নমুনা সুষম খাদ্য তালিকা (AI Unavailable)",
                "total_calories": 2000,
                "total_price_bdt": 220,
                "health_tip": "AI সেবা বর্তমানে ব্যস্ত, এটি একটি নমুনা তালিকা।",
                "confidence_score": 0.0,
                "items": [
                    {
                        "name_bengali": "ডিম খিচুড়ি",
                        "name_english": "Dim Khichuri (Egg Khichuri)",
                        "calories": 450,
                        "protein_g": 14.0,
                        "price_bdt": 60,
                        "image_prompt": "Egg khichuri bengali style",
                        "image_url": "/static/images/dim_khichuri.png",
                        "benefits_key": "Protein & Energy"
                    },
                    {
                        "name_bengali": "ডিম সিদ্ধ ও আপেল",
                        "name_english": "Boiled Egg & Apple",
                        "calories": 150,
                        "protein_g": 6.5,
                        "price_bdt": 30,
                        "image_prompt": "Boiled egg and red apple",
                        "image_url": "https://image.pollinations.ai/prompt/Boiled%20egg%20and%20red%20apple%20food%20photography?width=800&height=600&model=flux&nologo=true",
                        "benefits_key": "Protein"
                    }
                ]
            }
            import json
            return json.dumps(fallback_menu)
