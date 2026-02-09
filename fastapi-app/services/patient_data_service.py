"""
Patient Data Service
Unified data access layer that aggregates data from all sources for omniscient context.
"""
from typing import Dict, Any, Optional, List
from services.patient_state import get_patient, IN_MEMORY_DB


class PatientDataService:
    """
    Aggregates data from all sources for the omniscient agent.
    This provides a single point of access for complete patient context.
    """
    
    def get_full_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete patient context for AI agent.
        Aggregates data from:
        - Runtime state (IN_MEMORY_DB)
        - Document service (uploaded documents)
        - Emergency history
        - Care plan history
        - Food preferences
        """
        # Get base patient state
        patient = get_patient(user_id)
        
        # Try to get additional data from document service
        document_data = self._get_document_data(user_id)
        
        # Build comprehensive context
        context = {
            **patient,
            "document_profile": document_data,
            "emergency_summary": self._summarize_emergencies(patient),
            "care_plan_summary": self._summarize_care_plans(patient),
            "diet_summary": self._summarize_diet(patient)
        }
        
        return context
    
    def _get_document_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get extracted data from uploaded documents"""
        try:
            from services.document_service import document_service
            return document_service.get_user_profile(user_id)
        except Exception as e:
            print(f"Could not get document data: {e}")
            return None
    
    def _summarize_emergencies(self, patient: Dict[str, Any]) -> str:
        """Create human-readable summary of emergency history"""
        emergencies = patient.get("emergency_sessions", [])
        if not emergencies:
            return "কোনো জরুরি ঘটনা নেই (No emergency history)"
        
        summaries = []
        for e in emergencies[-5:]:  # Last 5 for prompt efficiency
            time_str = e.get("timestamp", "Unknown time")[:10]
            type_str = e.get("type", "Unknown")
            severity_str = e.get("severity", "Unknown")
            summaries.append(f"- {time_str}: {type_str} ({severity_str})")
        
        total = len(emergencies)
        if total > 5:
            summaries.append(f"... and {total - 5} more events")
        
        return "\n".join(summaries)
    
    def _summarize_care_plans(self, patient: Dict[str, Any]) -> str:
        """Create summary of care plan history"""
        plans = patient.get("care_plan_history", [])
        if not plans:
            return "কোনো কেয়ার প্ল্যান নেই (No care plan history)"
        
        latest = plans[-1]
        return f"Week {latest.get('week', '?')}: Generated on {latest.get('generated_at', '?')[:10]}"
    
    def _summarize_diet(self, patient: Dict[str, Any]) -> str:
        """Create summary of diet preferences"""
        prefs = patient.get("food_preferences", {})
        budget = prefs.get("budget", 500)
        restrictions = prefs.get("dietary_restrictions", [])
        
        if restrictions:
            return f"Budget: {budget} BDT, Restrictions: {', '.join(restrictions)}"
        else:
            return f"Budget: {budget} BDT, No dietary restrictions"
    
    def get_emergency_count(self, user_id: str) -> int:
        """Get total number of emergency events for a patient"""
        patient = get_patient(user_id)
        return len(patient.get("emergency_sessions", []))
    
    def get_recent_emergencies(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent emergency events"""
        patient = get_patient(user_id)
        emergencies = patient.get("emergency_sessions", [])
        return emergencies[-limit:] if emergencies else []
    
    def get_all_emergencies(self, user_id: str) -> List[Dict[str, Any]]:
        """Get ALL emergency events (as per user requirement)"""
        patient = get_patient(user_id)
        return patient.get("emergency_sessions", [])


# Singleton instance
patient_data_service = PatientDataService()
