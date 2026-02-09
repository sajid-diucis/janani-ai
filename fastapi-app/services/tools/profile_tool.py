from typing import Dict, Any, Optional
import traceback
from services.tools.tool_interface import ToolResult
from services.patient_state import update_patient

async def update_profile(params: Dict[str, Any], profile: Dict[str, Any]) -> ToolResult:
    """Update patient profile via voice command"""
    TOOL_NAME = "UPDATE_PROFILE"
    print(f"🔧 {TOOL_NAME} START: params={params}, current_user={profile.get('user_id')}")
    
    try:
        user_id = profile.get("user_id", "default_user")
        updates = {}

        if isinstance(params.get("profile"), dict):
            profile_data = params.get("profile") or {}
            user_id = profile_data.get("user_id", user_id)
            updates = {k: v for k, v in profile_data.items() if k != "user_id"}
            if "week_number" in updates and "weeks_pregnant" not in updates:
                updates["weeks_pregnant"] = updates.get("week_number")
            if "weeks_pregnant" in updates and "trimester" not in updates:
                try:
                    w = int(updates.get("weeks_pregnant"))
                    if w <= 12:
                        updates["trimester"] = "first"
                    elif w <= 26:
                        updates["trimester"] = "second"
                    else:
                        updates["trimester"] = "third"
                except Exception:
                    pass
        
        if "name" in params:
            updates["name"] = params["name"]
        
        if "week" in params:
            try:
                # Handle "25 সপ্তাহ" -> 25
                w = str(params["week"]).replace("সপ্তাহ", "").strip()
                updates["weeks_pregnant"] = int(w)
                
                # Auto-calc trimester
                week_int = int(w)
                if week_int <= 12: updates["trimester"] = "first"
                elif week_int <= 26: updates["trimester"] = "second"
                else: updates["trimester"] = "third"
            except:
                pass
                
        if "age" in params:
            try:
                updates["age"] = int(params["age"])
            except:
                pass
        
        # [NEW] Handle Location
        if "location" in params and params["location"]:
            updates["location"] = params["location"]

        if not updates:
             # Instead of error, return a prompt for details
             print(f"⚠️ {TOOL_NAME}: No updates found, prompting user.")
             current_name = profile.get("name", "Unknown")
             return ToolResult(
                success=True, # Return success so frontend shows the message
                tool_name=TOOL_NAME,
                message=f"আপনার প্রোফাইল আপডেট করতে, দয়া করে বলুন: 'আমার নাম [নাম] এবং আমি [সপ্তাহ] সপ্তাহের গর্ভবতী' \n\n(বর্তমানে: {current_name})",
                data=profile # Return current profile so UI can show it
            )
            
        # Update state
        new_state = update_patient(user_id, updates)
        
        message = f"✅ প্রোফাইল আপডেট করা হয়েছে!\n"
        if "name" in updates: message += f"• নাম: {updates['name']}\n"
        if "weeks_pregnant" in updates: message += f"• সপ্তাহ: {updates['weeks_pregnant']}\n"
        if "age" in updates: message += f"• বয়স: {updates['age']}\n"
        
        print(f"✅ {TOOL_NAME} SUCCESS: {updates}")
        
        return ToolResult(
            success=True,
            tool_name=TOOL_NAME,
            message=message,
            data=updates
        )
    
    except Exception as e:
        print(f"❌ {TOOL_NAME} CRITICAL ERROR: {e}")
        traceback.print_exc()
        return ToolResult(
            success=False,
            tool_name=TOOL_NAME,
            message=f"প্রোফাইল আপডেট করতে সমস্যা হয়েছে। (Error: {str(e)[:50]})",
            error=str(e)
        )
