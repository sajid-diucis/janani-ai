"""
Pydantic models for AR Emergency Labor Assistant
"""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class LaborStageEnum(str, Enum):
    """Labor stages enumeration"""
    PREPARATION = "preparation"
    STAGE_1_EARLY = "stage_1_early"
    STAGE_1_ACTIVE = "stage_1_active"
    STAGE_2_CROWNING = "stage_2_crowning"
    STAGE_2_DELIVERY = "stage_2_delivery"
    STAGE_3_PLACENTA = "stage_3_placenta"
    NEWBORN_CARE = "newborn_care"
    EMERGENCY = "emergency"


class EmergencyTypeEnum(str, Enum):
    """Emergency types enumeration"""
    CORD_PROLAPSE = "cord_prolapse"
    SHOULDER_DYSTOCIA = "shoulder_dystocia"
    POSTPARTUM_HEMORRHAGE = "postpartum_hemorrhage"
    BREECH_PRESENTATION = "breech_presentation"
    MATERNAL_DISTRESS = "maternal_distress"
    FETAL_DISTRESS = "fetal_distress"


class ARInstruction(BaseModel):
    """Single AR instruction step"""
    step: int
    text_bn: str
    text_en: str
    ar_visual: str
    audio_priority: str = "medium"
    timer_seconds: Optional[int] = None


class AROverlay(BaseModel):
    """AR overlay configuration"""
    type: str
    target_angle: Optional[int] = None
    green_zone: Optional[Dict] = None
    hand_position: Optional[str] = None
    visual_cue: Optional[str] = None
    duration_seconds: Optional[int] = None


class LaborStage(BaseModel):
    """Complete labor stage with instructions"""
    stage_id: str
    title_bn: str
    title_en: str
    color: str
    icon: str
    instructions: List[ARInstruction]
    ar_overlay: Optional[AROverlay] = None
    pose_landmarks: Optional[List[str]] = None


class EmergencyProtocol(BaseModel):
    """Emergency protocol with immediate actions"""
    type: str
    title_bn: str
    title_en: str
    severity: str
    color: str
    immediate_actions: List[ARInstruction]


class SessionLogEntry(BaseModel):
    """Log entry for session tracking"""
    timestamp: datetime
    action: str
    stage: str
    details: Optional[Dict] = None


class ContractionLog(BaseModel):
    """Log entry for contraction tracking"""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    intensity: Optional[str] = None  # mild, moderate, strong
    notes: Optional[str] = None


class VitalSigns(BaseModel):
    """Patient vital signs"""
    timestamp: datetime
    maternal_heart_rate: Optional[int] = None
    fetal_heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    temperature: Optional[float] = None
    notes: Optional[str] = None


class OfflineBundle(BaseModel):
    """Complete offline data bundle"""
    stages: Dict
    emergencies: Dict
    pose_landmarks: Dict
    disclaimer: Dict
    emergency_numbers: Dict
    version: str
    last_updated: datetime


class SyncRequest(BaseModel):
    """Request to sync offline data"""
    device_id: str
    session_id: str
    session_log: List[SessionLogEntry]
    contractions: Optional[List[ContractionLog]] = None
    vitals: Optional[List[VitalSigns]] = None
    sync_timestamp: datetime


class SyncResponse(BaseModel):
    """Response after syncing"""
    success: bool
    synced_entries: int
    server_timestamp: datetime
    message_bn: str
    message_en: str
