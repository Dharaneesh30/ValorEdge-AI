from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
import pandas as pd

try:
    from services.full_pipeline_service import FullPipelineService
    from services.pipeline_state import pipeline_state
    from services.company_benchmark_service import CompanyBenchmarkService
    from services.ai_advice_service import AIAdviceService
except ModuleNotFoundError:
    from backend.services.full_pipeline_service import FullPipelineService
    from backend.services.pipeline_state import pipeline_state
    from backend.services.company_benchmark_service import CompanyBenchmarkService
    from backend.services.ai_advice_service import AIAdviceService


logger = logging.getLogger(__name__)
router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_PATH = PROJECT_ROOT / "backend" / "uploads" / "dataset.csv"
PIPELINE = FullPipelineService(PROJECT_ROOT)
AI_SERVICE = AIAdviceService()


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported. Required columns: date, text")

    try:
        UPLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
        content = await file.read()
        UPLOAD_PATH.write_bytes(content)

        payload = PIPELINE.run(UPLOAD_PATH)
        return {
            "message": "Dataset uploaded and full pipeline executed successfully.",
            "metadata": payload["metadata"],
            "reputation": payload["reputation"],
            "best_model": payload["models"]["best_model"],
        }
    except Exception as exc:
        logger.exception("Upload pipeline failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/eda")
def get_eda():
    data = pipeline_state.snapshot().eda
    if not data:
        raise HTTPException(status_code=404, detail="No EDA results available. Upload dataset first.")
    return data


@router.get("/sentiment")
def get_sentiment():
    data = pipeline_state.snapshot().sentiment
    if not data:
        raise HTTPException(status_code=404, detail="No sentiment results available. Upload dataset first.")
    return data


@router.get("/pca")
def get_pca():
    data = pipeline_state.snapshot().pca
    if not data:
        raise HTTPException(status_code=404, detail="No PCA results available. Upload dataset first.")
    return data


@router.get("/clusters")
def get_clusters():
    data = pipeline_state.snapshot().clusters
    if not data:
        raise HTTPException(status_code=404, detail="No clustering results available. Upload dataset first.")
    return data


@router.get("/models")
def get_models():
    data = pipeline_state.snapshot().models
    if not data:
        raise HTTPException(status_code=404, detail="No model results available. Upload dataset first.")
    return data


@router.get("/forecast")
def get_forecast():
    data = pipeline_state.snapshot().forecast
    if not data:
        raise HTTPException(status_code=404, detail="No forecast results available. Upload dataset first.")
    return data


@router.get("/genai-insights")
def get_genai_insights():
    snapshot = pipeline_state.snapshot()
    if not snapshot.genai_insights:
        raise HTTPException(status_code=404, detail="No GenAI insights available. Upload dataset first.")
    return {
        "reputation": snapshot.reputation,
        "insights": snapshot.genai_insights,
    }


@router.get("/dashboard")
def get_dashboard_view():
    snapshot = pipeline_state.snapshot()
    if not snapshot.reputation:
        raise HTTPException(status_code=404, detail="No dashboard data available. Upload dataset first.")

    trend_points = snapshot.eda.get("trend", [])
    forecast_points = snapshot.forecast.get("forecast", [])
    model_rows = snapshot.models.get("model_comparison", [])

    return {
        "reputation_score": snapshot.reputation.get("final_reputation_score"),
        "sentiment_trend": trend_points,
        "forecast": forecast_points,
        "model_summary": model_rows,
        "best_model": snapshot.models.get("best_model"),
    }


@router.get("/analytics")
def get_analytics_view():
    snapshot = pipeline_state.snapshot()
    if not snapshot.clusters:
        raise HTTPException(status_code=404, detail="No analytics data available. Upload dataset first.")

    cluster_keywords = snapshot.clusters.get("interpretation", {}).get("cluster_keywords", {})
    cluster_sizes = snapshot.clusters.get("interpretation", {}).get("cluster_sizes", {})
    feature_importance = snapshot.models.get("feature_importance", [])
    corr = snapshot.eda.get("correlation_matrix", {})
    pca = snapshot.pca.get("components", [])

    largest_cluster = None
    if cluster_sizes:
        largest_cluster = max(cluster_sizes.items(), key=lambda x: x[1])[0]
    root_cause = (
        f"Cluster {largest_cluster} dominates discussion volume; keywords suggest primary drivers: "
        f"{', '.join(cluster_keywords.get(str(largest_cluster), [])[:6])}."
        if largest_cluster is not None
        else "Cluster volume is balanced; monitor feature importance and trend shifts for root-cause updates."
    )

    return {
        "root_cause_analysis": root_cause,
        "cluster_insights": {
            "keywords": cluster_keywords,
            "sizes": cluster_sizes,
        },
        "feature_importance": feature_importance,
        "correlation_matrix": corr,
        "pca_components": pca,
    }


@router.get("/strategy")
def get_strategy_view():
    snapshot = pipeline_state.snapshot()
    if not snapshot.forecast:
        raise HTTPException(status_code=404, detail="No strategy data available. Upload dataset first.")

    reputation = float(snapshot.reputation.get("final_reputation_score", 0.5))
    forecast_vals = [float(item.get("value", 0.0)) for item in snapshot.forecast.get("forecast", [])]
    next_7 = forecast_vals[:7]
    avg_next_7 = float(sum(next_7) / len(next_7)) if next_7 else 0.0
    decline_risk = avg_next_7 < 0
    risk_level = "high" if avg_next_7 < -0.15 else "moderate" if avg_next_7 < 0 else "low"

    # Simple what-if: +10% sentiment -> +5.5% score (weight from score engine sentiment component).
    what_if_score = min(1.0, reputation + 0.055)
    what_if_pct = ((what_if_score - reputation) / max(reputation, 1e-6)) * 100

    prompt = (
        "You are a strategy advisor for corporate reputation. "
        f"Current reputation score: {reputation:.3f}. "
        f"7-day forecast average sentiment: {avg_next_7:.3f}. "
        f"Top feature importance: {(snapshot.models.get('feature_importance') or [])[:5]}. "
        "Provide targeted recommendations, risks, and quick wins."
    )
    strategy_text = AI_SERVICE.generate_text(prompt)
    provider_status = AI_SERVICE.status()

    recommendations = [
        "Improve customer support response speed and publish weekly resolution metrics.",
        "Prioritize communication around top-performing peer themes identified in benchmark keywords.",
        "Track sentiment and forecast deltas every 7 days and trigger corrective action when trend weakens.",
    ]

    risk_alerts = [
        {
            "type": "forecast_decline",
            "severity": risk_level,
            "message": "High probability of decline in next 7 days." if decline_risk else "No immediate decline signal in next 7 days.",
        }
    ]

    return {
        "recommendations": recommendations,
        "what_if_analysis": {
            "scenario": "If sentiment increases by 10%",
            "current_reputation_score": round(reputation, 4),
            "projected_reputation_score": round(what_if_score, 4),
            "relative_improvement_percent": round(float(what_if_pct), 2),
        },
        "risk_alerts": risk_alerts,
        "genai_strategy_insights": strategy_text,
        "genai_provider_status": provider_status,
    }


@router.post("/clusters/assign")
def assign_cluster(payload: dict):
    text = (payload or {}).get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    try:
        return PIPELINE.assign_text_to_cluster(text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/companies")
def get_companies():
    snapshot = pipeline_state.snapshot()
    if not snapshot.processed_path:
        raise HTTPException(status_code=404, detail="No processed dataset available. Upload dataset first.")
    try:
        df = pd.read_csv(snapshot.processed_path)
        companies = sorted(df.get("company", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
        return {"companies": companies}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/company-benchmark")
def company_benchmark(company: str):
    snapshot = pipeline_state.snapshot()
    if not snapshot.processed_path:
        raise HTTPException(status_code=404, detail="No processed dataset available. Upload dataset first.")

    try:
        df = pd.read_csv(snapshot.processed_path)
        benchmark = CompanyBenchmarkService(df).compare_one_vs_many(company)

        prompt = (
            "You are a corporate reputation strategy consultant. "
            f"Target company: {company}. "
            f"Target metrics: {benchmark['target_metrics']}. "
            f"Peer comparison: {benchmark['peer_comparison'][:5]}. "
            f"Peer-derived focus keywords: {benchmark['focus_keywords_from_peers']}. "
            "Provide concise recommendations to improve target company reputation against competitors. "
            "Include quick wins and 90-day actions."
        )
        ai_text = AI_SERVICE.generate_text(prompt)
        benchmark["ai_recommendation"] = ai_text

        return benchmark
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/scenario-simulate")
def scenario_simulate(payload: dict):
    try:
        return PIPELINE.simulate_scenario(payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
