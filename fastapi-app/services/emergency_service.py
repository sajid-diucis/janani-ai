from typing import List
from models import EmergencyCheckResponse
from config import settings

class EmergencyService:
    def __init__(self):
        self.emergency_keywords = settings.emergency_keywords
    
    async def check_emergency(self, text: str) -> EmergencyCheckResponse:
        """Check if text contains emergency keywords"""
        text_lower = text.lower()
        detected_keywords = []
        
        # Check for emergency keywords
        for keyword in self.emergency_keywords:
            if keyword.lower() in text_lower:
                detected_keywords.append(keyword)
        
        is_emergency = len(detected_keywords) > 0
        
        # Determine emergency level
        emergency_level = "normal"
        if is_emergency:
            # Critical keywords that require immediate attention
            critical_keywords = ["রক্তপাত", "রক্তস্রাব", "অজ্ঞান", "শ্বাসকষ্ট"]
            has_critical = any(keyword in detected_keywords for keyword in critical_keywords)
            emergency_level = "critical" if has_critical else "warning"
        
        # Generate recommendations
        recommendation = self._generate_recommendation(emergency_level, detected_keywords)
        urgent_action = self._generate_urgent_action(emergency_level) if is_emergency else None
        
        return EmergencyCheckResponse(
            is_emergency=is_emergency,
            emergency_level=emergency_level,
            detected_keywords=detected_keywords,
            recommendation=recommendation,
            urgent_action=urgent_action
        )
    
    def get_emergency_keywords(self) -> List[str]:
        """Get list of emergency keywords"""
        return self.emergency_keywords
    
    def _generate_recommendation(self, level: str, keywords: List[str]) -> str:
        """Generate recommendation based on emergency level"""
        if level == "critical":
            return "🚨 জরুরি! অবিলম্বে নিকটস্থ হাসপাতালে যান বা জরুরি সেবা কলে (999) যোগাযোগ করুন।"
        elif level == "warning":
            return "⚠️ সতর্কতা: এই লক্ষণগুলো গুরুতর হতে পারে। যত তাড়াতাড়ি সম্ভব ডাক্তারের সাথে যোগাযোগ করুন।"
        else:
            return "আপনার স্বাস্থ্য ভালো আছে। নিয়মিত চেকআপ করান।"
    
    def _generate_urgent_action(self, level: str) -> str:
        """Generate urgent action steps"""
        if level == "critical":
            return """অবিলম্বে:
1. হাসপাতালে যান বা অ্যাম্বুলেন্স ডাকুন
2. পরিবারকে জানান
3. জরুরি হটলাইন: 999"""
        elif level == "warning":
            return """যত তাড়াতাড়ি সম্ভব:
1. ডাক্তারের সাথে যোগাযোগ করুন
2. লক্ষণগুলো নোট করুন
3. বিশ্রাম নিন"""
        return None