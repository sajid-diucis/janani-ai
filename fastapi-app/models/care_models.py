"""
Digital Midwife - Care Plan & Risk Models
Based on WHO Maternal Health Guidelines
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


# ==================== ENUMS ====================

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    # Added for clarity in RAG
    UNKNOWN = "unknown"

class Trimester(str, Enum):
    FIRST = "first"    # Weeks 1-12
    SECOND = "second"  # Weeks 13-26
    THIRD = "third"    # Weeks 27-40

class RedFlagType(str, Enum):
    HYPERTENSION = "hypertension"
    ANEMIA = "anemia"
    GESTATIONAL_DIABETES = "gestational_diabetes"
    PREECLAMPSIA = "preeclampsia"
    ECLAMPSIA = "eclampsia"
    HEMORRHAGE = "hemorrhage"
    INFECTION = "infection"
    PRETERM_LABOR = "preterm_labor"
    FETAL_DISTRESS = "fetal_distress"
    RUPTURE_OF_MEMBRANES = "rom"
    CONVULSIONS = "convulsions"

class SymptomSeverity(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    EMERGENCY = "emergency"

class FacilityType(str, Enum):
    CLINIC = "clinic"
    HOSPITAL = "hospital"
    EMERGENCY_UNIT = "emergency_unit"
    COMMUNITY_HEALTH_CENTER = "community_health_center"

class TransportUrgency(str, Enum):
    IMMEDIATE = "immediate"
    WITHIN_HOUR = "within_hour"
    CAN_WAIT = "can_wait"

class MemoryCategory(str, Enum):
    CONCERN = "concern"
    SYMPTOM = "symptom"
    QUESTION = "question"
    EMOTIONAL = "emotional"

class ValidationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


# ==================== SUPPORTING TYPES ====================

class MedicalCondition(BaseModel):
    name: str
    severity: RiskLevel
    diagnosed_date: Optional[date] = None
    managed: bool = False
    notes: Optional[str] = None

class PatientMemory(BaseModel):
    date: datetime = Field(default_factory=datetime.now)
    context: str
    resolved: bool = False
    category: MemoryCategory = MemoryCategory.CONCERN

class VitalSignsRecord(BaseModel):
    recorded_at: datetime = Field(default_factory=datetime.now)
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: Optional[int] = None
    weight_kg: float
    temperature_celsius: Optional[float] = None
    notes: Optional[str] = None

class EmergencyContact(BaseModel):
    name: str
    relation: str
    phone: str
    alternative_phone: Optional[str] = None

class CheckupRecord(BaseModel):
    date: date
    provider: str
    findings: List[str] = Field(default_factory=list)
    prescribed_medications: List[str] = Field(default_factory=list)
    next_appointment: Optional[date] = None

class DocumentProfile(BaseModel):
    """Refined model for document extraction results (P0 Improvement)"""
    extracted_at: datetime = Field(default_factory=datetime.now)
    filename: str
    raw_text_snippet: str
    structured_info: Dict[str, Any]
    extraction_confidence: float = 0.0
    validation_status: ValidationStatus = ValidationStatus.PENDING
    extracted_by_model: str = "gemini-1.5-flash"
    schema_version: str = "1.1"


# ==================== PATIENT PROFILE ====================

class MaternalRiskProfile(BaseModel):
    """Complete maternal risk assessment profile"""
    user_id: str
    name: str = "মা"
    age: int = 25
    height_cm: float = 155.0
    pre_pregnancy_weight_kg: float = 55.0
    current_weight_kg: float = 58.0
    blood_group: Optional[str] = None
    
    # Pregnancy details
    lmp_date: Optional[date] = None  # Last Menstrual Period
    edd: Optional[date] = None  # Expected Due Date
    current_week: int = 20
    trimester: Trimester = Trimester.SECOND
    gravida: int = 1  # Number of pregnancies
    para: int = 0  # Number of deliveries
    is_first_pregnancy: bool = True
    
    # Emergency & Support
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    nearby_hospital_name: Optional[str] = None
    
    # Risk factors
    bmi: float = 22.0
    hemoglobin_level: Optional[float] = None  # g/dL
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    fasting_blood_sugar: Optional[float] = None  # mg/dL
    gestational_diabetes_screening: Optional[Dict[str, Any]] = None # P0: {"date": "...", "result": "..."}
    last_checkup_date: Optional[date] = None # P0
    
    # Fast-track Risk Flags (for RAG speed)
    has_gestational_diabetes: bool = False
    has_hypertension: bool = False
    has_anemia: bool = False
    
    # Structured History (P0 Improvement)
    existing_conditions_v2: List[MedicalCondition] = Field(default_factory=list)
    vital_signs_history: List[VitalSignsRecord] = Field(default_factory=list)
    checkup_history: List[CheckupRecord] = Field(default_factory=list)
    emergency_contact: Optional[EmergencyContact] = None
    
    # Legacy fields (keep for compatibility during transition)
    existing_conditions: List[str] = Field(default_factory=list)
    previous_complications: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    
    # Social factors (affect risk)
    education_level: Optional[str] = None
    occupation: Optional[str] = None
    monthly_income_bdt: Optional[float] = None
    has_anc_access: bool = True  # Antenatal care access
    distance_to_hospital_km: Optional[float] = None
    
    # Calculated risk
    overall_risk_level: RiskLevel = RiskLevel.LOW
    active_red_flags: List[str] = Field(default_factory=list)
    
    # AI Memory (P0 Type Safety)
    recent_memories: List[PatientMemory] = Field(default_factory=list)
    
    # Lifestyle Data
    lifestyle_factors: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }

    @property
    def current_bmi(self) -> float:
        """Dynamically calculate BMI from latest measurements"""
        if self.height_cm > 0:
            return round(self.current_weight_kg / (self.height_cm / 100)**2, 1)
        return 0.0

    def calculate_week_from_lmp(self) -> Optional[int]:
        """Calculate current week based on LMP date"""
        if self.lmp_date:
            today = date.today()
            if isinstance(self.lmp_date, str):
                from datetime import date as dt_date
                lmp = dt_date.fromisoformat(self.lmp_date)
            else:
                lmp = self.lmp_date
            
            diff_days = (today - lmp).days
            if 0 < diff_days < 300: # Standard pregnancy range
                week = (diff_days // 7) + 1
                return min(max(week, 1), 42)
        return None

    # Pydantic V2 Validators (or V1 if env is older)
    try:
        from pydantic import field_validator
        @field_validator('current_week')
        @classmethod
        def validate_week(cls, v):
            if not 1 <= v <= 42:
                raise ValueError("Week must be between 1 and 42")
            return v
    except ImportError:
        from pydantic import validator
        @validator('current_week')
        def validate_week(cls, v):
            if not 1 <= v <= 42:
                raise ValueError("Week must be between 1 and 42")
            return v


# ==================== SYMPTOMS & TRIAGE ====================

class Symptom(BaseModel):
    """Single symptom report"""
    symptom_id: str
    name_bengali: str
    name_english: str
    severity: SymptomSeverity
    duration_hours: Optional[float] = None
    frequency: Optional[str] = None  # once, recurring, continuous
    associated_symptoms: List[str] = Field(default_factory=list)
    reported_at: datetime = Field(default_factory=datetime.now)

class SymptomReport(BaseModel):
    """Patient symptom report for triage"""
    user_id: str
    symptoms: List[Symptom]
    voice_transcript: Optional[str] = None
    dialect: str = "standard_bangla"  # standard_bangla, sylheti, chittagonian, etc.
    reported_via: str = "voice"  # voice, text, form
    patient_concern: Optional[str] = None
    vitals_if_available: Optional[Dict[str, Any]] = None

class TriageResult(BaseModel):
    """Result of symptom triage"""
    user_id: str
    risk_level: RiskLevel
    detected_red_flags: List[RedFlagType] = Field(default_factory=list)
    primary_concern: str
    primary_concern_bengali: str
    
    # Actions
    immediate_action: str
    immediate_action_bengali: str
    should_trigger_emergency: bool = False
    recommended_timeframe: str  # "immediate", "within_1_hour", "within_24_hours", "routine"
    
    # Advice
    home_care_advice: List[str] = Field(default_factory=list)
    warning_signs_to_watch: List[str] = Field(default_factory=list)
    
    # For emergency bridge
    emergency_contact_needed: bool = False
    hospital_referral_needed: bool = False
    ambulance_needed: bool = False
    
    # New Emergency Domain Fields (P0)
    recommended_facility_type: FacilityType = FacilityType.CLINIC
    transport_urgency: TransportUrgency = TransportUrgency.CAN_WAIT
    call_ambulance: bool = False
    symptoms_to_monitor: List[str] = Field(default_factory=list)
    expected_wait_safety_bengali: str = "পরিস্থিতি এখন স্থিতিশীল।"
    
    # Audio response for voice-first
    response_audio_text: str = ""
    confidence_score: float = 0.0


# ==================== WEEKLY CARE PLAN ====================

class WeeklyCheckItem(BaseModel):
    """Single check/task for the week"""
    item_id: str
    title_bengali: str
    title_english: str
    description_bengali: str
    category: str  # nutrition, exercise, checkup, medication, warning_signs
    priority: str  # high, medium, low
    is_completed: bool = False
    due_by: Optional[str] = None  # e.g., "daily", "once this week"

class NutritionGuideline(BaseModel):
    """Nutrition recommendation for the week"""
    nutrient: str
    daily_requirement: float
    unit: str
    food_sources_bengali: List[str]
    importance_bengali: str
    deficiency_risk: str  # what happens if deficient

class ExerciseRecommendation(BaseModel):
    """Safe exercise for the week"""
    exercise_bengali: str
    exercise_english: str
    duration_minutes: int
    frequency_per_week: int
    benefits_bengali: str
    precautions_bengali: List[str]
    contraindications: List[str]  # conditions where this should be avoided

class WarningSign(BaseModel):
    """Warning sign to watch for"""
    sign_bengali: str
    sign_english: str
    severity: str  # mild, moderate, severe
    action_required_bengali: str
    is_emergency: bool = False

class WeeklyCarePlan(BaseModel):
    """Complete weekly care plan based on WHO guidelines"""
    user_id: str
    week_number: int
    trimester: Trimester
    generated_at: datetime = Field(default_factory=datetime.now)
    
    # Overview
    week_title_bengali: str
    week_summary_bengali: str
    baby_development_bengali: str
    mother_changes_bengali: str
    
    # Risk assessment
    current_risk_level: RiskLevel
    active_concerns: List[str] = Field(default_factory=list)
    
    # Checklist
    weekly_checklist: List[WeeklyCheckItem] = Field(default_factory=list)
    
    # Nutrition
    nutrition_focus: List[str]  # This week's priority nutrients
    nutrition_guidelines: List[NutritionGuideline] = Field(default_factory=list)
    foods_to_emphasize: List[str] = Field(default_factory=list)
    foods_to_avoid: List[str] = Field(default_factory=list)
    
    # Exercise
    exercise_recommendations: List[ExerciseRecommendation] = Field(default_factory=list)
    exercises_to_avoid: List[str] = Field(default_factory=list)
    
    # Medical
    recommended_tests: List[str] = Field(default_factory=list)
    medications_reminders: List[str] = Field(default_factory=list)
    vaccination_due: List[str] = Field(default_factory=list)
    next_anc_visit: Optional[str] = None
    
    # Warning signs
    warning_signs: List[WarningSign] = Field(default_factory=list)
    
    # Tips
    self_care_tips_bengali: List[str] = Field(default_factory=list)
    partner_support_tips_bengali: List[str] = Field(default_factory=list)


# ==================== EMERGENCY BRIDGE ====================

class EmergencyBridgeRequest(BaseModel):
    """Request to activate emergency bridge"""
    user_id: str
    trigger_source: str  # "voice_triage", "manual", "auto_detection"
    detected_emergency: str
    red_flags: List[RedFlagType]
    patient_location: Optional[Dict[str, float]] = None  # lat, lng
    patient_phone: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    patient_profile: Optional[Dict[str, Any]] = None

class EmergencyBridgeResponse(BaseModel):
    """Emergency bridge activation response"""
    bridge_id: str
    status: str  # "activated", "connecting", "connected", "failed"
    
    # Immediate guidance
    immediate_steps_bengali: List[str]
    do_not_do_bengali: List[str]
    
    # Contacts
    emergency_number: str = "999"
    nearest_hospital: Optional[str] = None
    hospital_phone: Optional[str] = None
    hospital_distance_km: Optional[float] = None
    hospital_lat: Optional[float] = None
    hospital_lng: Optional[float] = None
    emergency_unit: Optional[str] = None
    available_doctors: List[Dict[str, Any]] = Field(default_factory=list)
    
    # AR guidance available
    ar_guidance_available: bool = False
    ar_guidance_type: Optional[str] = None  # "labor_support", "first_aid", etc.
    
    # Voice guidance
    voice_guidance_text: str
    
    # Tracking
    estimated_response_time: Optional[str] = None
    ambulance_dispatched: bool = False
    
    # New: Nearby helpers
    nearest_volunteers: List[Dict[str, Any]] = Field(default_factory=list)


# ==================== OFFLINE SYNC ====================

class OfflineSyncStatus(BaseModel):
    """Status of offline data sync"""
    user_id: str
    last_sync_at: Optional[datetime] = None
    pending_symptom_reports: int = 0
    pending_checklist_updates: int = 0
    cached_care_plans_weeks: List[int] = Field(default_factory=list)
    offline_mode_since: Optional[datetime] = None
    needs_sync: bool = False


# ==================== API REQUESTS/RESPONSES ====================

class GenerateCarePlanRequest(BaseModel):
    """Request to generate weekly care plan"""
    user_id: str
    week_number: Optional[int] = None  # If not provided, calculate from profile
    force_regenerate: bool = False

class TriageRequest(BaseModel):
    """Request for voice/text triage"""
    user_id: str
    input_type: str = "text"  # "text", "voice_transcript"
    input_text: str
    dialect: str = "standard_bangla"
    include_history: bool = True  # Cross-reference with patient history
    patient_location: Optional[Dict[str, float]] = None

class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment"""
    user_id: str
    include_vitals: bool = True
    vitals: Optional[Dict[str, Any]] = None

class RiskAssessmentResponse(BaseModel):
    """Risk assessment result"""
    user_id: str
    overall_risk: RiskLevel
    risk_factors: List[Dict[str, Any]]
    red_flags: List[RedFlagType]
    recommendations_bengali: List[str]
    next_steps_bengali: List[str]
    requires_immediate_attention: bool = False

# ==================== DOCTOR/CLINICAL MODE ====================

class DifferentialDiagnosis(BaseModel):
    """Potential diagnosis with likelihood analysis"""
    condition_name: str
    likelihood: str  # High, Moderate, Low
    supporting_evidence: List[str]  # Facts from history/vitals
    red_flags: List[str]  # Critical warning signs active

class ClinicalIntervention(BaseModel):
    """Recommended clinical action"""
    action: str
    urgency: str  # Immediate, Urgent, Routine
    rationale: str

class ClinicalInsightReport(BaseModel):
    """High-density medical report for Doctor Handoff"""
    patient_id: str
    generated_at: datetime = Field(default_factory=datetime.now)
    
    # Synthesis
    clinical_summary: str  # Concise 2-line header
    potential_causality: str  # Physiological trigger analysis
    
    # Analysis
    differential_diagnoses: List[DifferentialDiagnosis]
    
    # Action Plan
    recommended_interventions: List[ClinicalIntervention]
    contraindications: List[str] = Field(default_factory=list)
    
    # Metadata
    confidence_score: float
    required_specialist: Optional[str] = None  # e.g. "Obstetrician", "Cardiologist"
