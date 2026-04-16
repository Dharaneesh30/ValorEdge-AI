from fastapi import APIRouter, HTTPException
from api.routes._paths import dataset_csv_path
from services.reputation_service import ReputationService
from services.ai_advice_service import AIAdviceService
from analytics.scenario_simulation import ScenarioSimulation
from api.routes._paths import dataset_csv_path

router = APIRouter()
ai_service = AIAdviceService()

@router.get("")
def get_analysis():
    try:
        service = ReputationService(dataset_csv_path())
        result = service.run_analysis()

        ai_advice = ai_service.get_analysis_advice(
            reputation_score=result.get("reputation_score", 0.0),
            top_correlations=result.get("top_correlations", {}),
            weak_areas=result.get("weak_areas", [])
        )

        return {
            **result,
            "ai_advice": ai_advice
        }
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
        before_score = service.run_analysis().get("reputation_score", 0.0)

        simulator = ScenarioSimulation(service.df)

        if change_percent >= 0:
            after_score = simulator.simulate_growth(column, change_percent)
        else:
            after_score = simulator.simulate_decline(column, abs(change_percent))

        ai_advice = ai_service.get_simulation_advice(
            column=column,
            change_percent=change_percent,
            before_score=before_score,
            after_score=after_score
        )

        return {
            "column": column,
            "change_percent": change_percent,
            # Backward-compatible key for frontend variants that still read `new_mean`.
            "new_mean": float(after_score),
            "before_score": float(before_score),
            "after_score": float(after_score),
            "impact": float(after_score - before_score),
            "ai_advice": ai_advice
        }

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
