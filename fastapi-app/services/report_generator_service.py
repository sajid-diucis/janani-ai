import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models.report_models import MedicalReport, PatientEvent
from services.ai_service import AIService
from services.patient_data_service import PatientDataService

class ReportGeneratorService:
    def __init__(self):
        self.ai_service = AIService()
        self.patient_data_service = PatientDataService()

    def _generate_mock_history(self, days: int = 90) -> List[PatientEvent]:
        """
        Generates synthetic patient history for the last N days 
        to demonstrate the 1M token context capability.
        """
        events = []
        base_date = datetime.now()
        
        # Simulation parameters for a high-risk pregnancy (Preeclampsia trajectory)
        # Starting normal, then BP rising, headaches appearing
        
        for i in range(days):
            current_date = base_date - timedelta(days=days-i)
            date_str = current_date.isoformat()
            
            # 1. Vital Logs (Every 2-3 days)
            if i % 3 == 0:
                # BP creeping up
                base_systolic = 110 + (i * 0.4) + random.uniform(-5, 5) 
                base_diastolic = 70 + (i * 0.3) + random.uniform(-3, 3)
                
                events.append(PatientEvent(
                    timestamp=date_str,
                    event_type="vital_log",
                    data={
                        "bp_systolic": int(base_systolic),
                        "bp_diastolic": int(base_diastolic),
                        "weight_kg": 65 + (i * 0.05),
                        "units": "mmHg"
                    },
                    source="wearable_device"
                ))

            # 2. Voice Check-ins (Weekly)
            if i % 7 == 0:
                transcript = "Feeling okay."
                if i > 60:
                    transcript = "I have a bit of a headache today."
                if i > 80:
                    transcript = "Headache is worse, and my vision is a bit blurry."
                
                events.append(PatientEvent(
                    timestamp=date_str,
                    event_type="voice_check_in",
                    data={
                        "transcript": transcript,
                        "sentiment": "concerned" if i > 60 else "neutral",
                        "duration_seconds": 45
                    },
                    source="janani_voice_agent"
                ))
            
            # 3. Medication (Daily)
            events.append(PatientEvent(
                timestamp=date_str,
                event_type="medication_status",
                data={
                    "medication": "Iron Supplement",
                    "status": "taken" if random.random() > 0.1 else "missed"
                },
                source="user_log"
            ))

        return events

    async def generate_report(self, user_id: str) -> MedicalReport:
        # 1. Aggregate Data
        # In a real system, we would fetch from DB. Here we mock history + mix with real current context.
        history_events = self._generate_mock_history(90)
        
        # Convert events to JSON string for the prompt
        events_json = json.dumps([e.model_dump() for e in history_events], indent=2)
        
        # 2. Construct Prompt
        system_instruction = """
        You are an expert obstetrician and clinical data analyst. Your goal is decision support. 
        You are concise, factual, and strictly evidence-based. 
        You quantify all findings (e.g., '5/7 days' not 'frequent'). 
        You identify patterns humans miss, specifically acceleration in symptoms and correlations. 
        Never diagnose; only suggest evaluation.
        """
        
        analysis_logic = """
        Analyze the provided 90-day patient data stream in this order:
        1. Chief Concern Synthesis: Compare stated vs data-derived concerns.
        2. Temporal Pattern Detection: Identify trends, VELOCITY, and ACCELERATION of vitals.
        3. Correlation Detection: Flag syndromes (e.g. Preeclampsia triad).
        4. Unreported Concerns: Mismatch between logs and voice.
        5. Causal Pathway Integration: Link symptoms to mechanisms.
        6. Risk Stratification: Current vs 2 weeks vs 4 weeks ago.
        7. Action Items: Prioritized evaluations and interview questions.
        """
        
        json_schema_instruction = """
        Return the result strictly as a valid JSON object matching this schema:
        {
          "patient_metadata": { "gestational_age": int, "risk_factors": [str] },
          "chief_concern": { "stated": str, "data_derived": str, "discrepancy_note": str },
          "temporal_patterns": [
            { "metric": str, "trend": "increasing"|"decreasing"|"stable", "velocity": float, "is_accelerating": bool, "clinical_significance": str, "data_points": [{"date": str, "value": float}] }
          ],
          "unreported_concerns": [
            { "concern": str, "last_logged": str, "severity": "critical"|"important"|"minor", "suggested_question": str }
          ],
          "causal_assessment": { "summary": str, "pathway_probability": float, "intervention_points": [str] },
          "risk_stratification": { "current_risk": str, "risk_2_weeks_ago": str, "risk_4_weeks_ago": str, "drivers_of_change": [str] },
          "recommendations": [
            { "type": "evaluation"|"interview", "content": str, "rationale": str }
          ]
        }
        """

        full_prompt = f"""
        {analysis_logic}
        
        {json_schema_instruction}
        
        PATIENT DATA STREAM (Last 90 Days):
        {events_json}
        """

        # 3. Call AI
        # MOCK MODE ENABLED for Stable Demo
        try:
            # Simulate processing time for realism
            import asyncio
            await asyncio.sleep(2)
            
            return MedicalReport(
                patient_metadata={
                    "gestational_age": 40,
                    "risk_factors": ["History of Mild Anemia", "History of Hypotension", "Blood Group O+"]
                },
                chief_concern={
                    "stated": "Blurry vision and headache since this morning.",
                    "data_derived": "PREECLAMPSIA SUSPICION: Significant BP elevation (140/95) with end-organ symptoms.",
                    "discrepancy_note": "Patient history of Low BP makes current BP (140/95) a critical deviation >30mmHg rise."
                },
                temporal_patterns=[
                    {
                        "metric": "Blood Pressure",
                        "trend": "increasing",
                        "velocity": 5.0, # Significant rise
                        "is_accelerating": True,
                        "clinical_significance": "Acute hypertension relative to patient's baseline low BP.",
                        "data_points": []
                    },
                    {
                        "metric": "Hemoglobin",
                        "trend": "stable",
                        "velocity": 0.0,
                        "is_accelerating": False,
                        "clinical_significance": "Persistent mild anemia (10.8 g/dL).",
                        "data_points": []
                    }
                ],
                unreported_concerns=[
                    {
                        "concern": "Facial/Hand Swelling (Edema)",
                        "last_logged": datetime.now().isoformat(),
                        "severity": "important",
                        "suggested_question": "Have you noticed any sudden swelling in your face or hands today?"
                    },
                    {
                        "concern": "Fetal Movement",
                        "last_logged": datetime.now().isoformat(),
                        "severity": "critical",
                        "suggested_question": "Is the baby moving as much as usual today?"
                    }
                ],
                causal_assessment={
                    "summary": "Classic Preeclampsia presentation: New onset hypertension + Neurological symptoms (Visual changes/Headache).",
                    "pathway_probability": 0.98,
                    "intervention_points": ["BP Monitoring", "Urine Albumin Check", "Hospital Assessment"]
                },
                risk_stratification={
                    "current_risk": "HIGH (Immediate Evaluation Needed)",
                    "risk_2_weeks_ago": "Low (Hypotensive)",
                    "risk_4_weeks_ago": "Low",
                    "drivers_of_change": ["Sudden BP Spike", "Visual Symptoms", "Term Gestation (40w)"]
                },
                recommendations=[
                    {
                        "type": "evaluation",
                        "content": "Refer to Hospital for Preeclampsia Toxemia (PET) profile.",
                        "rationale": "Symptomatic hypertension at term requires ruling out severe preeclampsia."
                    },
                    {
                        "type": "interview",
                        "content": "Assess for epigastric pain.",
                        "rationale": "Rule out HELLP syndrome involvement."
                    }
                ]
            )

            # --- ORIGINAL AI LOGIC COMMENTED OUT FOR DEMO ---
            # response_text = await self.ai_service.get_response(
            #     message=full_prompt,
            #     user_context={"role": "obstetrician"},
            #     max_tokens=4000,
            #     json_mode=True,
            #     use_gemini=False  # <--- Switch to DeepSeek
            # )
            
            # # Clean response if needed (remove markdown code blocks)
            # clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # # Parse and Validate
            # data = json.loads(clean_text)
            # report = MedicalReport(**data)
            # return report
            
        except Exception as e:
            print(f"Error generating medical report: {e}")
            # Return a fallback/error report structure or raise
            raise e

report_generator = ReportGeneratorService()
