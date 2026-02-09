from typing import Dict, Any, Optional
import json
import traceback
from services.tools.tool_interface import ToolResult
from services.ai_service import AIService

# Initialize service locally or pass as dependency
ai_service = AIService()

async def generate_food_menu(params: Dict[str, Any], profile: Dict[str, Any]) -> ToolResult:
    """
    Generate personalized food menu with all 3 phases (13 items total with images)
    Returns standardized ToolResult
    """
    TOOL_NAME = "GENERATE_FOOD_MENU"
    print(f"🔧 {TOOL_NAME} START: params={params}, user={profile.get('user_id')}")
    
    try:
        budget = params.get("budget", 2000)
        name = profile.get("name", "মা")
        trimester = profile.get("trimester", "second")
        conditions = profile.get("conditions", [])
        
        all_items = []
        
        # Load all 3 phases to get all 13 items with images
        for phase in [1, 2, 3]:
            try:
                menu_json_str = await ai_service.generate_visual_menu_plan(
                    user_name=name,
                    trimester=trimester,
                    conditions=conditions,
                    budget=budget,
                    phase=phase
                )
                
                menu_data = json.loads(menu_json_str)
                # Handle field name variations
                phase_items = menu_data.get("items", []) or menu_data.get("menu_items", [])
                all_items.extend(phase_items)
            except Exception as e:
                print(f"⚠️ Error loading phase {phase}: {e}")
                # Continue even if one phase fails
        
        print(f"📋 MENU ITEMS COUNT: {len(all_items)} (all phases)")
        
        if not all_items:
            return ToolResult(
                success=False,
                tool_name=TOOL_NAME,
                message="দুঃখিত, কোনো মেনু আইটেম লোড করা যায়নি। আবার চেষ্টা করুন।",
                error="No items returned from AI service"
            )

        total_cost = sum(item.get("price_bdt", 0) for item in all_items)
        
        message = f"""✅ আপনার জন্য {budget} টাকার বাজেটে পুষ্টিকর খাবারের মেনু তৈরি করেছি!

📋 **মোট {len(all_items)}টি খাবার** (আনুমানিক খরচ: ৳{total_cost})

"""
        for i, item in enumerate(all_items[:5], 1):
            name_bn = item.get("name_bangla", item.get("name_bengali", item.get("name", "")))
            price = item.get("price_bdt", 0)
            benefits = item.get("benefits", item.get("benefits_key", ""))
            message += f"{i}. **{name_bn}** - ৳{price}\n   _{benefits}_\n\n"
        
        if len(all_items) > 5:
            message += f"👆 + আরও {len(all_items) - 5}টি খাবার নিচে দেখুন!"
        
        data = {
            "menu_items": all_items,
            "budget": budget,
            "total_cost": total_cost,
            "count": len(all_items)
        }
        
        print(f"✅ {TOOL_NAME} SUCCESS")
        
        return ToolResult(
            success=True,
            tool_name=TOOL_NAME,
            message=message,
            data=data
        )
    
    except Exception as e:
        print(f"❌ {TOOL_NAME} CRITICAL ERROR: {e}")
        traceback.print_exc()
        return ToolResult(
            success=False,
            tool_name=TOOL_NAME,
            message=f"দুঃখিত, মেনু তৈরি করতে সমস্যা হয়েছে। (Error: {str(e)[:50]})",
            error=str(e)
        )
