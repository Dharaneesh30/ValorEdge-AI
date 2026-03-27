from fastapi import APIRouter, HTTPException

from services.forecast_service import ForecastService
from services.ai_advice_service import AIAdviceService
from api.routes._paths import dataset_csv_path

router = APIRouter()
ai_service = AIAdviceService()

@router.get("")
def get_forecast():
    try:
        service = ForecastService(dataset_csv_path())
        result = service.run_forecast()

        trend = result.get("trend", "Stable")
        combined = result.get("arima_forecast", []) + result.get("smoothing_forecast", [])

        ai_advice = ai_service.get_forecast_advice(
            forecast_values=result.get("arima_forecast", []),
            trend=trend,
            current_score=service.df["reputation_score"].mean() if "reputation_score" in service.df.columns else 0.0
        )

        return {
            **result,
            "ai_advice": ai_advice
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
