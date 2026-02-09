"""
Janani AI - Omniscient Agent Brain
DeepMind-Style Architecture for Digital Midwife
Uses OpenAI client with Gemini via OneBrain Proxy
"""

import os
import base64
import json
import re
from typing import Optional, Dict, List, Any
from openai import OpenAI
from pydantic import BaseModel, Field

# Import demo configuration for hackathon modes
try:
    from config_demo import get_demo_config, print_current_config
    DEMO_CONFIG = get_demo_config()
    print_current_config()
except ImportError:
    DEMO_CONFIG = None


class PatientState(BaseModel):
    """
    Master JSON - Complete Patient Context
    The Agent knows EVERYTHING before answering.
    """
    user_id: str = "anonymous"
    name: str = "Unknown"
    weeks_pregnant: int = 0
    trimester: str = "unknown"
    age: int = 0
    risks: List[str] = Field(default_factory=list)
    conditions: List[str] = Field(default_factory=list)
    last_symptoms: List[str] = Field(default_factory=list)
    recent_concerns: List[str] = Field(default_factory=list)
    blood_pressure: Optional[str] = None
    hemoglobin: Optional[float] = None
    last_checkup: Optional[str] = None


class JananiAgent:
    """
    The Omniscient Agent - Knows Patient Context Before Responding
    """
    
    def __init__(self):
        self._client = None
        self.model = os.getenv("GEMINI_MODEL_ID", "google/gemini-2.0-flash-exp:free")
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client (OpenRouter/Gemini)"""
        if self._client is None:
            # Try loading from dotenv first
            try:
                from dotenv import load_dotenv
                from pathlib import Path
                env_path = Path(__file__).resolve().parent.parent / ".env"
                load_dotenv(dotenv_path=env_path)
            except:
                pass
            
            # Use OpenRouter API for Gemini
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                # Fallback to DeepSeek if OpenRouter not configured
                api_key = os.getenv("DEEPSEEK_API_KEY")
                self._client = OpenAI(
                    api_key=api_key or "dummy-key",
                    base_url="https://api.deepseek.com/v1",
                    timeout=120.0
                )
                self.model = "deepseek-chat"
            else:
                # Use OpenRouter (Gemini)
                self._client = OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                    timeout=60.0,
                    default_headers={
                        "HTTP-Referer": "https://janani-ai.app",
                        "X-Title": "Janani AI - Digital Midwife"
                    }
                )
                self.model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
                print(f"🚀 Using OpenRouter with model: {self.model}")
        return self._client
    
    @property
    def groq_client(self):
        """Lazy initialization of Groq client for Vision"""
        if not hasattr(self, '_groq_client') or self._groq_client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                try:
                    from dotenv import load_dotenv
                    load_dotenv()
                    api_key = os.getenv("GROQ_API_KEY")
                except:
                    pass
            
            self._groq_client = OpenAI(
                api_key=api_key or "dummy-key-for-vision",
                base_url="https://api.groq.com/openai/v1",
                timeout=120.0
            )
        return self._groq_client

    def _build_system_instruction(self, state: Dict[str, Any]) -> str:
        """
        Inject patient state directly into system prompt.
        """
        return f"""
# ROLE: Janani AI - Digital Midwife for Rural Bangladesh

You are "Janani", an empathetic, WHO-trained Digital Midwife. You speak in warm, colloquial Bengali (Cholitobhasha).

## CRITICAL: COMPLETE PATIENT CONTEXT:
```json
{state}
```

## YOUR BEHAVIOR:
1. **CONTEXT-AWARE**: Reference patient details (week, risks).
2. **WHO GUIDELINES**: Detect RED FLAGS (Headache+Vision=Preeclampsia, Bleeding=Emergency).
3. **EMPATHY FIRST**: Validate feelings before advising.
4. **LANGUAGE**: Colloquial Bengali (Cholitobhasha).

## RESPONSE FORMAT (IMPORTANT FOR JUDGES):
Structure EVERY response like this:

💬 [Your empathetic Bengali response here]

🇬🇧 **English Translation:** [Provide a clear English translation of the Bengali response]

📋 **WHO Guideline:** [State which WHO/medical guideline you followed, e.g., "WHO recommends 30-60mg iron daily during pregnancy" or "WHO danger sign: severe headache with vision changes indicates preeclampsia risk"]

## ACTION TAGS:
Append action tags at the end if applicable:
- [ACTION: SHOW_FOOD_MENU]: If user asks about diet, food, menu, budget.
- [ACTION: NAVIGATE_CARE_PLAN]: If user asks about exercises, care plan, or "what should I do".
- [ACTION: UPDATE_PROFILE]: If user provides name, age, or pregnancy week.
- [ACTION: NAVIGATE_AR_DASHBOARD]: Only for severe medical emergencies (bleeding, etc).

Example Response:
"💬 আপনি সবুজ শাকসবজি আর কলিজা খেতে পারেন। এগুলো আয়রন সমৃদ্ধ।

🇬🇧 **English Translation:** You can eat green leafy vegetables and liver. These are rich in iron.

📋 **WHO Guideline:** WHO recommends iron-rich foods and 30-60mg iron supplementation during pregnancy to prevent anemia.

[ACTION: SHOW_FOOD_MENU]"
"""

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def _get_image_mime_type(self, image_path: str) -> str:
        """Get MIME type from file extension"""
        ext = image_path.lower().split(".")[-1]
        mime_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp"
        }
        return mime_types.get(ext, "image/jpeg")

    def _build_structured_instruction(self, state: Dict[str, Any]) -> str:
        return f"""
# ROLE: Janani AI - Digital Midwife for Rural Bangladesh

You are "Janani", an empathetic, WHO-trained Digital Midwife. You speak in warm, colloquial Bengali (Cholitobhasha).

## CRITICAL: COMPLETE PATIENT CONTEXT:
```json
{state}
```

## YOUR BEHAVIOR:
1. CONTEXT-AWARE: Reference patient details (week, risks).
2. WHO GUIDELINES: Detect RED FLAGS (Headache+Vision=Preeclampsia, Bleeding=Emergency).
3. EMPATHY FIRST: Validate feelings before advising.
4. LANGUAGE: Colloquial Bengali (Cholitobhasha).

## OUTPUT FORMAT
Return ONLY a JSON object with these fields:
{{
  "response": "string (Your empathetic Bengali response. Then add a new line and '🇬🇧 English Translation: ' followed by the English translation.)",
  "tool_call": "NONE | GENERATE_FOOD_MENU | GET_CARE_PLAN | CHECK_FOOD_SAFETY | UPDATE_PROFILE | ACTIVATE_EMERGENCY | EXECUTE_EXTERNAL_TASK",
  "tool_params": {{}},
  "action": "NONE | SHOW_FOOD_MENU | NAVIGATE_CARE_PLAN | NAVIGATE_AR_DASHBOARD",
  "emergency_confidence": 0.0
}}

## TOOL RULES
Use ACTIVATE_EMERGENCY only for explicit emergency cases (bleeding, seizure, unconscious, severe danger).
Set emergency_confidence between 0 and 1.
If tool_call is NONE then action must be NONE.
Use GENERATE_FOOD_MENU only when user asks for menu, diet, budget, or food list, and then action must be SHOW_FOOD_MENU.
Use GET_CARE_PLAN only when user asks about care plan, weekly guidance, or exercises, and then action must be NAVIGATE_CARE_PLAN.
Use UPDATE_PROFILE only when user explicitly provides name, age, or pregnancy week.
"""

    def _build_classifier_instruction(self, state: Dict[str, Any]) -> str:
        return f"""
You are a strict classifier. Decide the tool_call based only on the user query.
Output ONLY one of these tokens, nothing else:
NONE
GENERATE_FOOD_MENU
GET_CARE_PLAN
CHECK_FOOD_SAFETY
UPDATE_PROFILE
ACTIVATE_EMERGENCY
EXECUTE_EXTERNAL_TASK
Rules:
- ACTIVATE_EMERGENCY only for explicit emergencies (bleeding, seizure, unconscious).
- GENERATE_FOOD_MENU only when user asks for menu, diet, budget, or food list.
- GET_CARE_PLAN only when user asks about care plan, weekly guidance, or exercises.
- UPDATE_PROFILE only when user provides name, age, or pregnancy week.
"""

    async def ask(
        self, 
        query: str, 
        state: Dict[str, Any], 
        image_path: Optional[str] = None,
        image_base64: Optional[str] = None
    ) -> str:
        """
        The Agent Thinks - Returns PLAIN TEXT with TAGS
        """
        system_instruction = self._build_system_instruction(state)
        
        has_image = (image_path and os.path.exists(image_path)) or image_base64
        response_content = ""
        
        if has_image:
            final_image_b64 = image_base64
            mime_type = "image/jpeg"
            if image_path:
                final_image_b64 = self._encode_image_to_base64(image_path)
                mime_type = self._get_image_mime_type(image_path)
                
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"{system_instruction}\n\nUSER QUERY: {query}"}, 
                                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{final_image_b64}"}}
                            ]
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.5
                )
                response_content = response.choices[0].message.content.strip()
            except Exception as e:
                return f"ছবি বিশ্লেষণে সমস্যা হয়েছে। (Error: {str(e)[:50]})"

        else:
            try:
                # Use demo config values if available
                max_tokens = DEMO_CONFIG.max_tokens if DEMO_CONFIG else 1000
                temperature = DEMO_CONFIG.temperature if DEMO_CONFIG else 0.7
                
                response = self.client.chat.completions.create(
                    model=self.model,  # Uses OpenRouter model or fallback
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                response_content = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"❌ AI Agent Error: {e}")
                return f"দুঃখিত, সমস্যা হয়েছে। (Error: {str(e)[:50]})"
        
        # SAFETY NET: Ensure action tags are present using deterministic rules
        response_content = self._ensure_action_tags(response_content, query)
        
        return response_content

    async def ask_structured(
        self,
        query: str,
        state: Dict[str, Any],
        image_path: Optional[str] = None,
        image_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        system_instruction = self._build_structured_instruction(state)
        response_content = ""
        try:
            max_tokens = DEMO_CONFIG.max_tokens if DEMO_CONFIG else 1000
            temperature = DEMO_CONFIG.temperature if DEMO_CONFIG else 0.4
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
            except Exception:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            response_content = response.choices[0].message.content.strip()
        except Exception as e:
            return {
                "response": f"দুঃখিত, সমস্যা হয়েছে। (Error: {str(e)[:50]})",
                "tool_call": "NONE",
                "tool_params": {},
                "action": "NONE",
                "emergency_confidence": 0.0
            }
        response_text = self._extract_response_text(response_content)
        json_text = response_content.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", json_text, re.IGNORECASE)
        if fence_match:
            json_text = fence_match.group(1).strip()
        match = re.search(r"\{[\s\S]*\}", json_text)
        if match:
            json_text = match.group(0).strip()
        json_text = re.sub(r",\s*}", "}", json_text)
        json_text = re.sub(r",\s*]", "]", json_text)
        try:
            parsed = json.loads(json_text)
        except Exception:
            parsed = {}
        if not parsed or not parsed.get("tool_call") or parsed.get("tool_call") == "NONE":
            classified = await self._classify_tool(query, state)
            return {
                "response": response_text,
                "tool_call": classified.get("tool_call") or "NONE",
                "tool_params": classified.get("tool_params") or {},
                "action": classified.get("action") or "NONE",
                "emergency_confidence": float(classified.get("emergency_confidence") or 0.0)
            }
        return {
            "response": str(parsed.get("response") or "").strip() or response_text,
            "tool_call": parsed.get("tool_call") or "NONE",
            "tool_params": parsed.get("tool_params") or {},
            "action": parsed.get("action") or "NONE",
            "emergency_confidence": float(parsed.get("emergency_confidence") or 0.0)
        }

    def _extract_response_text(self, response_content: str) -> str:
        json_text = response_content.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", json_text, re.IGNORECASE)
        if fence_match:
            json_text = fence_match.group(1).strip()
        match = re.search(r"\{[\s\S]*\}", json_text)
        if match:
            json_text = match.group(0).strip()
        json_text = re.sub(r",\s*}", "}", json_text)
        json_text = re.sub(r",\s*]", "]", json_text)
        try:
            parsed = json.loads(json_text)
        except Exception:
            parsed = {}
        response_text = str(parsed.get("response") or "").strip()
        return response_text or response_content

    async def _classify_tool(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        system_instruction = self._build_classifier_instruction(state)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": query}
                ],
                max_tokens=300,
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content.strip()
        except Exception:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=300,
                    temperature=0.0
                )
                raw = response.choices[0].message.content.strip()
            except Exception:
                return {
                    "tool_call": "NONE",
                    "tool_params": {},
                    "action": "NONE",
                    "emergency_confidence": 0.0
                }
        json_text = raw.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", json_text, re.IGNORECASE)
        if fence_match:
            json_text = fence_match.group(1).strip()
        match = re.search(r"\{[\s\S]*\}", json_text)
        if match:
            json_text = match.group(0).strip()
        json_text = re.sub(r",\s*}", "}", json_text)
        json_text = re.sub(r",\s*]", "]", json_text)
        try:
            parsed = json.loads(json_text)
        except Exception:
            parsed = {}
        tool_call = parsed.get("tool_call")
        if not tool_call:
            for opt in [
                "ACTIVATE_EMERGENCY",
                "GENERATE_FOOD_MENU",
                "GET_CARE_PLAN",
                "CHECK_FOOD_SAFETY",
                "UPDATE_PROFILE",
                "EXECUTE_EXTERNAL_TASK",
                "NONE"
            ]:
                if re.search(rf"\b{opt}\b", raw):
                    tool_call = opt
                    break
        if not tool_call:
            tool_call = "NONE"
        if tool_call == "NONE":
            ql = query.lower()
            emergency_keywords = ["রক্তপাত", "bleeding", "unconscious", "অজ্ঞান", "seizure", "খিঁচুনি"]
            menu_keywords = ["মেনু", "খাবার তালিকা", "diet", "menu", "food list", "food plan", "বাজেট", "budget"]
            care_keywords = ["কেয়ার প্ল্যান", "care plan", "weekly plan", "সপ্তাহ", "exercise", "ব্যায়াম"]
            safety_keywords = ["খেতে পারি", "safe", "নিরাপদ", "can i eat", "খাওয়া যাবে"]
            profile_keywords = ["আমার নাম", "name is", "my name", "বয়স", "age", "সপ্তাহ চলছে", "weeks pregnant"]
            if any(k in ql for k in emergency_keywords):
                tool_call = "ACTIVATE_EMERGENCY"
            elif any(k in ql for k in menu_keywords):
                tool_call = "GENERATE_FOOD_MENU"
            elif any(k in ql for k in care_keywords):
                tool_call = "GET_CARE_PLAN"
            elif any(k in ql for k in safety_keywords):
                tool_call = "CHECK_FOOD_SAFETY"
            elif any(k in ql for k in profile_keywords):
                tool_call = "UPDATE_PROFILE"
        action_map = {
            "GENERATE_FOOD_MENU": "SHOW_FOOD_MENU",
            "GET_CARE_PLAN": "NAVIGATE_CARE_PLAN",
            "ACTIVATE_EMERGENCY": "NAVIGATE_AR_DASHBOARD"
        }
        emergency_confidence = float(parsed.get("emergency_confidence") or 0.0)
        if tool_call == "ACTIVATE_EMERGENCY" and emergency_confidence == 0.0:
            emergency_confidence = 1.0
        return {
            "tool_call": tool_call,
            "tool_params": parsed.get("tool_params") or {},
            "action": parsed.get("action") or action_map.get(tool_call, "NONE"),
            "emergency_confidence": emergency_confidence
        }
    
    def _ensure_action_tags(self, response: str, query: str) -> str:
        """
        Redundant Intent Detection (The Safety Net)
        If the LLM forgot to add [ACTION: ...] tags, we add them based on keywords.
        """
        import re
        
        # If response already has an action tag, trust the LLM
        if "[ACTION:" in response:
            return response
        
        # Combine query + response for keyword detection
        combined_text = (query + " " + response).lower()
        
        # Bengali digit translation table
        trans_table = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
        normalized_text = combined_text.translate(trans_table)
        
        # Intent Detection Rules (Prioritized)
        detected_tag = None
        
        # 1. EMERGENCY (Highest Priority)
        emergency_keywords = ["রক্তপাত", "bleeding", "জরুরি", "emergency", "খিঁচুনি", "seizure", "অজ্ঞান", "unconscious"]
        if any(kw in combined_text for kw in emergency_keywords):
            # Granular Emergency Detection
            if any(k in combined_text for k in ["রক্তপাত", "bleeding", "hemorrhage"]):
                detected_tag = "[ACTION: NAVIGATE_AR_DASHBOARD:BLEEDING]"
            elif any(k in combined_text for k in ["খিঁচুনি", "seizure", "fit", "convulsion"]):
                detected_tag = "[ACTION: NAVIGATE_AR_DASHBOARD:SEIZURE]"
            elif any(k in combined_text for k in ["শ্বাস", "breath", "baby", "newborn", "বাচ্চা"]):
                detected_tag = "[ACTION: NAVIGATE_AR_DASHBOARD:NEWBORN]"
            elif any(k in combined_text for k in ["labor", "delivery", "pain", "ব্যথা", "প্রসব"]):
                detected_tag = "[ACTION: NAVIGATE_AR_DASHBOARD:LABOR]"
            else:
                detected_tag = "[ACTION: NAVIGATE_AR_DASHBOARD:LABOR]" # Default fallback

        
        # 2. FOOD MENU
        elif any(kw in combined_text for kw in ["মেনু", "menu", "খাবার তালিকা", "food list", "বাজেট", "budget", "টাকা", "taka"]):
            detected_tag = "[ACTION: SHOW_FOOD_MENU]"
        
        # 3. CARE PLAN
        elif any(kw in combined_text for kw in ["কেয়ার প্ল্যান", "care plan", "সপ্তাহ", "weekly", "ব্যায়াম", "exercise", "কী করব", "what should i do"]):
            detected_tag = "[ACTION: NAVIGATE_CARE_PLAN]"
        
        # 4. DOCTOR CALL
        elif any(kw in combined_text for kw in ["ডাক্তার", "doctor", "ডাকো", "call", "অ্যাপয়েন্টমেন্ট", "appointment"]):
            detected_tag = "[ACTION: CONNECT_DOCTOR]"
        
        # 5. FOOD SAFETY CHECK
        elif any(kw in combined_text for kw in ["খেতে পারি", "can i eat", "নিরাপদ", "safe", "খাওয়া যাবে"]):
            detected_tag = "[ACTION: CHECK_FOOD_SAFETY]"
        
        # 6. PROFILE UPDATE
        elif any(kw in combined_text for kw in ["আমার নাম", "my name is", "বয়স", "age", "সপ্তাহ চলছে"]):
            detected_tag = "[ACTION: UPDATE_PROFILE]"
        
        # Append detected tag if found
        if detected_tag:
            print(f"🤖 SAFETY NET: LLM forgot tag. Appending: {detected_tag}")
            response = response.strip() + f" {detected_tag}"
        
        return response


# Singleton Agent Instance
janani_agent = JananiAgent()


async def ask_janani_agent(
    query: str, 
    state: Dict[str, Any], 
    image_path: Optional[str] = None,
    image_base64: Optional[str] = None
) -> str:
    """
    Main entry point for the Agent
    Returns raw string with [ACTION: TAGS]
    """
    return await janani_agent.ask(query, state, image_path, image_base64)


async def ask_janani_agent_structured(
    query: str,
    state: Dict[str, Any],
    image_path: Optional[str] = None,
    image_base64: Optional[str] = None
) -> Dict[str, Any]:
    return await janani_agent.ask_structured(query, state, image_path, image_base64)
