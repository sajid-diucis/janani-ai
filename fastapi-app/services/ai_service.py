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
        if settings.gemini_api_key:
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

        # SYSTEM INSTRUCTION (Optimized for Speed - 50% shorter)
        return f"""You are 'Janani' - a warm, sisterly health companion from Bangladesh. Sound like a caring friend, NOT a robot.

LANGUAGE RULES:
- Use Colloquial Bangla (Cholitobhasha): "khaichi," "korsio," "ar," "bolchi"
- Mix Banglish naturally: "Relax koro," "Check-up," "Pressure"
- NO formal Sadhu Bangla or regional dialects (no Noakhali/Chittagong words)
- Short, punchy sentences

PERSONALITY:
- Empathetic: "Ami bujhte parchi tomar kemon lagche"
- Supportive: "Pera nai," "Ami achi to"
- Natural: Use "..." and "!" freely

EXAMPLE:
User: "Matha betha korche"
AI: "Oh no! Beshi betha? Ektu rest nao. Pani khao ar chokh bondho koro. Thik hoye jabe!"

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


    async def generate_visual_menu_plan(self, user_name: str, trimester: str, conditions: List[str], budget: int, phase: int = 1) -> str:
        """
        Generate a visual food menu plan with prices and nutritional info.
        Returns JSON string matching MenuPlanResponse.
        Phase 1: 5 hardcoded items
        Phase 2: 4 hardcoded items  
        Phase 3: 4 hardcoded items
        Phase 4+: AI-generated items
        """
        import json

        # Phase 1: 5 hardcoded items with images
        if phase == 1:
            phase_1_items = [
                {
                    "name_bengali": "চিংড়ি দিয়ে কচুর লতি (আয়রন সমৃদ্ধ)",
                    "name_english": "Kochur Loti with Chingri (High Iron)",
                    "calories": 250,
                    "protein_g": 18.0,
                    "price_bdt": 120,
                    "image_prompt": "Kochur Loti with Chingri and Lal Shak",
                    "image_url": "/static/images/menu_kochur_loti.jpg",
                    "benefits_key": "High Iron",
                    "recipe_bengali": "উপকরণ: কচুর লতি, চিংড়ি, রসুন, পেঁয়াজ।",
                    "audio_script_bengali": "চিংড়ি দিয়ে কচুর লতি! এটি আয়রন সমৃদ্ধ।",
                    "phase": 1
                },
                {
                    "name_bengali": "রূপচাঁদা দোপেয়াজা ও বেগুন ভর্তা",
                    "name_english": "Rupchanda Dopeyaja & Begun Bharta",
                    "calories": 350,
                    "protein_g": 25.0,
                    "price_bdt": 180,
                    "image_prompt": "Rupchanda Dopeyaja with Begun Bharta",
                    "image_url": "/static/images/menu_rupchanda.jpg",
                    "benefits_key": "Proteins & Health",
                    "recipe_bengali": "উপকরণ: রূপচাঁদা মাছ, পেঁয়াজ, বেগুন।",
                    "audio_script_bengali": "রূপচাঁদা মাছের দোপেয়াজা প্রোটিন সমৃদ্ধ।",
                    "phase": 1
                },
                {
                    "name_bengali": "নোয়াখালী নারিকেল মুরগি (হালকা ভার্সন)",
                    "name_english": "Noakhali Coconut Chicken (Light Version)",
                    "calories": 400,
                    "protein_g": 30.0,
                    "price_bdt": 150,
                    "image_prompt": "Noakhali Coconut Chicken with Korla",
                    "image_url": "/static/images/menu_coconut_chicken.jpg",
                    "benefits_key": "Healthy Weight",
                    "recipe_bengali": "উপকরণ: মুরগি, নারিকেল দুধ।",
                    "audio_script_bengali": "নোয়াখালীর নারিকেল মুরগি।",
                    "phase": 1
                },
                {
                    "name_bengali": "লোইট্টা শুঁটকি ভুনা (কম লবণ)",
                    "name_english": "Chepa/Loitta Shutki Bhuna (Low Salt)",
                    "calories": 300,
                    "protein_g": 22.0,
                    "price_bdt": 100,
                    "image_prompt": "Loitta Shutki Bhuna with Pui Shak",
                    "image_url": "/static/images/menu_shutki.jpg",
                    "benefits_key": "Rich in Minerals",
                    "recipe_bengali": "উপকরণ: শুঁটকি, রসুন, পেঁয়াজ।",
                    "audio_script_bengali": "শুঁটকি ভুনা কম লবণে।",
                    "phase": 1
                },
                {
                    "name_bengali": "মলা মাছের চচ্চড়ি",
                    "name_english": "Mola Fish Chorchori",
                    "calories": 280,
                    "protein_g": 20.0,
                    "price_bdt": 90,
                    "image_prompt": "Mola Fish Chorchori with Shim Bharta",
                    "image_url": "/static/images/menu_mola.jpg",
                    "benefits_key": "Calcium Booster",
                    "recipe_bengali": "উপকরণ: মলা মাছ, আলু, সরিষার তেল।",
                    "audio_script_bengali": "মলা মাছে আছে ক্যালসিয়াম।",
                    "phase": 1
                }
            ]

            response_data = {
                "title_bengali": "আপনার জন্য ৫ দিনের বিশেষ মেনু (পর্যায় ১)",
                "total_calories": 1580,
                "total_price_bdt": 640,
                "health_tip": "খাবারে লেবু মিশিয়ে খান।",
                "phase": 1,
                "confidence_score": 1.0,
                "items": phase_1_items
            }
            return json.dumps(response_data)

        # Phase 2: 4 hardcoded items with images
        if phase == 2:
            phase_2_items = [
                {
                    "name_bengali": "সরিষা ইলিশ (ভাপা স্টাইল)",
                    "name_english": "Ilish with Mustard (Shorisha Ilish)",
                    "calories": 420,
                    "protein_g": 32.0,
                    "price_bdt": 350,
                    "image_prompt": "Ilish Fish with Mustard Sauce",
                    "image_url": "/static/images/menu_ilish.jpg",
                    "benefits_key": "Omega-3 & Protein",
                    "recipe_bengali": "উপকরণ: ইলিশ, সরিষা বাটা।",
                    "audio_script_bengali": "সরিষা ইলিশ! ওমেগা-৩ সমৃদ্ধ।",
                    "phase": 2
                },
                {
                    "name_bengali": "ধোকার ডালনা (মসুর ডালের কেক)",
                    "name_english": "Dhokar Dalna (Lentil Cakes)",
                    "calories": 320,
                    "protein_g": 18.0,
                    "price_bdt": 80,
                    "image_prompt": "Dhokar Dalna Lentil Cakes",
                    "image_url": "/static/images/menu_dhokar.jpg",
                    "benefits_key": "Vegetarian Protein",
                    "recipe_bengali": "উপকরণ: ছোলার ডাল বাটা।",
                    "audio_script_bengali": "ধোকার ডালনা নিরামিষ প্রোটিন।",
                    "phase": 2
                },
                {
                    "name_bengali": "চিতল মাছের কোফতা",
                    "name_english": "Chital Fish Kofta",
                    "calories": 380,
                    "protein_g": 28.0,
                    "price_bdt": 200,
                    "image_prompt": "Chital Fish Kofta in Tomato Gravy",
                    "image_url": "/static/images/menu_chital.jpg",
                    "benefits_key": "High Protein",
                    "recipe_bengali": "উপকরণ: চিতল মাছ, আলু।",
                    "audio_script_bengali": "চিতল মাছের কোফতা প্রোটিন দেয়।",
                    "phase": 2
                },
                {
                    "name_bengali": "মুড়ি ঘণ্ট (মাছের মাথা দিয়ে)",
                    "name_english": "Muri Ghonto (Fish Head)",
                    "calories": 400,
                    "protein_g": 25.0,
                    "price_bdt": 150,
                    "image_prompt": "Muri Ghonto Fish Head with Dal",
                    "image_url": "/static/images/menu_4.jpg",
                    "benefits_key": "Brain Food & Calcium",
                    "recipe_bengali": "উপকরণ: মাছের মাথা, মুগ ডাল।",
                    "audio_script_bengali": "মুড়ি ঘণ্ট পুষ্টিকর!",
                    "phase": 2
                }
            ]

            response_data = {
                "title_bengali": "বৈচিত্র্যময় মেনু (পর্যায় ২)",
                "total_calories": 1520,
                "total_price_bdt": 780,
                "health_tip": "মাছে লেবু দিন।",
                "phase": 2,
                "confidence_score": 1.0,
                "items": phase_2_items
            }
            return json.dumps(response_data)

        # Phase 3: 4 hardcoded items with images
        if phase == 3:
            phase_3_items = [
                {
                    "name_bengali": "দেশি মুরগি ও কাঁচা পেঁপে স্টু",
                    "name_english": "Deshi Chicken with Raw Papaya",
                    "calories": 380,
                    "protein_g": 30.0,
                    "price_bdt": 180,
                    "image_prompt": "Deshi Chicken with Raw Papaya Stew",
                    "image_url": "/static/images/menu_3.jpg",
                    "benefits_key": "Digestive & Protein",
                    "recipe_bengali": "উপকরণ: মুরগি, কাঁচা পেঁপে।",
                    "audio_script_bengali": "দেশি মুরগি ও পেঁপে!",
                    "phase": 3
                },
                {
                    "name_bengali": "সয়া চাঙ্কস কারি (মাংসের বিকল্প)",
                    "name_english": "Soya Chunks Curry (Meat Alternative)",
                    "calories": 280,
                    "protein_g": 24.0,
                    "price_bdt": 60,
                    "image_prompt": "Soya Chunks Curry with Vegetables",
                    "image_url": "/static/images/menu_5.jpg",
                    "benefits_key": "Plant Protein",
                    "recipe_bengali": "উপকরণ: সয়া চাঙ্কস, আলু।",
                    "audio_script_bengali": "সয়া চাঙ্কস মাংসের বিকল্প!",
                    "phase": 3
                },
                {
                    "name_bengali": "বাটাসি মাছ ড্রাই ফ্রাই",
                    "name_english": "Batashi Fish Dry Fry",
                    "calories": 300,
                    "protein_g": 22.0,
                    "price_bdt": 120,
                    "image_prompt": "Batashi Fish Dry Fry with Onions",
                    "image_url": "/static/images/menu_1.jpg",
                    "benefits_key": "Calcium Rich",
                    "recipe_bengali": "উপকরণ: বাটাসি মাছ, পেঁয়াজ।",
                    "audio_script_bengali": "বাটাসি মাছে ক্যালসিয়াম!",
                    "phase": 3
                },
                {
                    "name_bengali": "গরুর মাংস ভুনা চুকাই পাতা দিয়ে",
                    "name_english": "Beef Bhuna with Chukai (Sour Leaves)",
                    "calories": 450,
                    "protein_g": 35.0,
                    "price_bdt": 220,
                    "image_prompt": "Beef Bhuna with Chukai Sour Leaves",
                    "image_url": "/static/images/menu_2.jpg",
                    "benefits_key": "Iron & Protein Boost",
                    "recipe_bengali": "উপকরণ: গরু, চুকাই পাতা।",
                    "audio_script_bengali": "গরুর মাংস আয়রন দেয়!",
                    "phase": 3
                }
            ]

            response_data = {
                "title_bengali": "বিশেষ মেনু (পর্যায় ৩)",
                "total_calories": 1410,
                "total_price_bdt": 580,
                "health_tip": "শাক খান প্রতিদিন।",
                "phase": 3,
                "confidence_score": 1.0,
                "items": phase_3_items
            }
            return json.dumps(response_data)

        # Phase 4+: Fallback
        fallback_menu = {
            "title_bengali": "সম্পূর্ণ মেনু দেখা হয়ে গেছে",
            "total_calories": 0,
            "total_price_bdt": 0,
            "health_tip": "সব মেনু দেখা শেষ!",
            "phase": phase,
            "confidence_score": 1.0,
            "items": []
        }
        return json.dumps(fallback_menu)
