"""
Emergency Tool - Activates emergency bridge and returns AR dashboard redirect
"""
from typing import Dict, Any
import traceback
from services.tools.tool_interface import ToolResult

async def activate_emergency(params: Dict[str, Any], profile: Dict[str, Any]) -> ToolResult:
    """
    Activate emergency bridge for critical/urgent situations.
    Returns redirect info for AR dashboard.
    """
    TOOL_NAME = "ACTIVATE_EMERGENCY"
    print(f"🚨 {TOOL_NAME} START: params={params}, user={profile.get('user_id')}")
    
    try:
        from services.emergency_bridge_service import emergency_bridge_service
        from models.care_models import EmergencyBridgeRequest, RedFlagType
        
        reason = params.get("reason", "emergency_detected")
        query = params.get("query", "")
        user_id = profile.get("user_id", "default_user")
        
        # Map reason to RedFlagType if possible
        red_flags_list = []
        reason_lower = reason.lower()
        
        if any(x in reason_lower for x in ["bleeding", "রক্তপাত", "hemorrhage"]):
            red_flags_list.append(RedFlagType.HEMORRHAGE)
        elif any(x in reason_lower for x in ["seizure", "convulsion", "খিঁচুনি", "অজ্ঞান", "unconscious", "pre-eclampsia", "pressure"]):
            red_flags_list.append(RedFlagType.CONVULSIONS) 
            # Note: Unconscious could be eclampsia or other, defaulting to high priority
        elif any(x in reason_lower for x in ["pain", "ব্যথা", "ব্যাথা"]):
             # Generic severe pain might not translate directly to a standard red flag enum 
             # without more info, but let's try pre-term labor if pain implies it?
             # For now, safe to leave empty if no specific enum matches, 
             # logic will still trigger emergency bridge but maybe with generic protocols
             pass
             
        # Create emergency bridge request
        emergency_request = EmergencyBridgeRequest(
            user_id=user_id,
            trigger_source="voice_emergency",
            detected_emergency=reason,
            red_flags=red_flags_list,
            patient_location=profile.get("location", None)
        )
        
        # Activate emergency bridge
        bridge_response = await emergency_bridge_service.activate_emergency_bridge(emergency_request)
        
        # [NEW] Delegate Physical Call to Execution Client (Port 8001)
        try:
             from services.execution_bridge import delegate_to_agent
             # Fire and forget (don't await strictly or ignore error)
             call_params = {
                 "location": profile.get("location") or "Dhaka, Bangladesh",
                 "condition": reason,
                 "phone": "999" # In real demo, this might be a specific number
             }
             print("🚑 TRIGGERING AGENT call_ambulance...")
             await delegate_to_agent("emergency_call", call_params)
        except Exception as e:
             print(f"⚠️ AGENT CALL FAILED: {e}")
        
        # Create response message in Bengali
        message = f"""🚨 **জরুরি সেবা সক্রিয় হয়েছে!**

আপনার জরুরি অবস্থা শনাক্ত হয়েছে: **{reason}**

📍 **নিকটতম হাসপাতাল:** {bridge_response.nearest_hospital if bridge_response.nearest_hospital else 'তথ্য নেই'}
📞 **জরুরি নম্বর:** ১৬২৬৩

⚠️ **এখনই এই পদক্ষেপ নিন:**
{bridge_response.immediate_steps_bengali[0] if bridge_response.immediate_steps_bengali else 'শান্ত থাকুন এবং সাহায্যের জন্য অপেক্ষা করুন।'}

---
🔴 AR জরুরি ড্যাশবোর্ড চালু হচ্ছে...
"""

        data = {
            "emergency_activated": True,
            "emergency_redirect": "http://localhost:8000/ar-dashboard",
            "reason": reason,
            "hospital": bridge_response.nearest_hospital,
            "emergency_contacts": emergency_bridge_service.emergency_contacts,
            "immediate_steps": bridge_response.immediate_steps_bengali
        }
        
        print(f"✅ {TOOL_NAME} SUCCESS - Emergency activated for: {reason}")
        
        return ToolResult(
            success=True,
            tool_name=TOOL_NAME,
            message=message,
            data=data
        )
    
    except Exception as e:
        print(f"❌ {TOOL_NAME} CRITICAL ERROR: {e}")
        traceback.print_exc()
        
        # Even on error, return emergency redirect
        return ToolResult(
            success=False,
            tool_name=TOOL_NAME,
            message=f"🚨 জরুরি সেবা সক্রিয় করতে সমস্যা হয়েছে। এখনই ১৬২৬৩ এ কল করুন!",
            data={
                "emergency_activated": True,
                "emergency_redirect": "http://localhost:8000/ar-dashboard",
                "error": str(e)
            },
            error=str(e)
        )
