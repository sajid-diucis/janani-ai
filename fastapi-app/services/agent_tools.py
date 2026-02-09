import json
import re
from typing import Dict, Any, Tuple, Optional
from services.ai_service import AIService
from services.patient_state import update_patient

# Build a Tool Registry logic
# We map tool names to their execution functions

# Initialize services
ai_service = AIService()

def detect_tool_from_query(user_query: str, ai_response: str = "") -> Optional[Tuple[str, Dict]]:
    """
    Determine if a user query requires a specific tool execution.
    Returns (tool_name: str, params: Dict) or None.
    """
    query_lower = user_query.lower()
    
    # [NEW] Normalize Bengali Numerals to English
    # ০-৯ (09E6-09EF) -> 0-9
    translation = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    query_lower = query_lower.translate(translation)
    
    # 0. EMERGENCY ACTIVATION (HIGHEST PRIORITY - checked first!)
    emergency_keywords = [
        # English
        "emergency", "bleeding", "seizure", "unconscious", "serious", "critical",
        "help", "ambulance", "hospital", "dying", "severe pain", "convulsion",
        # Bengali - Core
        "জরুরি", "রক্তপাত", "রক্ত", "অজ্ঞান", "হঠাৎ", "গুরুতর", "বাঁচাও",
        "মৃত্যু", "ভয়ংকর", "প্রচন্ড ব্যথা", "খিঁচুনি",
        # Romanized Bengali
        "rokto", "rokto porche", "rokto jacche", "rokto jachche", "rokto ber hocche",
        "rokto ber hocche", "rokto hocche", "rokto berhochhe", "rokto ber",
        "oshustho", "oshustho lagche", "beche thakte", "khichuni", "agyan",
        # Bengali - Extended (common phrases)
        "রক্ত পড়ছে", "রক্ত যাচ্ছে", "অনেক ব্যথা", "সাহায্য", "ডাক্তার লাগবে",
        "হাসপাতাল", "এম্বুলেন্স", "বাচ্চা নড়ছে না", "পানি ভাঙছে", "পানি ভেঙেছে"
    ]
    if any(k in query_lower for k in emergency_keywords):
        detected_keyword = next(k for k in emergency_keywords if k in query_lower)
        return ("ACTIVATE_EMERGENCY", {"reason": detected_keyword, "query": user_query})

    try:
        json_match = re.search(r'\{[\s\S]*\}', user_query)
        if json_match:
            parsed = json.loads(json_match.group(0))
            if isinstance(parsed, dict) and any(k in parsed for k in ["user_id", "name", "age", "weeks_pregnant", "week_number"]):
                return ("UPDATE_PROFILE", {"profile": parsed})
    except Exception:
        pass
    
    # 1. MENU GENERATION - Expanded Bengali keywords
    menu_keywords = [
        "মেনু", "খাবার তালিকা", "diet chart", "menu", "food plan",
        "কি খাব", "কী খাব", "খাবার", "রান্না", "পুষ্টি", "খাদ্য",
        "খাওয়ার", "তালিকা দাও", "eating", "nutrition"
    ]
    if any(k in query_lower for k in menu_keywords):
        # Extract budget param if present
        budget = 2000
        if "budget" in query_lower or "taka" in query_lower or "bdt" in query_lower or "টাকা" in query_lower:
            nums = re.findall(r'\d+', query_lower)
            if nums:
                 # Assume largest number is budget if multiple
                 candidates = [int(n) for n in nums if int(n) > 500] 
                 if candidates: budget = candidates[0]
        
        return ("GENERATE_FOOD_MENU", {"budget": budget})

    # 2. CARE PLAN - Expanded Bengali keywords for conversational queries
    care_plan_keywords = [
        "care plan", "weekly plan", "সপ্তাহের", "করণীয়", "checklist", "guideline",
        "করব", "করা", "বলো", "জানাও", "আজ কি", "আজ কী", "এখন কি", "এখন কী",
        "উপদেশ", "পরামর্শ", "advice", "what to do", "what should", "kori", "korbo"
    ]
    # Avoid matching if it's clearly a food query
    if any(k in query_lower for k in care_plan_keywords) and not any(f in query_lower for f in ["খাব", "খাওয়া", "মেনু", "menu"]):
        # Extract week if present
        week = None
        nums = re.findall(r'\d+', query_lower)
        if nums:
             candidates = [int(n) for n in nums if 4 <= int(n) <= 42]
             if candidates: week = candidates[0]
             
        return ("GET_CARE_PLAN", {"week": week})

    # 3. FOOD SAFETY
    if any(k in query_lower for k in ["safe to eat", "khawa jabe", "খেতে পারি", "নিরাপদ", "can i eat", "safe for pregnancy"]):
        # Extract food name (simple heuristic)
        food_name = "unknown"
        
        patterns = [
            r"can i eat (.*)",
            r"(.*) khete pari",
            r"(.*) khawa jabe",
            r"(.*) কি খাওয়া যাবে",
            r"is (.*) safe"
        ]
        
        for p in patterns:
            match = re.search(p, query_lower)
            if match:
                food_name = match.group(1).strip()
                break
        
        # If regex failed, just use part of the query or fallback to AI extraction later
        if food_name == "unknown":
            # Remove "safe to eat" keywords
            clean_q = query_lower
            for k in ["safe to eat", "can i eat", "is", "safe"]:
                 clean_q = clean_q.replace(k, "")
            food_name = clean_q.strip() or user_query
            
        return ("CHECK_FOOD_SAFETY", {"food_name": food_name})

    # 4. PROFILE UPDATE (NEW)
    # Added "profile", "save", "update"
    if any(k in query_lower for k in ["নাম", "বয়স", "সপ্তাহ", "name", "age", "week", "pregnant", "profile", "update", "save", "location", "অবস্থান", "থাকি", "বাড়ি", "সিটি"]):
        # Trigger if it looks like an update intent
        # [UPDATED] Added field names as triggers so "Name: X" works without "My"
        triggers = ["amar", "my", "ano", "hobe", "running", "change", "set", "update", "save", "is", "new", "create", "start", 
                   "name", "nam", "naam", "age", "boyos", "বয়স", "week", "soptaho", "সপ্তাহ", "গর্ভকাল", "location", "অবস্থান", "থাকি", "বাড়ি", "সিটি"]
        if any(k in query_lower for k in triggers):
             updates = {}
             # Extract Name (Support English + Bengali + CSV format "Name, Value")
             # Matches: "Name is X", "Nam: X", "নাম, X", "নাম X"
             name_match = re.search(r'(name is|nam|naam|name to|নাম)\s*[:,\s]\s*([a-zA-Z\s\u0980-\u09FF]+)', query_lower)
             if name_match:
                 updates["name"] = name_match.group(2).strip()

             # Extract Week (Support "20 weeks", "week 20", "গর্ভকাল, 32 সপ্তাহ")
             week_match1 = re.search(r'(\d+)\s*(weeks|sopta|soptaho|\s*সপ্তাহ)', query_lower)
             if week_match1:
                 updates["week"] = week_match1.group(1)
             
             if "week" not in updates:
                 week_match2 = re.search(r'(week|soptaha|running|গর্ভকাল)\s*[:,\s]?\s*(\d+)', query_lower)
                 if week_match2:
                     updates["week"] = week_match2.group(2)
                 
             # Extract Age (Support "25 years", "age is 25", "বয়স 26", "বয়স, 26 বছর")
             # First try prefix pattern: বয়স 25, age 25
             age_match_prefix = re.search(r'(age|boyos|বয়স)\s*[:,\s]?\s*(\d+)', query_lower)
             if age_match_prefix:
                 updates["age"] = int(age_match_prefix.group(2))
            
             # Then try suffix pattern: 25 years, 25 বছর
             if "age" not in updates:
                 age_match_suffix = re.search(r'(\d+)\s*(years|bochor|বছর)', query_lower)
                 if age_match_suffix:
                     updates["age"] = int(age_match_suffix.group(1))
                     
             # Capture full raw text for potential LLM extraction of other fields
             # (Address, History etc. - simplified for now by just catching name/week/age correctly first)
             
             # Extract Location/Address if possible
             loc_match = re.search(r'(address|location|loc|thikana|ঠিকানা|অবস্থান|থাকি|বাড়ি|সিটি)\s*(is|:)?\s*([a-zA-Z\s\u0980-\u09FF,:\-\(\)]+)', query_lower)
             if loc_match:
                  raw_loc = loc_match.group(3).strip().split('\n')[0]
                  updates["location"] = raw_loc

             # Only return if we found specific updates OR generic "update profile" intent
             if updates:
                  return ("UPDATE_PROFILE", updates)
             
             # Fallback for "save profile" without explicit data (maybe trigger interactive form or just assume success if previously set?)
             # For now, let's treat "update profile" as a valid intent even with empty params, 
             # the tool might handle it by asking or just saving current state.
             if "profile" in query_lower and ("update" in query_lower or "save" in query_lower):
                  return ("UPDATE_PROFILE", {}) 
             
             # Name update specific check
             if "name is" in query_lower or "naam" in query_lower:
                  # If regex failed but intent is clear
                  return ("UPDATE_PROFILE", {})

    # 5. EXTERNAL TASKS (Agentic Hand)
    # Detects: "Book appointment", "Schedule visit", "Call doctor"
    if any(k in query_lower for k in ["book", "appointment", "schedule", "visit", "call", "doctor", "hospital", "অ্যাপয়েন্টমেন্ট", "বুক", "ডাক্তার"]):
        # Simple extraction
        task_type = "appointment"
        params = {"query": user_query}
        
        # Check for specific locations
        if "hatirjheel" in query_lower:
             params["location"] = "hatirjheel"
             
        # Check for date (very simple)
        if "15" in query_lower or "jan" in query_lower:
             params["date"] = "15 Jan"
             
        return ("EXECUTE_EXTERNAL_TASK", {"task_type": task_type, "params": params})

    return None


async def execute_tool(tool_name: str, params: Dict, profile: Dict) -> Tuple[str, Optional[Dict]]:
    """
    Execute a specific tool and return the result message.
    Acts as a router to isolated tool implementations.
    """
    print(f"🚀 EXECUTING TOOL: {tool_name}")
    
    # Import tools locally to avoid circular imports and keep startup fast
    from services.tools.menu_tool import generate_food_menu
    from services.tools.care_plan_tool import get_care_plan
    from services.tools.food_safety_tool import check_food_safety
    from services.tools.profile_tool import update_profile
    from services.tools.emergency_tool import activate_emergency

    try:
        # Dispatch to appropriate tool function
        if tool_name == "GENERATE_FOOD_MENU":
            result = await generate_food_menu(params, profile)
        
        elif tool_name == "GET_CARE_PLAN":
            result = await get_care_plan(params, profile)
            
        elif tool_name == "CHECK_FOOD_SAFETY":
            result = await check_food_safety(params, profile)
            
        elif tool_name == "UPDATE_PROFILE":
            result = await update_profile(params, profile)
        
        elif tool_name == "ACTIVATE_EMERGENCY":
            result = await activate_emergency(params, profile)
            
        elif tool_name == "EXECUTE_EXTERNAL_TASK":
             # Use the new bridge to delegate
             from services.execution_bridge import delegate_to_agent
             from services.tools.tool_interface import ToolResult
             
             print(f"🌉 EXECUTING EXTERNAL TASK BRIDGE...")
             bridge_result = await delegate_to_agent(params.get("task_type", "appointment"), params.get("params", {}))
             
             # Format as ToolResult
             success = bridge_result.get("status") != "error"
             msg = f"Agent Execution: {bridge_result.get('message', 'Done')}"
             
             # If booking, show details
             if success and "result" in bridge_result:
                 res = bridge_result["result"]
                 if "booking_id" in res:
                     msg = f"✅ অ্যাপয়েন্টমেন্ট বুক করা হয়েছে! (Appointment Booked)\nConf: {res.get('booking_id')}\nLoc: {res.get('location', 'Unknown')}\n"
             
             result = ToolResult(
                 success=success,
                 tool_name="EXECUTE_EXTERNAL_TASK",
                 message=msg,
                 data=bridge_result
             )
            
        else:
            return (f"অজানা টুল: {tool_name}", None)
            
        # Return standardized tuple result
        return result.to_tuple()

    except Exception as e:
        print(f"❌ TOOL EXECUTION ERROR ({tool_name}): {e}")
        import traceback
        traceback.print_exc()
        return (f"টুল চালাতে সমস্যা হয়েছে। ({str(e)})", None)
