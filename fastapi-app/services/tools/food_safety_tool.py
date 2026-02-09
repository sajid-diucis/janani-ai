from typing import Dict, Any, Optional
import traceback
from services.tools.tool_interface import ToolResult
from services.food_rag_service import food_rag_pipeline
from models.food_models import FoodAnalysisRequest, TrimesterStage

async def check_food_safety(params: Dict[str, Any], profile: Dict[str, Any]) -> ToolResult:
    """Check if a specific food is safe"""
    TOOL_NAME = "CHECK_FOOD_SAFETY"
    print(f"🔧 {TOOL_NAME} START: params={params}, user={profile.get('user_id')}")
    
    try:
        food_name = params.get("food_name", "")
        if not food_name:
             return ToolResult(
                success=False,
                tool_name=TOOL_NAME,
                message="খাবারের নাম পাওয়া যায়নি।",
                error="Missing food_name param"
            )

        trimester_str = profile.get("trimester", "second")
        
        # Map string to enum
        trimester_map = {
            "first": TrimesterStage.FIRST,
            "second": TrimesterStage.SECOND,
            "third": TrimesterStage.THIRD,
            "postpartum": TrimesterStage.POSTPARTUM
        }
        trimester = trimester_map.get(trimester_str.lower(), TrimesterStage.SECOND)
        
        request = FoodAnalysisRequest(
            user_id=profile.get("user_id", "user"),
            food_name=food_name,
            trimester=trimester,
            include_nutrition=True
        )
        
        result = await food_rag_pipeline.analyze_food(request)
        
        # Extract decision
        safety = result.stage4_final.safety_decision.value if result.stage4_final else "caution"
        explanation = result.stage4_final.explanation_bengali if result.stage4_final else ""
        
        emoji = "✅" if safety == "safe" else ("⚠️" if safety == "caution" else "❌")
        
        message = f"""{emoji} **{food_name}** - {safety.upper()}

{explanation[:200]}..."""

        data = {
            "food_name": food_name, 
            "safety": safety, 
            "explanation": explanation,
            "risks": result.stage4_final.risks if result.stage4_final else [],
            "alternatives": result.stage4_final.alternatives if result.stage4_final else []
        }
        
        print(f"✅ {TOOL_NAME} SUCCESS: {safety}")

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
            message=f"খাবার পরীক্ষা করতে সমস্যা হয়েছে। (Error: {str(e)[:50]})",
            error=str(e)
        )
