from fastapi import APIRouter, HTTPException

from services.prediction_service import PredictionService
from services.ai_advice_service import AIAdviceService
from api.routes._paths import dataset_csv_path

router = APIRouter()
ai_service = AIAdviceService()

@router.get("")
def get_prediction():
    try:
        service = PredictionService(dataset_csv_path())
        result = service.run_prediction()

        ai_advice = ai_service.get_prediction_advice(
            predicted_score=result.get("predicted_score", 0.0),
            reputation_class=result.get("reputation_class", "Stable"),
            coefficients=result.get("coefficients", {})
        )

        return {
            **result,
            "ai_advice": ai_advice
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
