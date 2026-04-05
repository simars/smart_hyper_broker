from fastapi import APIRouter
import insights
import traceback

router = APIRouter()

@router.get("/manager-thesis")
def get_manager_thesis():
    try:
        # Currently relies on the old `insights.py` which depends on old `normalization.get_normalized_positions()`
        # We should decouple insights so it takes positions as input, but for this pass we keep functionality intact
        # Alternatively, we rewire `insights.py` to use `portfolio_service.get_normalized_positions()`.
        return insights.generate_manager_thesis()
    except Exception as e:
        print(f"Error in manager-thesis: {e}")
        traceback.print_exc()
        return {"title": "Manager Thesis Validation", "generated_at": "", "error": str(e), "findings": []}

@router.get("/behavioral-bias")
def get_behavioral_bias():
    try:
        return insights.generate_behavioral_bias()
    except Exception as e:
        return {"title": "Behavioral Bias Report", "generated_at": "", "error": str(e), "findings": []}
