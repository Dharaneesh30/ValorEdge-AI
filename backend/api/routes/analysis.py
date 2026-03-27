from fastapi import APIRouter, HTTPException

from services.reputation_service import ReputationService
from analytics.scenario_simulation import ScenarioSimulation
from api.routes._paths import dataset_csv_path

router = APIRouter()


@router.get("")
def get_analysis():
    try:
        service = ReputationService(dataset_csv_path())
        result = service.run_analysis()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate")
def simulate_scenario(payload: dict):
    try:
        column = payload.get("column")
        change_percent = payload.get("change_percent")

        if column is None or change_percent is None:
            raise HTTPException(status_code=400, detail="column and change_percent are required")

        service = ReputationService(dataset_csv_path())
        df = service.df

        simulator = ScenarioSimulation(df)

        if change_percent >= 0:
            new_mean = simulator.simulate_growth(column, change_percent)
        else:
            new_mean = simulator.simulate_decline(column, abs(change_percent))

        return {
            "column": column,
            "change_percent": change_percent,
            "new_mean": float(new_mean)
        }

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
