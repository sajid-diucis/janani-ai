
from services.care_plan_service import care_plan_service
from models.care_models import MaternalRiskProfile, Trimester, RiskLevel
from datetime import date

def test_plan_generation():
    print("Testing Weekly Care Plan Generation...")
    
    # Create a profile that resembles what might come from the DB
    profile = MaternalRiskProfile(
        user_id="test_user_plan",
        name="Test Mother",
        age=28,
        current_week=20,
        trimester=Trimester.SECOND,
        bmi=24.5,
        blood_pressure_systolic=120,
        hemoglobin_level=12.5,
        existing_conditions=["Diabetes"],
        has_gestational_diabetes=True # High risk flag
    )
    
    try:
        plan = care_plan_service.generate_weekly_plan(profile)
        print(f"Plan generated successfully for week {plan.week_number}")
        print(f"Risk Level: {plan.current_risk_level}")
        print(f"Development: {plan.week_summary_bengali}")
        return True
    except Exception as e:
        print(f"Plan generation FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_plan_generation()
