"""
Digital Midwife - Voice-First Triage & Risk Detection Service
Deterministic Decision Tree for Red Flag Detection
Supports Bangla regional dialects
"""
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime

from models.care_models import (
    Symptom, SymptomReport, TriageResult, MaternalRiskProfile,
    RiskLevel, RedFlagType, SymptomSeverity
)


class TriageDecisionTree:
    """
    Deterministic Decision Tree for maternal health triage.
    Based on WHO danger signs and clinical protocols.
    """
    
    def __init__(self):
        # Symptom keywords mapping (standard Bengali + dialects)
        self._load_symptom_keywords()
        # Decision rules
        self._load_decision_rules()
        # Historical cross-reference rules
        self._load_history_rules()
    
    def _load_symptom_keywords(self):
        """
        Load symptom detection keywords.
        Includes: Standard Bengali, Sylheti, Chittagonian dialects
        """
        self.symptom_keywords = {
            # === ENGLISH / PHONETIC SUPPORT (For offline/typing) ===
            "severe_headache": {
                "bengali": ["মাথাব্যথা", "মাথা ব্যথা", "প্রচণ্ড মাথাব্যথা", "তীব্র মাথাব্যথা", "মাথা ধরা", "মাথা টিপটিপ", "matha", "headache", "matha betha", "matha batha"],
                "sylheti": ["মাডা ব্যথা", "মাডা বিষ"],
                "chittagonian": ["মাথা ধরছে", "মাথায় যন্ত্রণা"],
                "severity": SymptomSeverity.SEVERE,
                "red_flag": RedFlagType.PREECLAMPSIA,
                "needs_severity_check": True
            },
            "bleeding": {
                "bengali": ["রক্তপাত", "রক্তস্রাব", "ব্লিডিং", "রক্ত পড়া", "রক্ত যাওয়া", "রক্ত আসা", "bleeding", "rokto", "blood", "spotting"],
                "sylheti": ["রক্ত ফইরা যাওয়া", "রক্ত পরতাছে"],
                "chittagonian": ["রক্ত পইরতাছে", "রক্ত যাইতাছে"],
                "severity": SymptomSeverity.EMERGENCY,
                "red_flag": RedFlagType.HEMORRHAGE
            },
            "high_fever": {
                "bengali": ["জ্বর", "তীব্র জ্বর", "বেশি জ্বর", "গায়ে জ্বর", "শরীর গরম", "jor", "fever", "gorom", "temperature"],
                "sylheti": ["জুর", "গা গরম"],
                "chittagonian": ["জ্বর আছে"],
                "severity": SymptomSeverity.MODERATE,
                "red_flag": RedFlagType.INFECTION
            },
            "nausea": {
                "bengali": ["বমি", "বমি ভাব", "বমি বমি লাগা", "গা গুলানো", "bomi", "vomiting", "nausea"],
                "sylheti": ["বমি লাগে", "গা ঘুলায়"],
                "chittagonian": ["বমি বমি"],
                "severity": SymptomSeverity.MILD,
                "red_flag": None
            },
            "severe_abdominal_pain": {
                "bengali": ["পেটব্যথা", "পেটে ব্যথা", "তীব্র পেটব্যথা", "প্রচণ্ড পেটে ব্যথা", "পেট মোচড়ানো", "pet betha", "stomach pain", "abdomen pain"],
                "sylheti": ["পেডে ব্যথা", "পেড বিষ"],
                "chittagonian": ["পেডে যন্ত্রণা"],
                "severity": SymptomSeverity.SEVERE,
                "red_flag": RedFlagType.HEMORRHAGE,
                "needs_severity_check": True
            },
            "vision_problems": {
                "bengali": ["চোখে ঝাপসা", "ঝাপসা দেখা", "চোখে আলো দেখা", "চোখে তারা দেখা", "চোখে অন্ধকার", "chokhe jhapsha", "blurred vision"],
                "sylheti": ["চউখে দেহা যায় না", "ঝাপসা লাগে"],
                "chittagonian": ["চোক্কুত দেখা যায় না"],
                "severity": SymptomSeverity.EMERGENCY,
                "red_flag": RedFlagType.PREECLAMPSIA
            },
            "convulsions": {
                "bengali": ["খিঁচুনি", "ফিট", "হাত পা কাঁপা", "অজ্ঞান", "khichuni", "convulsion", "seizure", "fit"],
                "sylheti": ["খিচুনি", "বেহুশ"],
                "chittagonian": ["খিচানি", "অজ্ঞান"],
                "severity": SymptomSeverity.EMERGENCY,
                "red_flag": RedFlagType.ECLAMPSIA
            },
            "water_breaking": {
                "bengali": ["পানি ভাঙা", "পানি ছুটে গেছে", "জল ভাঙা", "পানি আসছে", "pani bhanga", "water break"],
                "sylheti": ["পানি ফাইটা গেছে"],
                "chittagonian": ["পানি যাইতাছে"],
                "severity": SymptomSeverity.EMERGENCY,
                "red_flag": RedFlagType.RUPTURE_OF_MEMBRANES
            },
            "reduced_movement": {
                "bengali": ["বাচ্চা নড়ছে না", "বাচ্চার নড়াচড়া কম", "বাচ্চা নাড়ে না", "বাচ্চা নড়াচড়া বন্ধ", "baby not moving", "movement kom", "norachora kom"],
                "sylheti": ["বাচ্চা নারতাছে না"],
                "chittagonian": ["বাচ্চা নারে না"],
                "severity": SymptomSeverity.EMERGENCY,
                "red_flag": RedFlagType.FETAL_DISTRESS
            },
            "swelling": {
                "bengali": ["পা ফোলা", "মুখ ফোলা", "হাত ফোলা", "ফুলে গেছে", "পানি জমা", "pa fula", "swelling", "edema"],
                "sylheti": ["পা ফুইলা গেছে"],
                "chittagonian": ["ফুলে গেছে"],
                "severity": SymptomSeverity.MODERATE,
                "red_flag": RedFlagType.PREECLAMPSIA
            },
            "fatigue": {
                "bengali": ["ক্লান্ত", "দুর্বল", "শক্তি নেই", "অবসাদ", "weak", "durbol", "klanto"],
                "sylheti": ["ট্যারা লাগে", "ক্লান্ত"],
                "chittagonian": ["শক্তি নাই"],
                "severity": SymptomSeverity.MILD,
                "red_flag": None
            },
            "back_pain": {
                "bengali": ["পিঠে ব্যথা", "কোমরে ব্যথা", "পিঠ ব্যথা", "merudondo", "back pain", "pith betha", "komor betha"],
                "sylheti": ["পিঠে বিষ", "কোমরে ব্যথা"],
                "chittagonian": ["পিঠে যন্ত্রণা"],
                "severity": SymptomSeverity.MILD,
                "red_flag": None
            },
            "constipation": {
                "bengali": ["কোষ্ঠকাঠিন্য", "পেট পরিষ্কার হয় না", "পায়খানা হয় না", "kosh", "constipation", "paykhana kosh"],
                "sylheti": ["পেট পরিষ্কার অয় না"],
                "chittagonian": ["পায়খানা হয় না"],
                "severity": SymptomSeverity.MILD,
                "red_flag": None
            },
             "leg_cramps": {
                "bengali": ["পায়ে টান", "পা কামড়ানো", "পায়ে ব্যথা", "pa betha", "leg cramp"],
                "sylheti": ["পায়ে টান ধরে"],
                "chittagonian": ["পায়ে কামড়"],
                "severity": SymptomSeverity.MILD,
                "red_flag": None
            },
             "breathlessness": {
                "bengali": ["শ্বাসকষ্ট", "শ্বাস নিতে কষ্ট", "দম বন্ধ লাগা", "shashkoshto", "breathing trouble"],
                "sylheti": ["দম আইনা কষ্ট", "শ্বাস অয় না"],
                "chittagonian": ["দম পাই না"],
                "severity": SymptomSeverity.MODERATE,
                "red_flag": None,
                "needs_severity_check": True
            }
        }
        
        # Severity modifiers in Bengali
        self.severity_modifiers = {
            "severe": ["প্রচণ্ড", "তীব্র", "খুব বেশি", "অনেক", "সহ্য হচ্ছে না", "অসহ্য"],
            "continuous": ["সারাক্ষণ", "থামছে না", "ক্রমাগত", "বারবার"],
            "sudden": ["হঠাৎ", "আচমকা", "হুট করে"]
        }
    
    def _load_decision_rules(self):
        """
        Deterministic decision rules for triage.
        Based on WHO clinical protocols.
        """
        self.decision_rules = {
            # IMMEDIATE EMERGENCY - Call 999
            "emergency": {
                "conditions": [
                    {"symptoms": ["bleeding"], "action": "immediate_hospital"},
                    {"symptoms": ["convulsions"], "action": "immediate_hospital"},
                    {"symptoms": ["vision_problems", "severe_headache"], "action": "immediate_hospital"},
                    {"symptoms": ["water_breaking"], "week_lt": 37, "action": "immediate_hospital"},
                    {"symptoms": ["reduced_movement"], "action": "immediate_hospital"},
                    {"symptoms": ["severe_abdominal_pain", "bleeding"], "action": "immediate_hospital"}
                ],
                "risk_level": RiskLevel.CRITICAL,
                "timeframe": "immediate"
            },
            
            # URGENT - See doctor within 1 hour
            "urgent": {
                "conditions": [
                    {"symptoms": ["severe_headache"], "with_history": ["hypertension"], "action": "urgent_care"},
                    {"symptoms": ["high_fever"], "temp_gt": 100.4, "action": "urgent_care"},
                    {"symptoms": ["contractions_preterm"], "week_lt": 37, "action": "urgent_care"},
                    {"symptoms": ["swelling"], "location": ["face", "hands"], "action": "urgent_care"},
                    {"symptoms": ["severe_abdominal_pain"], "action": "urgent_care"}
                ],
                "risk_level": RiskLevel.HIGH,
                "timeframe": "within_1_hour"
            },
            
            # SOON - See doctor within 24 hours
            "soon": {
                "conditions": [
                    {"symptoms": ["burning_urination"], "action": "see_doctor_today"},
                    {"symptoms": ["swelling"], "location": ["legs"], "action": "see_doctor_today"},
                    {"symptoms": ["high_fever"], "action": "see_doctor_today"},
                    {"symptoms": ["breathlessness"], "severity": "moderate", "action": "see_doctor_today"}
                ],
                "risk_level": RiskLevel.MODERATE,
                "timeframe": "within_24_hours"
            },
            
            # ROUTINE - Self-care or routine visit
            "routine": {
                "conditions": [
                    {"symptoms": ["nausea"], "action": "self_care"},
                    {"symptoms": ["fatigue"], "action": "self_care"},
                    {"symptoms": ["back_pain"], "action": "self_care"},
                    {"symptoms": ["constipation"], "action": "self_care"},
                    {"symptoms": ["leg_cramps"], "action": "self_care"}
                ],
                "risk_level": RiskLevel.LOW,
                "timeframe": "routine"
            }
        }
    
    def _load_history_rules(self):
        """
        Rules for cross-referencing with patient history.
        If patient has certain conditions, symptoms become more serious.
        """
        self.history_rules = {
            # If history of hypertension + headache = HIGH RISK (preeclampsia)
            "hypertension": {
                "elevates": ["severe_headache", "swelling", "vision_problems"],
                "to_level": RiskLevel.CRITICAL,
                "concern": "প্রি-এক্লাম্পসিয়া/এক্লাম্পসিয়ার ঝুঁকি"
            },
            # If history of diabetes + certain symptoms
            "gestational_diabetes": {
                "elevates": ["fatigue", "nausea", "breathlessness"],
                "to_level": RiskLevel.HIGH,
                "concern": "ডায়াবেটিস জটিলতার ঝুঁকি"
            },
            # If history of anemia
            "anemia": {
                "elevates": ["fatigue", "breathlessness"],
                "to_level": RiskLevel.MODERATE,
                "concern": "রক্তস্বল্পতা বাড়তে পারে"
            },
            # If history of preterm labor
            "preterm_labor_history": {
                "elevates": ["contractions_preterm", "back_pain"],
                "to_level": RiskLevel.HIGH,
                "concern": "আবার প্রিম্যাচিউর প্রসবের ঝুঁকি"
            }
        }
    
    def detect_symptoms(self, text: str, dialect: str = "standard_bangla") -> List[Tuple[str, SymptomSeverity]]:
        """
        Detect symptoms from voice/text input.
        Returns list of (symptom_id, severity) tuples.
        """
        detected = []
        text_lower = text.lower()
        
        for symptom_id, symptom_data in self.symptom_keywords.items():
            # Check all dialect variants
            all_keywords = symptom_data.get("bengali", [])
            all_keywords += symptom_data.get("sylheti", [])
            all_keywords += symptom_data.get("chittagonian", [])
            
            for keyword in all_keywords:
                if keyword.lower() in text_lower:
                    severity = symptom_data["severity"]
                    
                    # Check for severity modifiers
                    if symptom_data.get("needs_severity_check"):
                        for mod in self.severity_modifiers.get("severe", []):
                            if mod in text_lower:
                                severity = SymptomSeverity.SEVERE
                                break
                        for mod in self.severity_modifiers.get("continuous", []):
                            if mod in text_lower:
                                if severity != SymptomSeverity.EMERGENCY:
                                    severity = SymptomSeverity.SEVERE
                                break
                    
                    detected.append((symptom_id, severity))
                    break  # Found this symptom, move to next
        
        return detected
    
    def apply_decision_tree(
        self, 
        detected_symptoms: List[Tuple[str, SymptomSeverity]],
        patient_history: List[str],
        current_week: int
    ) -> Dict:
        """
        Apply deterministic decision tree to detected symptoms.
        Returns triage decision.
        """
        symptom_ids = [s[0] for s in detected_symptoms]
        max_severity = max([s[1] for s in detected_symptoms], default=SymptomSeverity.MILD)
        
        # Default result
        result = {
            "risk_level": RiskLevel.LOW,
            "red_flags": [],
            "timeframe": "routine",
            "action": "self_care",
            "elevated_due_to_history": False,
            "history_concern": None
        }
        
        # Check emergency rules first
        for priority in ["emergency", "urgent", "soon", "routine"]:
            rules = self.decision_rules[priority]
            for condition in rules["conditions"]:
                required_symptoms = condition.get("symptoms", [])
                
                # Check if required symptoms are present
                if all(s in symptom_ids for s in required_symptoms):
                    # Check week constraint
                    week_lt = condition.get("week_lt")
                    if week_lt and current_week >= week_lt:
                        continue
                    
                    # Check history constraint
                    with_history = condition.get("with_history", [])
                    if with_history and not any(h in patient_history for h in with_history):
                        continue
                    
                    # This condition matches
                    result["risk_level"] = rules["risk_level"]
                    result["timeframe"] = rules["timeframe"]
                    result["action"] = condition.get("action", "see_doctor")
                    
                    # Collect red flags
                    for s_id in symptom_ids:
                        symptom_data = self.symptom_keywords.get(s_id, {})
                        red_flag = symptom_data.get("red_flag")
                        if red_flag and red_flag not in result["red_flags"]:
                            result["red_flags"].append(red_flag)
                    
                    # Found a matching rule, check history elevation
                    break
            
            if result["risk_level"] != RiskLevel.LOW:
                break
        
        # Cross-reference with patient history
        for history_item in patient_history:
            history_rule = self.history_rules.get(history_item)
            if history_rule:
                elevates = history_rule.get("elevates", [])
                if any(s in symptom_ids for s in elevates):
                    elevated_level = history_rule["to_level"]
                    # Only elevate if current level is lower
                    level_order = [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]
                    if level_order.index(elevated_level) > level_order.index(result["risk_level"]):
                        result["risk_level"] = elevated_level
                        result["elevated_due_to_history"] = True
                        result["history_concern"] = history_rule["concern"]
        
        return result


class TriageService:
    """
    Voice-First Triage Service.
    Processes symptom reports and generates triage results.
    """
    
    def __init__(self):
        self.decision_tree = TriageDecisionTree()
        self.patient_history_cache: Dict[str, MaternalRiskProfile] = {}
    
    def _detect_dialect(self, text: str) -> str:
        """Detect Bangla dialect from text patterns"""
        # Simple dialect detection based on common patterns
        sylheti_markers = ["ফাইটা", "অইছে", "কইতাছে", "খাইছে", "যাইতাছে"]
        chittagonian_markers = ["গই", "ইতা", "হোই", "কিয়া"]
        
        for marker in sylheti_markers:
            if marker in text:
                return "sylheti"
        
        for marker in chittagonian_markers:
            if marker in text:
                return "chittagonian"
        
        return "standard_bangla"
    
    async def process_symptom_report(
        self,
        user_id: str,
        input_text: str,
        patient_profile: Optional[MaternalRiskProfile] = None,
        include_history: bool = True
    ) -> TriageResult:
        """
        Process a symptom report and return triage result.
        """
        # Detect dialect
        dialect = self._detect_dialect(input_text)
        
        # Detect symptoms
        detected_symptoms = self.decision_tree.detect_symptoms(input_text, dialect)
        
        if not detected_symptoms:
            # No symptoms detected - ask for clarification
            return TriageResult(
                user_id=user_id,
                risk_level=RiskLevel.LOW,
                detected_red_flags=[],
                primary_concern="কোনো নির্দিষ্ট লক্ষণ বোঝা যায়নি",
                primary_concern_bengali="কোনো নির্দিষ্ট লক্ষণ বোঝা যায়নি",
                immediate_action="Please describe your symptoms more clearly",
                immediate_action_bengali="অনুগ্রহ করে আপনার সমস্যাটি আরেকটু বিস্তারিত বলুন। যেমন: কোথায় ব্যথা, কতক্ষণ ধরে, কতটা কষ্ট হচ্ছে।",
                should_trigger_emergency=False,
                recommended_timeframe="routine",
                home_care_advice=[],
                warning_signs_to_watch=[],
                response_audio_text="আপনার সমস্যাটি আমি ঠিকমতো বুঝতে পারিনি। একটু বিস্তারিত বলবেন?",
                confidence_score=0.3
            )
        
        # Get patient history
        patient_history = []
        current_week = 20  # Default
        
        if patient_profile:
            current_week = patient_profile.current_week
            patient_history = patient_profile.existing_conditions
            patient_history.extend(patient_profile.previous_complications)
        
        # Apply decision tree
        decision = self.decision_tree.apply_decision_tree(
            detected_symptoms,
            patient_history,
            current_week
        )
        
        # Build response based on decision
        return self._build_triage_result(
            user_id=user_id,
            detected_symptoms=detected_symptoms,
            decision=decision,
            input_text=input_text,
            current_week=current_week
        )
    
    def _build_triage_result(
        self,
        user_id: str,
        detected_symptoms: List[Tuple[str, SymptomSeverity]],
        decision: Dict,
        input_text: str,
        current_week: int
    ) -> TriageResult:
        """Build the complete triage result"""
        
        risk_level = decision["risk_level"]
        red_flags = decision["red_flags"]
        timeframe = decision["timeframe"]
        
        # Primary concern (first detected severe/emergency symptom)
        primary_symptom = detected_symptoms[0][0] if detected_symptoms else "unknown"
        primary_concern_map = {
            "bleeding": ("Vaginal bleeding", "যোনি থেকে রক্তপাত"),
            "severe_headache": ("Severe headache", "তীব্র মাথাব্যথা"),
            "vision_problems": ("Vision problems", "চোখে সমস্যা"),
            "convulsions": ("Convulsions", "খিঁচুনি"),
            "severe_abdominal_pain": ("Severe abdominal pain", "তীব্র পেটব্যথা"),
            "water_breaking": ("Water breaking", "পানি ভাঙা"),
            "reduced_movement": ("Reduced fetal movement", "বাচ্চার নড়াচড়া কম"),
            "contractions_preterm": ("Preterm contractions", "সময়ের আগে সংকোচন"),
            "high_fever": ("High fever", "জ্বর"),
            "burning_urination": ("Urinary infection", "প্রস্রাবে সমস্যা"),
            "swelling": ("Swelling", "ফুলে যাওয়া"),
        }
        
        concern_en, concern_bn = primary_concern_map.get(primary_symptom, ("Health concern", "স্বাস্থ্য সমস্যা"))
        
        # Immediate action based on risk level
        action_map = {
            RiskLevel.CRITICAL: {
                "en": "Go to hospital immediately or call 999",
                "bn": "🚨 আপু, এখনই দেরি না করে হাসপাতালে পৌঁছে যান। খুব দরকার হলে 999 এ কল দিন।"
            },
            RiskLevel.HIGH: {
                "en": "See a doctor within 1 hour",
                "bn": "⚠️ আমাদের একটু সতর্ক হতে হবে। এক ঘণ্টার মধ্যে ডাক্তার দেখানোর চেষ্টা করুন।"
            },
            RiskLevel.MODERATE: {
                "en": "See a doctor today",
                "bn": "আজকের দিনেই একবার আপনার ডাক্তারের সাথে কথা বলে নিন।"
            },
            RiskLevel.LOW: {
                "en": "Self-care at home, routine checkup",
                "bn": "চিন্তা করবেন না, বাসায় বিশ্রাম নিন। পরবর্তী চেকআপের সময় ডাক্তারকে এই কথা বলবেন।"
            }
        }
        
        action = action_map.get(risk_level, action_map[RiskLevel.LOW])
        
        # Home care advice
        home_care = self._get_home_care_advice(primary_symptom, risk_level)
        # Apply dialect to home care - DISABLED for Standard Bengali
        # home_care = [self._apply_noakhali_dialect(advice) for advice in home_care]
        
        # Warning signs
        warning_signs = self._get_warning_signs(detected_symptoms)
        # Apply dialect to warning signs - DISABLED for Standard Bengali
        # warning_signs = [self._apply_noakhali_dialect(sign) for sign in warning_signs]
        
        # Audio response
        audio_text = self._generate_voice_response(
            concern_bn, 
            action["bn"], 
            risk_level,
            decision.get("history_concern")
        )
        # Verify dialect application on audio text - DISABLED for Standard Bengali
        # if "হানি" not in audio_text and "পানি" in audio_text:
        #      audio_text = self._apply_noakhali_dialect(audio_text)

        # Apply dialect to other Bengali fields - DISABLED for Standard Bengali
        concern_bn_dialect = concern_bn # self._apply_noakhali_dialect(concern_bn)
        action_bn_dialect = action["bn"] # self._apply_noakhali_dialect(action["bn"])

        # Should trigger emergency?
        should_emergency = risk_level in [RiskLevel.CRITICAL]
        ambulance_needed = risk_level == RiskLevel.CRITICAL and any(
            rf in [RedFlagType.HEMORRHAGE, RedFlagType.ECLAMPSIA, RedFlagType.CONVULSIONS] 
            for rf in red_flags
        )
        
        return TriageResult(
            user_id=user_id,
            risk_level=risk_level,
            detected_red_flags=red_flags,
            primary_concern=concern_en,
            primary_concern_bengali=concern_bn_dialect,
            immediate_action=action["en"],
            immediate_action_bengali=action_bn_dialect,
            should_trigger_emergency=should_emergency,
            recommended_timeframe=timeframe,
            home_care_advice=home_care,
            warning_signs_to_watch=warning_signs,
            emergency_contact_needed=should_emergency,
            hospital_referral_needed=risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH],
            ambulance_needed=ambulance_needed,
            response_audio_text=audio_text,
            confidence_score=0.9 if detected_symptoms else 0.5
        )
    
    def _get_home_care_advice(self, symptom: str, risk_level: RiskLevel) -> List[str]:
        """Get home care advice based on symptom"""
        advice_map = {
            "nausea": [
                "অল্প অল্প করে খান",
                "শুকনো বিস্কুট বা টোস্ট খেয়ে দেখুন",
                "আদা চা বা লেবু পানি খেতে পারেন",
                "গন্ধযুক্ত খাবার এড়িয়ে চলুন"
            ],
            "back_pain": [
                "বাম পাশে কাত হয়ে শুন",
                "গরম সেঁক দিন",
                "নরম জুতা পরুন",
                "ভারী জিনিস তুলবেন না"
            ],
            "constipation": [
                "বেশি করে পানি খান",
                "শাকসবজি ও ফল খান",
                "হালকা হাঁটাহাঁটি করুন",
                "ইসবগুল খেতে পারেন"
            ],
            "leg_cramps": [
                "পা স্ট্রেচ করুন",
                "হালকা ম্যাসাজ করুন",
                "কলা খান (পটাশিয়াম)",
                "ঘুমানোর আগে পা উঁচু করে রাখুন"
            ],
            "fatigue": [
                "পর্যাপ্ত বিশ্রাম নিন",
                "দিনে একটু ঘুমান",
                "আয়রনযুক্ত খাবার খান",
                "হালকা হাঁটাহাঁটি করুন"
            ]
        }
        
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            return ["হাসপাতালে যাওয়ার আগে শান্ত থাকুন", "পরিবারকে জানান"]
        
        return advice_map.get(symptom, ["বিশ্রাম নিন", "পানি খান"])
    
    def _get_warning_signs(self, detected_symptoms: List[Tuple[str, SymptomSeverity]]) -> List[str]:
        """Get warning signs to watch based on detected symptoms"""
        signs = [
            "রক্তপাত হলে",
            "প্রচণ্ড মাথাব্যথা হলে",
            "চোখে ঝাপসা দেখলে",
            "বাচ্চার নড়াচড়া কমে গেলে"
        ]
        return signs
    
    def _load_dialect_rules(self) -> Dict[str, str]:
        """Load Noakhali dialect rules (Core Lexicon)"""
        mappings = {}
        try:
            # Deep Lexicon (High-Entropy words)
            mappings = {
                # Core
                "ছেলে": "হোলা",
                "মেয়ে": "মাইয়া",
                "মেয়েকে": "মাইয়ারে",
                "কেন": "কীয়া",
                "সব": "বেগগুন",
                "টাকা": "টেঁয়া",
                "সে": "হেতে", 
                "তাদের": "হেগো",
                "গতকাল": "গাইল্লা",
                "আগামীকাল": "কাইল্লা",
                "পানি": "হানি",
                "ফুল": "হুল",
                
                # Clinical/Common
                "ভাল": "বালা",
                "ভালো": "বালা",
                "খারাপ": "হারাফ",
                "রক্ত": "লু",
                "ব্যথা": "বেথা",
                "ব্যাথা": "বেথা",
                "মাথা": "মাথা", # Stays similar usually
                "পেট": "হ্রেট", # P -> H shift sometimes, but 'Pet' common. Let's strictly follow rule P->H if initial.
                "ডাক্তার": "ডাক্তর",
                "হাসপাতাল": "হাসাতাল",
                "ঔষধ": "অসুদ",
                "শুনুন": "হুনেন",
                "বলুন": "কইওন",
                "করুন": "করেন",
                "আছেন": "আছোস",
                "আছি": "আছি",
                "যাবে": "যাইবো",
                "হবে": "অইবো",
                "খাবেন": "খাইবেন",
                "নিবেন": "লইবেন",
                "দিন": "দেওন",
                "কি": "কিতা",
                "আমার": "আঁঁর",
                "আপনার": "আন্নের", # Honorific or 'Tor' for familiar
                "তার": "হেঁঁঁর",
                "এখানে": "ইয়ানো",
                "বসুন": "বইসেন",
                "ভয়": "ডর",
                "পাবেন": "হাইয়েন",
                "না": "না",
                "ঠিক": "ঠিক",
            }
        except Exception:
            pass
        return mappings

    def _apply_noakhali_dialect(self, text: str) -> str:
        """Apply Noakhali dialect rules using Phonological Shifts and Lexicon"""
        import re
        
        # 0. Pre-processing normalization
        text = text.replace("ছেন", "সেন").replace("চ্ছ", "চ্চ")

        # 1. Phonological Transformation Rules (The 'Sound' Logic)
        
        # Rule: P (প) -> H (হ) [Start of word]
        # Example: Pani -> Hani, Pabe -> Habe
        # Regex: Word boundary + প -> হ
        text = re.sub(r'\bপ', 'হ', text) 
        
        # Rule: Ph (ফ) -> H/F (ফ/হ) [Start of word]
        # Example: Phul -> Hul/Ful
        # Generally 'Ph' is 'F' sound in standard, but deeply 'H' in Noakhali for some words like Fel (throw) -> Hal (throw).
        # Let's map specific common ones or soft shift. 
        # text = re.sub(r'\bফ', 'হ', text) # Can be aggressive, keep selective or F
        
        # Rule: S/Sh (স/শ) -> H (হ) [Start of word or distinct syllable]
        # Example: Shokal -> Hokal, Shob -> Hob
        text = re.sub(r'\bস', 'হ', text)
        text = re.sub(r'\bশ', 'হ', text)

        # Rule: Ch (চ/ছ) -> S (স)
        # Example: Chhele -> Sele (Hola is lexical), Chinta -> Sinta
        text = re.sub(r'চ', 'স', text)
        text = re.sub(r'ছ', 'স', text)
        
        # Rule: K (ক) -> X (খ) [Intervocalic/Initial often]
        # Example: Kemon -> Xemon (Kh-sound)
        # We will use 'খ' to represent X (Kh) or Guttural
        text = re.sub(r'\bক', 'খ', text)
        
        # Rule: Bh (ভ) -> B (ব) / V
        # Example: Bhalo -> Balo
        text = re.sub(r'\bভ', 'ব', text)

        # 2. Case Endings & Suffixes (Morphology)
        # Possession: -er -> -r / -ar (Standard 'er' is often 'r')
        # This is hard to regex safely without NLP, relying on Lexicon for pronouns.
        
        # Locative: -te -> -ot
        # Example: Barite -> Bari-ot
        text = re.sub(r'তে\b', 'ত', text) # Simple shift

        # Verb: -chhi/chhe -> -er (Continuous)
        # Korchhi -> Koriyer/Xiyer
        text = re.sub(r'ছি\b', 'ইয়ের', text)
        text = re.sub(r'ছে\b', 'ছে', text) # Keep or shift? Often 'che' -> 'se' handled above.
        
        # Future: -bo -> -um/om
        # Jabo -> Zaum
        text = re.sub(r'বো\b', 'উম', text)
        
        # 3. Apply Deep Lexicon Overrides
        # (This overrides phonology if there's a specific word match)
        mappings = self._load_dialect_rules()
        words = text.split()
        new_words = []
        for word in words:
            # Strip punctuation for matching
            cleaned = re.sub(r'[^\w\s]', '', word)
            if cleaned in mappings:
                # Replace but keep punctuation if possible (simple heuristic)
                replacement = mappings[cleaned]
                new_word = word.replace(cleaned, replacement)
                new_words.append(new_word)
            else:
                new_words.append(word)
        
        text = " ".join(new_words)

        # 4. Phrase-level corrections (Post-processing)
        # Fix generated 'H' sound consistency if regex over-applied
        # e.g., 'Haspatal' -> 'Hasatal' (already in lexicon)
        
        # Remove 'Re' after 'Ke' if redundant? No, 'Ke' -> 'Re' usually.
        # Amake -> Arey
        text = text.replace("কে", "রে") 

        return text

    def _generate_voice_response(
        self, 
        concern: str, 
        action: str, 
        risk_level: RiskLevel,
        history_concern: Optional[str] = None
    ) -> str:
        """Generate empathetic voice response using Hybrid Model: Validate -> Assess -> Advise pattern"""
        
        # Phase 1 & 3A: Validate & Empathy
        if risk_level == RiskLevel.CRITICAL:
            intro = f"আপু, আপনার {concern} এর কথা শুনে আমি চিন্তিত। শান্ত থাকুন, আমি আপনার সাথে আছি।"
        elif risk_level == RiskLevel.HIGH:
            intro = f"আপু, আপনার {concern} এর বিষয়টা আমি বুঝতে পারছি। আমাদের এখনই এটা নিয়ে কাজ করতে হবে।"
        elif risk_level == RiskLevel.MODERATE:
            intro = f"আপু, আপনার {concern} নিয়ে একটু মন খারাপ হতে পারে, আমি বুঝতে পারছি। গর্ভাবস্থায় মাঝে মাঝে এমন হয়।"
        else:
            intro = f"আপু, আপনার {concern} এর কথা শুনে বুঝলাম আপনার কষ্ট হচ্ছে। ভয় নেই, আমি শুনছি।"

        # Phase 3C: Assess & Advise
        if risk_level == RiskLevel.CRITICAL:
            body = f"আপনাকে এখনই হাসপাতালে যেতে হবে। {action} এটি আপনার ও সন্তানের নিরাপত্তার জন্য জরুরি।"
            if history_concern:
                body += f" আপনার {history_concern} এর ইতিহাস থাকায় আমাদের আরও বেশি সতর্ক থাকতে হবে।"
        elif risk_level == RiskLevel.HIGH:
            body = f"এই লক্ষণটি অবহেলা করা ঠিক হবে না। আপনার উচিত {action}। এতে আমরা নিশ্চিত হতে পারব সব ঠিক আছে কি না।"
        elif risk_level == RiskLevel.MODERATE:
            body = f"শরীর একটু খারাপ লাগা স্বাভাবিক। আপনি {action}। এতে আপনি আরাম পাবেন।"
        else:
            body = f"এটি একটি সাধারণ সমস্যা। {action} বিশ্রাম নিলে ভালো লাগবে।"

        # Phase 4: Agency Rule
        empowerment = "আমরা একসাথে সঠিক পদক্ষেপ নিচ্ছি।"
        
        full_response = f"{intro} {body} {empowerment}"
        
        # Apply Noakhali Dialect for regional touch - DISABLED
        # return self._apply_noakhali_dialect(full_response)
        return full_response



# Global instance
triage_service = TriageService()
