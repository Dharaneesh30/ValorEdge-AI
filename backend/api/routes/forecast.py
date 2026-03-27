from fastapi import APIRouter, HTTPException

from services.forecast_service import ForecastService
from api.routes._paths import dataset_csv_path

router = APIRouter()


@router.get("")
def get_forecast():
    try:
        service = ForecastService(dataset_csv_path())
        return service.run_forecast()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
