import asyncio
from typing import Dict, Any, Optional
from config import settings
from services.ai_service import AIService
from services.speech_service import speech_service
from services.pose_analysis_service import pose_analysis_service

class CoachingService:
    def __init__(self):
        self.ai_service = AIService() # Re-use existing AI service logic

    def _rule_based_advice(self, visual_description: str, user_voice_text: str) -> Dict[str, Any]:
        voice_text = (user_voice_text or "").strip().lower()
        vision = (visual_description or "").lower()

        is_question = "?" in user_voice_text or any(q in voice_text for q in ["why", "how", "where", "when", "what"])
        if "no hands" in vision or "no hand" in vision:
            return {"text": "Show your hands in front of the camera.", "tone": "urgent", "is_correction": True}
        if "too high" in vision:
            return {"text": "Lower your hands and place them just below the navel.", "tone": "urgent", "is_correction": True}
        if "too low" in vision:
            return {"text": "Raise your hands slightly to just below the navel.", "tone": "urgent", "is_correction": True}
        if "off-center" in vision:
            return {"text": "Move to the center and keep your hands inside the red circle.", "tone": "urgent", "is_correction": True}
        if "static" in vision:
            return {"text": "Press firmly and move in a clockwise circle.", "tone": "urgent", "is_correction": True}
        if "circular" in vision or "correctly positioned" in vision:
            if is_question:
                return {"text": "Keep steady pressure and continue circular motion.", "tone": "calm", "is_correction": False}
            return {"text": "Good job. Keep the same pressure and motion.", "tone": "calm", "is_correction": False}
        if is_question:
            return {"text": "Press firmly just below the navel and move in slow circles.", "tone": "calm", "is_correction": False}
        return {"text": "Press firmly just below the navel and circle slowly.", "tone": "calm", "is_correction": False}

    async def get_coaching_advice(self, 
                                step: str, 
                                visual_description: str, 
                                user_voice_text: str = "") -> Dict[str, Any]:
        """
        Orchestrates the reasoning layer:
        1. Builds the context.
        2. Calls DeepSeek (via AsyncOpenAI in AIService).
        3. Returns text + metadata for TTS.
        """
        
        # 1. Construct System Prompt
        system_prompt = """
        You are a WHO Emergency First Aid Coach.
        Your goal is to guide a layperson through a medical procedure.
        
        INPUTS:
        - Current Protocol Step
        - Visual Observation (what the AI sees)
        - User's Voice (what the user just said)
        
        OUTPUT RULES:
        1. Keep responses under 30 words.
        2. Be imperative and clear.
        3. If the user is doing it WRONG (based on vision), correct them immediately (Urgent Tone).
        4. If the user is doing it RIGHT, encourage them briefly (Calm Tone).
        5. If the user asks a question, answer concisely.
        
        Output JSON:
        {
            "text": "Your spoken response here.",
            "tone": "urgent" | "calm",
            "is_correction": boolean
        }
        """

        # 2. Construct User Message
        user_message = f"""
        STEP: {step}
        VISION: {visual_description}
        USER SAID: "{user_voice_text}"
        """

        # 3. Call AI (Using DeepSeek if configured, else Gemini)
        # We leverage the existing get_response but need to force JSON mode manually here 
        # or use a specialized call. Since ai_service.get_response is general, let's use the client directly if possible
        # or wrap it.
        
        try:
            # We prefer DeepSeek for reasoning as per instructions
            client = self.ai_service.client if self.ai_service.client else self.ai_service.gemini_client
            model = "deepseek-chat" if self.ai_service.client else settings.gemini_model_id
            
            if not client:
                return self._rule_based_advice(visual_description, user_voice_text)

            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=100,
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            import json
            result = json.loads(content)
            return result

        except Exception as e:
            print(f"Coaching Logic Error: {e}")
            return self._rule_based_advice(visual_description, user_voice_text)

coaching_service = CoachingService()
