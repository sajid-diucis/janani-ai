"""
Digital Midwife - Emergency Bridge System
Connects patients to emergency services with AR guidance support
"""
from typing import Dict, List, Optional
from datetime import datetime
import uuid

from models.care_models import (
    EmergencyBridgeRequest, EmergencyBridgeResponse,
    RedFlagType, RiskLevel
)


import json
import os
from services.location_service import location_service

class EmergencyBridgeService:
    """
    Emergency Bridge System that:
    1. Activates when critical red flags are detected
    2. Provides step-by-step emergency guidance in Bengali
    3. Prepares data for AR overlay (MediaPipe integration)
    4. Connects to emergency services
    5. Real-time location checking for nearest hospitals and volunteers
    """
    
    def __init__(self):
        # Emergency contact database (Bangladesh)
        self.emergency_contacts = {
            "national": "999",
            "ambulance": "999",
            "health_hotline": "16789",
            "maternal_health": "16263"
        }
        
        # Load hospital database from JSON
        self.hospitals = self._load_json_data("hospitals.json", [
            {
                "id": "hosp_default",
                "name": "ঢাকা মেডিকেল কলেজ হাসপাতাল",
                "name_en": "Dhaka Medical College Hospital",
                "address": "Ramna, Dhaka",
                "lat": 23.7258,
                "lng": 90.3973,
                "phone": "02-55165001",
                "has_maternity": True,
                "type": "government"
            }
        ])
        
        # Load volunteer database from JSON
        self.volunteers = self._load_json_data("volunteers.json", [])
        
        # Emergency guidance by type
        self._load_emergency_protocols()

    def _load_json_data(self, filename: str, default: List) -> List:
        """Load data from JSON file in data directory"""
        try:
            # Try multiple possible paths to data directory
            paths = [
                os.path.join("data", filename),
                os.path.join("fastapi-app", "data", filename),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", filename)
            ]
            
            for path in paths:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
            return default
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return default
    
    def _load_emergency_protocols(self):
        """Load emergency guidance protocols"""
        
        self.emergency_protocols = {
            RedFlagType.HEMORRHAGE: {
                "name_bn": "অতিরিক্ত রক্তপাত (Hemorrhage)",
                "severity": "critical",
                "immediate_steps": [
                    "🚨 এখনই 999 কল করুন বা নিকটস্থ হাসপাতালে জান",
                    "সোজা হয়ে শুয়ে পড়ুন এবং পা ২-৩টি বালিশ দিয়ে উঁচু করে রাখুন (Shock Position)",
                    "তলপেটে জরায়ু মালিশ করুন যদি প্রসব পরবর্তী রক্তপাত হয়",
                    "রক্তাক্ত প্যাড বা কাপড় গুনে রাখুন যা ডাক্তারকে দেখাতে হবে",
                    "শরীরে গরম কাপড় বা কম্বল জড়িয়ে রাখুন",
                    "পানি বা খাবার একদম খাবেন না"
                ],
                "do_not": [
                    "❌ হাঁটাচলা করবেন না",
                    "❌ টয়লেটে যাওয়ার চেষ্টা করবেন না",
                    "❌ কোনো ওষুধ (ব্যথানাশক) খাবেন না"
                ],
                "ar_guidance": "hemorrhage_first_aid"
            },
            
            RedFlagType.ECLAMPSIA: {
                "name_bn": "খিঁচুনি/এক্লাম্পসিয়া",
                "severity": "critical",
                "immediate_steps": [
                    "🚨 এখনই 999 কল করুন",
                    "রোগীকে কাত করে শোয়ান (বাম দিকে)",
                    "মাথার নিচে নরম কিছু দিন",
                    "আঁটসাঁট কাপড় ঢিলা করুন",
                    "মুখে কিছু দেবেন না"
                ],
                "do_not": [
                    "❌ জোর করে ধরবেন না",
                    "❌ মুখে আঙুল বা চামচ দেবেন না",
                    "❌ পানি বা ওষুধ খাওয়াবেন না"
                ],
                "ar_guidance": "eclampsia_position"
            },
            
            RedFlagType.PREECLAMPSIA: {
                "name_bn": "প্রি-এক্লাম্পসিয়া",
                "severity": "critical",
                "immediate_steps": [
                    "🚨 এখনই হাসপাতালে যান",
                    "বাম কাত হয়ে শুয়ে থাকুন",
                    "অন্ধকার ও শান্ত ঘরে থাকুন",
                    "রক্তচাপ মাপুন (যদি সম্ভব হয়)"
                ],
                "do_not": [
                    "❌ লবণ খাবেন না",
                    "❌ একা যাবেন না",
                    "❌ দেরি করবেন না"
                ],
                "ar_guidance": "bp_monitoring"
            },
            
            RedFlagType.PRETERM_LABOR: {
                "name_bn": "সময়ের আগে প্রসব বেদনা",
                "severity": "critical",
                "immediate_steps": [
                    "🚨 এখনই হাসপাতালে যান",
                    "বাম কাত হয়ে শুয়ে পড়ুন",
                    "প্রচুর পানি পান করুন",
                    "সংকোচনের সময় ও বিরতি নোট করুন"
                ],
                "do_not": [
                    "❌ হাঁটাচলা করবেন না",
                    "❌ বাথরুমে দীর্ঘ সময় থাকবেন না",
                    "❌ ভারী কাজ করবেন না"
                ],
                "ar_guidance": "contraction_timing"
            },
            
            RedFlagType.RUPTURE_OF_MEMBRANES: {
                "name_bn": "পানি ভাঙা",
                "severity": "critical",
                "immediate_steps": [
                    "🚨 এখনই হাসপাতালে যান",
                    "শুয়ে পড়ুন",
                    "প্যাড ব্যবহার করুন, পরিমাণ দেখুন",
                    "পানির রং নোট করুন (স্বচ্ছ/সবুজ/হলুদ)",
                    "সময় নোট করুন"
                ],
                "do_not": [
                    "❌ গোসল করবেন না",
                    "❌ যৌন সম্পর্ক করবেন না",
                    "❌ ট্যাম্পন ব্যবহার করবেন না"
                ],
                "ar_guidance": "rom_guidance"
            },
            
            RedFlagType.FETAL_DISTRESS: {
                "name_bn": "বাচ্চার নড়াচড়া কমে যাওয়া",
                "severity": "critical",
                "immediate_steps": [
                    "🚨 এখনই হাসপাতালে যান",
                    "বাম কাত হয়ে শুন",
                    "ঠান্ডা পানি পান করুন",
                    "১০টি নড়াচড়া গুনুন - ২ ঘণ্টায় ১০ না হলে জরুরি"
                ],
                "do_not": [
                    "❌ দেরি করবেন না",
                    "❌ অপেক্ষা করবেন না 'আবার নড়বে'"
                ],
                "ar_guidance": "kick_count"
            },
            
            RedFlagType.INFECTION: {
                "name_bn": "সংক্রমণ/জ্বর",
                "severity": "high",
                "immediate_steps": [
                    "⚠️ আজকেই ডাক্তার দেখান",
                    "জ্বর মাপুন ও নোট করুন",
                    "প্রচুর পানি পান করুন",
                    "প্যারাসিটামল খেতে পারেন (৫০০mg)"
                ],
                "do_not": [
                    "❌ অ্যাসপিরিন বা আইবুপ্রোফেন খাবেন না",
                    "❌ মিসো/সাইটো খাবেন না"
                ],
                "ar_guidance": None
            }
        }
        
        # Labor guidance for AR (when labor starts)
        self.labor_ar_guidance = {
            "early_labor": {
                "name_bn": "প্রথম পর্যায়",
                "guidance": [
                    "শ্বাস নিন: নাক দিয়ে ভেতরে, মুখ দিয়ে বাহিরে",
                    "হাঁটাচলা করতে পারেন",
                    "হালকা খাবার খান",
                    "পানি পান করুন"
                ],
                "ar_overlay": "breathing_exercise_1"
            },
            "active_labor": {
                "name_bn": "সক্রিয় প্রসব",
                "guidance": [
                    "৪-১-৪ শ্বাস: ৪ সেকেন্ড ভেতরে, ১ সেকেন্ড ধরুন, ৪ সেকেন্ড বাহিরে",
                    "আরামদায়ক পজিশন নিন",
                    "সাপোর্ট পারসনকে কাছে রাখুন"
                ],
                "ar_overlay": "breathing_exercise_2"
            },
            "pushing": {
                "name_bn": "পুশিং পর্যায়",
                "guidance": [
                    "ডাক্তার/মিডওয়াইফের নির্দেশ মানুন",
                    "সংকোচনের সময় পুশ করুন",
                    "বিরতিতে বিশ্রাম নিন"
                ],
                "ar_overlay": "pushing_position"
            }
        }
    
    async def activate_emergency_bridge(
        self,
        request: EmergencyBridgeRequest
    ) -> EmergencyBridgeResponse:
        """
        Activate the emergency bridge when critical situation detected.
        """
        bridge_id = str(uuid.uuid4())[:8]
        
        # Determine the primary emergency type
        primary_emergency = request.red_flags[0] if request.red_flags else RedFlagType.HEMORRHAGE
        protocol = self.emergency_protocols.get(
            primary_emergency, 
            self.emergency_protocols[RedFlagType.HEMORRHAGE]
        )
        
        # Get patient location
        lat = None
        lng = None
        if request.patient_location:
            lat = request.patient_location.get("latitude") or request.patient_location.get("lat")
            lng = request.patient_location.get("longitude") or request.patient_location.get("lng")
        
        # Find nearest hospital using location service
        nearby_hospitals = location_service.find_nearest(lat, lng, self.hospitals, limit=1)
        nearest_hospital = nearby_hospitals[0] if nearby_hospitals else self.hospitals[0]
        
        print(f"Emergency activated! Lat: {lat}, Lng: {lng}. Nearest Hospital: {nearest_hospital['name']}")
        
        # Find nearest volunteers
        nearest_volunteers = location_service.find_nearest(lat, lng, self.volunteers, limit=2)
        print(f"Found {len(nearest_volunteers)} nearby volunteers.")

        # Personalized Logic
        personalized_steps = protocol["immediate_steps"][:]
        if request.patient_profile:
            profile = request.patient_profile
            # 1. Trimester specific advice
            week = profile.get("current_week", 20)
            if week > 28: # 3rd trimester
                personalized_steps.append("🦶 বাচ্চার নড়াচড়া খেয়াল করুন")
            
            # 2. Blood group awareness
            blood_group = profile.get("blood_group")
            if blood_group:
                personalized_steps.append(f"🩸 আপনার ব্লাড গ্রুপ ({blood_group}) হাসপাতালে জানান")
            
            # 3. High risk history
            if profile.get("overall_risk_level") == "high":
                personalized_steps.insert(0, "⚠️ আপনার রিস্ক প্রোফাইল হাই, দ্রুত হাসপাতালে পৌঁছানো জরুরি")
        
        # Generate voice guidance with location awareness
        voice_text = self._generate_emergency_voice_guidance(
            protocol["name_bn"],
            personalized_steps,
            nearest_hospital["name"]
        )
        
        return EmergencyBridgeResponse(
            bridge_id=bridge_id,
            status="activated",
            immediate_steps_bengali=personalized_steps,
            do_not_do_bengali=protocol["do_not"],
            emergency_number=self.emergency_contacts["national"],
            nearest_hospital=nearest_hospital["name"],
            hospital_phone=nearest_hospital["phone"],
            hospital_distance_km=nearest_hospital.get("distance_km"),
            hospital_lat=nearest_hospital.get("lat"),
            hospital_lng=nearest_hospital.get("lng"),
            emergency_unit=nearest_hospital.get("emergency_unit"),
            available_doctors=nearest_hospital.get("doctors", []),
            ar_guidance_available=protocol.get("ar_guidance") is not None,
            ar_guidance_type=protocol.get("ar_guidance"),
            voice_guidance_text=voice_text,
            estimated_response_time=f"{max(10, int(nearest_hospital.get('distance_km', 10) * 2.5))} মিনিট",
            ambulance_dispatched=False,
            nearest_volunteers=nearest_volunteers
        )
    
    def _generate_emergency_voice_guidance(
        self, 
        emergency_name: str, 
        steps: List[str],
        hospital_name: str = ""
    ) -> str:
        """Generate calm but urgent voice guidance for emergency (Digital Midwife Persona)"""
        
        intro = f"আপু, শান্ত হোন। আপনার {emergency_name} এর লক্ষণ দেখে মনে হচ্ছে আমাদের এখনই ব্যবস্থা নিতে হবে।"
        steps_text = " ".join([step.replace("🚨", "").replace("❌", "").strip() for step in steps[:2]])
        
        hospital_info = ""
        if hospital_name:
            hospital_info = f"নিকটস্থ {hospital_name} হাসপাতালে পৌঁছানো এখন সবচেয়ে জরুরি। আমরা আগে থেকেই ডাক্তারদের জানিয়ে রাখছি।"
            
        outro = "আমি আপনার পাশেই আছি। ভয় পাবেন না, সব ঠিক হয়ে যাবে ইনশাআল্লাহ।"
        
        return f"{intro} {steps_text} {hospital_info} {outro}"
    
    def get_ar_guidance_data(self, guidance_type: str) -> Optional[Dict]:
        """
        Get AR overlay data for MediaPipe integration.
        Returns visual instructions for delivery/emergency situations.
        """
        ar_data = {
            "hemorrhage_first_aid": {
                "type": "position",
                "title_bn": "শোয়ার পজিশন",
                "instructions": [
                    {"step": 1, "text_bn": "সোজা শুয়ে পড়ুন", "pose_key": "lying_flat"},
                    {"step": 2, "text_bn": "পা উঁচু করুন (বালিশ দিন)", "pose_key": "legs_elevated"},
                    {"step": 3, "text_bn": "শান্ত থাকুন, নড়াচড়া করবেন না", "pose_key": "still"}
                ],
                "mediapipe_landmarks": ["hip", "knee", "ankle"],
                "target_angle": 30  # Degrees for leg elevation
            },
            
            "eclampsia_position": {
                "type": "position",
                "title_bn": "রিকভারি পজিশন",
                "instructions": [
                    {"step": 1, "text_bn": "বাম দিকে কাত করুন", "pose_key": "left_lateral"},
                    {"step": 2, "text_bn": "উপরের হাঁটু বাঁকা করুন", "pose_key": "knee_bent"},
                    {"step": 3, "text_bn": "মাথার নিচে হাত বা বালিশ", "pose_key": "head_support"}
                ],
                "mediapipe_landmarks": ["shoulder", "hip", "knee"],
                "target_angle": 90
            },
            
            "breathing_exercise_1": {
                "type": "breathing",
                "title_bn": "শ্বাসের ব্যায়াম",
                "pattern": {
                    "inhale_seconds": 4,
                    "hold_seconds": 1,
                    "exhale_seconds": 4
                },
                "visual_cue": "circle_expand_contract",
                "audio_cue": True
            },
            
            "breathing_exercise_2": {
                "type": "breathing",
                "title_bn": "প্রসবকালীন শ্বাস",
                "pattern": {
                    "inhale_seconds": 4,
                    "hold_seconds": 1,
                    "exhale_seconds": 6
                },
                "visual_cue": "wave_animation"
            },
            
            "pushing_position": {
                "type": "position",
                "title_bn": "পুশিং পজিশন",
                "instructions": [
                    {"step": 1, "text_bn": "হাঁটু বুকের দিকে টানুন", "pose_key": "knees_up"},
                    {"step": 2, "text_bn": "থুতনি বুকে লাগান", "pose_key": "chin_tucked"},
                    {"step": 3, "text_bn": "হাত দিয়ে হাঁটু ধরুন", "pose_key": "holding_knees"}
                ],
                "mediapipe_landmarks": ["hip", "knee", "shoulder", "chin"],
                "requires_supervision": True
            },
            
            "kick_count": {
                "type": "monitoring",
                "title_bn": "বাচ্চার নড়াচড়া গোনা",
                "instructions": [
                    {"step": 1, "text_bn": "বাম কাত হয়ে শুন"},
                    {"step": 2, "text_bn": "প্রতিটি নড়াচড়ায় ট্যাপ করুন"},
                    {"step": 3, "text_bn": "২ ঘণ্টায় ১০টি হলে স্বাভাবিক"}
                ],
                "counter_enabled": True,
                "target_count": 10,
                "time_limit_minutes": 120
            }
        }
        
        return ar_data.get(guidance_type)
    
    def get_labor_stage_guidance(self, stage: str) -> Optional[Dict]:
        """Get guidance for specific labor stage"""
        return self.labor_ar_guidance.get(stage)


# Global instance
emergency_bridge_service = EmergencyBridgeService()
