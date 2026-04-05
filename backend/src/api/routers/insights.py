from fastapi import APIRouter
from src.application import insights_service
import traceback

router = APIRouter()

@router.get("/manager-thesis")
def get_manager_thesis():
    try:
        return insights_service.generate_manager_thesis()
    except Exception as e:
        print(f"Error in manager-thesis: {e}")
        traceback.print_exc()
        return {"title": "Manager Thesis Validation", "generated_at": "", "error": str(e), "findings": []}

@router.get("/behavioral-bias")
def get_behavioral_bias():
    try:
        return insights_service.generate_behavioral_bias()
    except Exception as e:
        return {"title": "Behavioral Bias Report", "generated_at": "", "error": str(e), "findings": []}
