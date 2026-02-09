from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

# --- Input / Pipeline Models ---

class PatientEvent(BaseModel):
    timestamp: str = Field(description="ISO_8601_DATE")
    event_type: str = Field(description="voice_check_in | vital_log | medication_status | ...")
    data: Dict[str, Any]
    source: str = Field(description="system_component_id")

# --- Output / Report Schema Models ---

class PatientMetadata(BaseModel):
    gestational_age: int
    risk_factors: List[str]

class ChiefConcern(BaseModel):
    stated: str
    data_derived: str
    discrepancy_note: Optional[str] = None

class DataPoint(BaseModel):
    date: str
    value: float

class TemporalPattern(BaseModel):
    metric: str = Field(description="e.g., Systolic BP")
    trend: Literal["increasing", "decreasing", "stable", "fluctuating"]
    velocity: float = Field(description="Rate of change")
    is_accelerating: bool
    clinical_significance: str
    data_points: List[DataPoint]

class UnreportedConcern(BaseModel):
    concern: str
    last_logged: str = Field(description="ISO date-time")
    severity: Literal["critical", "important", "minor"]
    suggested_question: str = Field(description="Exact question for doctor to ask")

class CausalAssessment(BaseModel):
    summary: str
    pathway_probability: float = Field(ge=0, le=1)
    intervention_points: List[str]

class MedicalReportResponse(BaseModel):
    patient_metadata: PatientMetadata
    chief_concern: ChiefConcern
    temporal_patterns: List[TemporalPattern]
    unreported_concerns: List[UnreportedConcern]
    causal_assessment: Optional[CausalAssessment] = None
    risk_stratification: str # Simplified as string or object based on prompt, let's keep it flexible or strict
    recommendations: List[str]

    # Matching the user's strict schema structure where risk_stratification might be an object in their prompt, 
    # but in their JSON example "risk_stratification" was required but not fully defined in properties.
    # I will assume it can be a descriptive string or object. 
    # Let's check the prompt requirements again.
    # "Risk Stratification: Compare current risk vs 2 and 4 weeks ago." -> This sounds like text or a structured object.
    # The user provided schema: "required": ["patient_metadata", ... "risk_stratification"]
    # But "risk_stratification" was NOT in "properties" detail in the user's example snippet! 
    # Wait, looking closely at the user input...
    # The user input JSON schema example shows "risk_stratification" in 'required', but its definition is missing in 'properties'.
    # I will define a sensible structure for it.

class RiskStratification(BaseModel):
    current_risk: str
    risk_2_weeks_ago: str
    risk_4_weeks_ago: str
    drivers_of_change: List[str]

class ActionItem(BaseModel):
    type: Literal["evaluation", "interview"]
    content: str
    rationale: Optional[str] = None

# Refined Main Response Model
class MedicalReport(BaseModel):
    patient_metadata: PatientMetadata
    chief_concern: ChiefConcern
    temporal_patterns: List[TemporalPattern]
    unreported_concerns: List[UnreportedConcern]
    causal_assessment: Optional[CausalAssessment] = None
    risk_stratification: RiskStratification
    recommendations: List[ActionItem]
