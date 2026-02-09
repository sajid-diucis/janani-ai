from typing import Dict, Any, Optional
import traceback
from services.tools.tool_interface import ToolResult
from services.care_plan_service import care_plan_service
from models.care_models import MaternalRiskProfile

async def get_care_plan(params: Dict[str, Any], profile: Dict[str, Any]) -> ToolResult:
    """Generate weekly care plan"""
    TOOL_NAME = "GET_CARE_PLAN"
    print(f"🔧 {TOOL_NAME} START: params={params}, user={profile.get('user_id')}")
    
    try:
        week = params.get("week") or profile.get("weeks_pregnant")
        
        # Ensure week is valid integer (1-42)
        try:
            val = int(week) if week is not None else 0
            week = val if 1 <= val <= 42 else 4 # Default to 20 if invalid (safe middle ground)
            if val != week:
                print(f"⚠️ Invalid week {val} for user. Defaulting to {week} for display.")
        except:
            week = 20 # Safe default
        
        # Build a minimal profile for care plan
        maternal_profile = MaternalRiskProfile(
            user_id=profile.get("user_id", "user"),
            current_week=week,
            age=profile.get("age", 28),
            existing_conditions=profile.get("conditions", [])
        )
        
        # Generate care plan (sync method, not async)
        care_plan = care_plan_service.generate_weekly_plan(maternal_profile, week)
        
        if not care_plan:
             return ToolResult(
                success=False,
                tool_name=TOOL_NAME,
                message="কেয়ার প্ল্যান তৈরি করা যায়নি।",
                error="care_plan_service returned None"
            )

        # Convert to dict safely
        try:
            plan_dict = care_plan.model_dump() if hasattr(care_plan, 'model_dump') else care_plan.dict()
        except Exception as e:
             print(f"⚠️ Model dump failed: {e}")
             plan_dict = care_plan.__dict__ if hasattr(care_plan, '__dict__') else {}

        # Validate essential keys for frontend
        required_keys = ['baby_development_bengali', 'mother_changes_bengali', 'weekly_checklist']
        existing_keys = list(plan_dict.keys())
        print(f"📋 CARE PLAN KEYS: {existing_keys}")
        
        missing = [k for k in required_keys if k not in existing_keys]
        if missing:
             print(f"⚠️ WARNING: Missing keys in care plan: {missing}")

        # Create friendly message
        message = f"""📅 **সপ্তাহ {week} - আপনার কেয়ার প্ল্যান**

🍼 **শিশুর বিকাশ:** {plan_dict.get('baby_development_bengali', '')[:100]}...

👩 **আপনার শরীর:** {plan_dict.get('mother_changes_bengali', '')[:100]}...

✅ **এই সপ্তাহের করণীয়:**
"""
        checklist = plan_dict.get("weekly_checklist", [])
        for item in checklist[:5]:
            title = item.get("title_bengali", "")
            message += f"• {title}\n"
        
        print(f"✅ {TOOL_NAME} SUCCESS")
        
        return ToolResult(
            success=True,
            tool_name=TOOL_NAME,
            message=message,
            data=plan_dict
        )
    
    except Exception as e:
        print(f"❌ {TOOL_NAME} CRITICAL ERROR: {e}")
        traceback.print_exc()
        return ToolResult(
            success=False,
            tool_name=TOOL_NAME,
            message=f"কেয়ার প্ল্যান তৈরি করতে সমস্যা হয়েছে। (Error: {str(e)[:50]})",
            error=str(e)
        )
