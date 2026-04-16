from fastapi import APIRouter, HTTPException
from api.routes._paths import dataset_csv_path
from services.prediction_service import PredictionService
from api.routes._paths import dataset_csv_path

router = APIRouter()


@router.get("")
def get_prediction():
    try:
        service = PredictionService(dataset_csv_path())
        return service.run_prediction()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
