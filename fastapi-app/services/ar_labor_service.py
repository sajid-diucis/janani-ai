"""
AR Emergency Labor Assistant Service
Offline-First Medical Emergency Tool for Rural Bangladesh

This is a DECISION SUPPORT TOOL and NOT a replacement for trained medical professionals.
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import json


class LaborStage(str, Enum):
    """Stages of labor for AR guidance"""
    PREPARATION = "preparation"
    STAGE_1_EARLY = "stage_1_early"
    STAGE_1_ACTIVE = "stage_1_active"
    STAGE_2_CROWNING = "stage_2_crowning"
    STAGE_2_DELIVERY = "stage_2_delivery"
    STAGE_3_PLACENTA = "stage_3_placenta"
    NEWBORN_CARE = "newborn_care"
    EMERGENCY = "emergency"


class EmergencyType(str, Enum):
    """Emergency situations requiring immediate action"""
    CORD_PROLAPSE = "cord_prolapse"
    SHOULDER_DYSTOCIA = "shoulder_dystocia"
    POSTPARTUM_HEMORRHAGE = "postpartum_hemorrhage"
    BREECH_PRESENTATION = "breech_presentation"
    MATERNAL_DISTRESS = "maternal_distress"
    FETAL_DISTRESS = "fetal_distress"


# Bengali instructions for each stage (offline-ready)
STAGE_INSTRUCTIONS = {
    LaborStage.PREPARATION: {
        "title_bn": "প্রস্তুতি পর্যায়",
        "title_en": "Preparation Stage",
        "color": "#FFC107",  # Yellow - Preparation
        "icon": "⚙️",
        "instructions": [
            {
                "step": 1,
                "text_bn": "পরিষ্কার সুতির কাপড় এবং জীবাণুমুক্ত সরঞ্জাম প্রস্তুত করুন",
                "text_en": "Prepare clean cotton cloths and sterile equipment",
                "ar_visual": "equipment_check",
                "audio_priority": "high"
            },
            {
                "step": 2,
                "text_bn": "মায়ের অবস্থান ঠিক করুন - বাম কাত বা আধা-বসা অবস্থা",
                "text_en": "Position mother - left lateral or semi-reclined",
                "ar_visual": "position_guide",
                "audio_priority": "high"
            },
            {
                "step": 3,
                "text_bn": "জরুরি যোগাযোগ নম্বর হাতের কাছে রাখুন",
                "text_en": "Keep emergency contact numbers ready",
                "ar_visual": "phone_icon",
                "audio_priority": "medium"
            }
        ],
        "pose_landmarks": ["LEFT_HIP", "RIGHT_HIP", "LEFT_SHOULDER", "RIGHT_SHOULDER"],
        "ar_overlay": {
            "type": "position_guide",
            "target_angle": 45,  # Semi-reclined angle
            "green_zone": {"pelvis_elevation": 15, "tolerance": 10}
        }
    },
    
    LaborStage.STAGE_1_EARLY: {
        "title_bn": "প্রথম পর্যায় - প্রারম্ভিক",
        "title_en": "Stage 1 - Early Labor",
        "color": "#FFC107",
        "icon": "⏱️",
        "instructions": [
            {
                "step": 1,
                "text_bn": "সংকোচনের সময় এবং ব্যবধান গণনা করুন",
                "text_en": "Count contraction timing and intervals",
                "ar_visual": "contraction_timer",
                "audio_priority": "high"
            },
            {
                "step": 2,
                "text_bn": "মাকে হাঁটাচলা এবং অবস্থান পরিবর্তনে উৎসাহিত করুন",
                "text_en": "Encourage walking and position changes",
                "ar_visual": "movement_guide",
                "audio_priority": "medium"
            },
            {
                "step": 3,
                "text_bn": "পর্যাপ্ত পানি পান করতে দিন",
                "text_en": "Ensure adequate hydration",
                "ar_visual": "hydration_icon",
                "audio_priority": "medium"
            }
        ],
        "contraction_guidance": {
            "normal_interval_minutes": [15, 20],
            "normal_duration_seconds": [30, 45],
            "warning_interval_minutes": 5
        }
    },
    
    LaborStage.STAGE_1_ACTIVE: {
        "title_bn": "প্রথম পর্যায় - সক্রিয়",
        "title_en": "Stage 1 - Active Labor",
        "color": "#FF9800",
        "icon": "🔄",
        "instructions": [
            {
                "step": 1,
                "text_bn": "সংকোচন প্রতি ৩-৫ মিনিটে আসছে কিনা দেখুন",
                "text_en": "Check if contractions are 3-5 minutes apart",
                "ar_visual": "contraction_intensity",
                "audio_priority": "high"
            },
            {
                "step": 2,
                "text_bn": "শ্বাস-প্রশ্বাসের কৌশল অনুসরণ করুন",
                "text_en": "Follow breathing techniques",
                "ar_visual": "breathing_guide",
                "audio_priority": "high"
            },
            {
                "step": 3,
                "text_bn": "পিঠে মালিশ করুন - কোমরের নিচে বৃত্তাকার চাপ দিন",
                "text_en": "Back massage - circular pressure on lower back",
                "ar_visual": "massage_zones",
                "audio_priority": "medium"
            }
        ],
        "pose_landmarks": ["LEFT_HIP", "RIGHT_HIP", "SPINE_BASE"],
        "ar_overlay": {
            "type": "pressure_zones",
            "massage_points": [
                {"name": "sacrum", "position": "lower_back_center"},
                {"name": "hip_pressure", "position": "bilateral_hips"}
            ]
        }
    },
    
    LaborStage.STAGE_2_CROWNING: {
        "title_bn": "দ্বিতীয় পর্যায় - শিশুর মাথা দেখা যাচ্ছে",
        "title_en": "Stage 2 - Crowning",
        "color": "#FF5722",
        "icon": "👶",
        "instructions": [
            {
                "step": 1,
                "text_bn": "⚠️ মাকে জোরে চাপ না দিতে বলুন - ধীরে শ্বাস নিতে বলুন",
                "text_en": "⚠️ Tell mother NOT to push hard - breathe slowly",
                "ar_visual": "stop_push_warning",
                "audio_priority": "critical"
            },
            {
                "step": 2,
                "text_bn": "পেরিনিয়ামে হালকা চাপ দিন - সবুজ জোনে হাত রাখুন",
                "text_en": "Apply gentle counter-pressure to perineum - place hand in green zone",
                "ar_visual": "perineum_support",
                "audio_priority": "critical"
            },
            {
                "step": 3,
                "text_bn": "মাথা ধীরে ধীরে বের হতে দিন - তাড়াহুড়ো করবেন না",
                "text_en": "Let head emerge slowly - do not rush",
                "ar_visual": "slow_delivery",
                "audio_priority": "high"
            }
        ],
        "ar_overlay": {
            "type": "hand_guide",
            "hand_position": "perineum_support",
            "visual_cue": "pulsing_green_zone",
            "counter_pressure_guide": True
        }
    },
    
    LaborStage.STAGE_2_DELIVERY: {
        "title_bn": "দ্বিতীয় পর্যায় - প্রসব",
        "title_en": "Stage 2 - Delivery",
        "color": "#4CAF50",
        "icon": "✅",
        "instructions": [
            {
                "step": 1,
                "text_bn": "মাথা বের হওয়ার পর ঘাড়ে নাড়ির প্যাঁচ পরীক্ষা করুন",
                "text_en": "Check for cord around neck after head emerges",
                "ar_visual": "cord_check",
                "audio_priority": "critical"
            },
            {
                "step": 2,
                "text_bn": "কাঁধ বের করতে মাকে আলতো করে ধাক্কা দিতে বলুন",
                "text_en": "Guide mother to push gently for shoulders",
                "ar_visual": "shoulder_delivery",
                "audio_priority": "high"
            },
            {
                "step": 3,
                "text_bn": "শিশুকে সাবধানে ধরুন - মাথা এবং ঘাড় সাপোর্ট দিন",
                "text_en": "Catch baby carefully - support head and neck",
                "ar_visual": "baby_catch_guide",
                "audio_priority": "critical"
            }
        ],
        "ar_overlay": {
            "type": "hand_position_guide",
            "positions": ["head_support", "neck_support", "body_cradle"]
        }
    },
    
    LaborStage.NEWBORN_CARE: {
        "title_bn": "নবজাতকের যত্ন",
        "title_en": "Newborn Care",
        "color": "#4CAF50",
        "icon": "👶💚",
        "instructions": [
            {
                "step": 1,
                "text_bn": "🕐 ৩০ সেকেন্ড অপেক্ষা করুন - নাড়ি এখনও কাটবেন না",
                "text_en": "🕐 Wait 30 seconds - DO NOT cut cord yet",
                "ar_visual": "cord_clamp_timer",
                "timer_seconds": 30,
                "audio_priority": "critical"
            },
            {
                "step": 2,
                "text_bn": "শিশুকে মায়ের বুকে রাখুন - ত্বকে ত্বক স্পর্শ",
                "text_en": "Place baby on mother's chest - skin to skin",
                "ar_visual": "skin_to_skin_heatmap",
                "audio_priority": "critical"
            },
            {
                "step": 3,
                "text_bn": "শিশু কাঁদছে এবং শ্বাস নিচ্ছে কিনা দেখুন",
                "text_en": "Check if baby is crying and breathing",
                "ar_visual": "breathing_check",
                "audio_priority": "critical"
            },
            {
                "step": 4,
                "text_bn": "শিশুকে শুকনো কাপড় দিয়ে মুছে গরম রাখুন",
                "text_en": "Dry baby with clean cloth and keep warm",
                "ar_visual": "warmth_guide",
                "audio_priority": "high"
            }
        ],
        "ar_overlay": {
            "type": "countdown_timer",
            "duration_seconds": 30,
            "label_bn": "নাড়ি কাটার আগে অপেক্ষা করুন",
            "heatmap": {
                "target": "mothers_chest",
                "optimal_zone": "between_breasts"
            }
        }
    },
    
    LaborStage.STAGE_3_PLACENTA: {
        "title_bn": "তৃতীয় পর্যায় - ফুল/গর্ভফুল",
        "title_en": "Stage 3 - Placenta Delivery",
        "color": "#9C27B0",
        "icon": "🔴",
        "instructions": [
            {
                "step": 1,
                "text_bn": "⏱️ ৩০ মিনিটের মধ্যে ফুল বের হওয়া উচিত",
                "text_en": "⏱️ Placenta should deliver within 30 minutes",
                "ar_visual": "placenta_timer",
                "audio_priority": "high"
            },
            {
                "step": 2,
                "text_bn": "নাড়িতে টান দেবেন না - অপেক্ষা করুন",
                "text_en": "DO NOT pull on cord - wait",
                "ar_visual": "no_pull_warning",
                "audio_priority": "critical"
            },
            {
                "step": 3,
                "text_bn": "রক্তপাতের পরিমাণ লক্ষ্য করুন",
                "text_en": "Monitor amount of bleeding",
                "ar_visual": "bleeding_monitor",
                "audio_priority": "high"
            }
        ],
        "warning_signs": {
            "excessive_bleeding": {
                "threshold_ml": 500,
                "text_bn": "🚨 অতিরিক্ত রক্তপাত - জরুরি সাহায্য কল করুন",
                "text_en": "🚨 Excessive bleeding - Call emergency help"
            }
        }
    }
}

# Emergency protocols
EMERGENCY_PROTOCOLS = {
    EmergencyType.CORD_PROLAPSE: {
        "title_bn": "🚨 নাড়ি বের হয়ে গেছে",
        "title_en": "🚨 Cord Prolapse",
        "severity": "critical",
        "color": "#F44336",
        "immediate_actions": [
            {
                "step": 1,
                "text_bn": "এখনই ৯৯৯ কল করুন",
                "text_en": "Call 999 immediately",
                "ar_visual": "emergency_call"
            },
            {
                "step": 2,
                "text_bn": "মাকে হাঁটু-বুক অবস্থানে রাখুন (মাথা নিচে, নিতম্ব উপরে)",
                "text_en": "Put mother in knee-chest position (head down, bottom up)",
                "ar_visual": "knee_chest_position"
            },
            {
                "step": 3,
                "text_bn": "নাড়িকে ভেজা গরম কাপড় দিয়ে ঢেকে রাখুন",
                "text_en": "Cover cord with warm wet cloth",
                "ar_visual": "cord_protection"
            }
        ]
    },
    
    EmergencyType.SHOULDER_DYSTOCIA: {
        "title_bn": "🚨 কাঁধ আটকে গেছে",
        "title_en": "🚨 Shoulder Dystocia",
        "severity": "critical",
        "color": "#F44336",
        "immediate_actions": [
            {
                "step": 1,
                "text_bn": "সাহায্যের জন্য চিৎকার করুন - একা চেষ্টা করবেন না",
                "text_en": "Call for help - Do not attempt alone",
                "ar_visual": "call_help"
            },
            {
                "step": 2,
                "text_bn": "McRoberts ম্যানুভার: মায়ের পা বুকের দিকে ভাঁজ করুন",
                "text_en": "McRoberts maneuver: Flex mother's legs to chest",
                "ar_visual": "mcroberts_position"
            },
            {
                "step": 3,
                "text_bn": "সুপ্রাপিউবিক প্রেশার: পেটের নিচে চাপ দিন",
                "text_en": "Suprapubic pressure: Press above pubic bone",
                "ar_visual": "suprapubic_pressure"
            }
        ]
    },
    
    EmergencyType.POSTPARTUM_HEMORRHAGE: {
        "title_bn": "🚨 প্রসব পরবর্তী অতিরিক্ত রক্তপাত",
        "title_en": "🚨 Postpartum Hemorrhage",
        "severity": "critical", 
        "color": "#F44336",
        "immediate_actions": [
            {
                "step": 1,
                "text_bn": "৯৯৯ কল করুন - এটি জরুরি অবস্থা",
                "text_en": "Call 999 - This is an emergency",
                "ar_visual": "emergency_call"
            },
            {
                "step": 2,
                "text_bn": "জরায়ু ম্যাসেজ করুন - নাভির নিচে শক্ত করে চাপুন",
                "text_en": "Massage uterus - Press firmly below navel",
                "ar_visual": "uterine_massage"
            },
            {
                "step": 3,
                "text_bn": "মায়ের পা উঁচু করে রাখুন",
                "text_en": "Elevate mother's legs",
                "ar_visual": "leg_elevation"
            },
            {
                "step": 4,
                "text_bn": "মাকে গরম রাখুন - শক থেকে বাঁচাতে",
                "text_en": "Keep mother warm - prevent shock",
                "ar_visual": "warmth_blanket"
            }
        ]
    }
}

# MediaPipe pose landmarks for labor positioning
POSE_LANDMARKS = {
    "pelvis_positioning": {
        "landmarks": [23, 24, 11, 12],  # LEFT_HIP, RIGHT_HIP, LEFT_SHOULDER, RIGHT_SHOULDER
        "optimal_angle": 45,
        "description_bn": "পেলভিস উচ্চতা এবং কোণ"
    },
    "knee_chest": {
        "landmarks": [25, 26, 23, 24, 11, 12],  # KNEES, HIPS, SHOULDERS
        "description_bn": "হাঁটু-বুক অবস্থান"
    },
    "lithotomy": {
        "landmarks": [25, 26, 27, 28, 23, 24],  # KNEES, ANKLES, HIPS
        "leg_angle": 90,
        "description_bn": "লিথোটমি অবস্থান"
    }
}


class ARLaborAssistant:
    """
    AR Emergency Labor Assistant
    Offline-first decision support tool
    """
    
    def __init__(self):
        self.current_stage = LaborStage.PREPARATION
        self.session_log = []
        self.start_time = None
        
    def get_stage_instructions(self, stage: LaborStage) -> Dict:
        """Get AR instructions for a specific labor stage"""
        return STAGE_INSTRUCTIONS.get(stage, STAGE_INSTRUCTIONS[LaborStage.PREPARATION])
    
    def get_all_stages(self) -> List[Dict]:
        """Get all stages with their instructions"""
        stages = []
        for stage in LaborStage:
            if stage != LaborStage.EMERGENCY:
                stage_data = STAGE_INSTRUCTIONS.get(stage, {})
                stages.append({
                    "stage_id": stage.value,
                    "title_bn": stage_data.get("title_bn", stage.value),
                    "title_en": stage_data.get("title_en", stage.value),
                    "color": stage_data.get("color", "#666"),
                    "icon": stage_data.get("icon", "📋"),
                    "instruction_count": len(stage_data.get("instructions", []))
                })
        return stages
    
    def get_emergency_protocol(self, emergency_type: EmergencyType) -> Dict:
        """Get emergency protocol for critical situations"""
        return EMERGENCY_PROTOCOLS.get(emergency_type, {})
    
    def get_all_emergencies(self) -> List[Dict]:
        """Get all emergency protocols"""
        emergencies = []
        for etype in EmergencyType:
            protocol = EMERGENCY_PROTOCOLS.get(etype, {})
            emergencies.append({
                "type": etype.value,
                "title_bn": protocol.get("title_bn", etype.value),
                "title_en": protocol.get("title_en", etype.value),
                "severity": protocol.get("severity", "critical"),
                "color": protocol.get("color", "#F44336")
            })
        return emergencies
    
    def get_pose_landmarks_config(self) -> Dict:
        """Get MediaPipe pose landmark configurations"""
        return POSE_LANDMARKS
    
    def log_action(self, action: str, details: Dict = None) -> Dict:
        """Log an action with timestamp for offline sync"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "stage": self.current_stage.value,
            "details": details or {}
        }
        self.session_log.append(log_entry)
        return log_entry
    
    def get_session_log(self) -> List[Dict]:
        """Get all logged actions for the session"""
        return self.session_log
    
    def get_offline_data_bundle(self) -> Dict:
        """Get complete data bundle for offline use"""
        return {
            "stages": STAGE_INSTRUCTIONS,
            "emergencies": EMERGENCY_PROTOCOLS,
            "pose_landmarks": POSE_LANDMARKS,
            "disclaimer": {
                "text_bn": "⚠️ এটি একটি সিদ্ধান্ত সহায়তা টুল। এটি প্রশিক্ষিত ধাত্রী বা ডাক্তারের বিকল্প নয়। জরুরি অবস্থায় সর্বদা পেশাদার সাহায্য নিন।",
                "text_en": "⚠️ This is a Decision Support Tool. It is NOT a replacement for a trained midwife or doctor. Always seek professional help in emergencies."
            },
            "emergency_numbers": {
                "bangladesh_999": "999",
                "ambulance": "199",
                "health_helpline": "16789"
            },
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat()
        }


# Singleton instance
ar_labor_assistant = ARLaborAssistant()
