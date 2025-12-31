"""
DeepSeek Service Wrapper
Wrapper around AIService for food RAG pipeline
"""
from services.ai_service import AIService

class DeepSeekService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def chat(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Simple chat wrapper for DeepSeek
        """
        return await self.ai_service.get_response(
            message=prompt,
            conversation_history=[],
            is_emergency=False,
            user_context=None
        )

# Global instance
deepseek_service = DeepSeekService()
