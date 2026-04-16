from __future__ import annotations

import io
import logging
import os
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
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
PRELOADED_COMPETITORS_PATH = Path(
    os.environ.get(
        "PRELOADED_COMPETITORS_PATH",
        str(PROJECT_ROOT / "backend" / "data" / "preloaded_competitors.csv"),
    )
)
PIPELINE = FullPipelineService(PROJECT_ROOT)
AI_SERVICE = AIAdviceService()
BENCHMARK_CACHE: dict[str, dict] = {}
_REPORTLAB_IMPORT_ERROR: Exception | None = None

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
except Exception as exc:
    _REPORTLAB_IMPORT_ERROR = exc


def _ensure_reportlab() -> bool:
    global _REPORTLAB_IMPORT_ERROR, letter, getSampleStyleSheet, ParagraphStyle, inch, SimpleDocTemplate, Paragraph, Spacer
    if _REPORTLAB_IMPORT_ERROR is None:
        return True
    try:
        from reportlab.lib.pagesizes import letter  # type: ignore[no-redef]
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore[no-redef]
        from reportlab.lib.units import inch  # type: ignore[no-redef]
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer  # type: ignore[no-redef]
        _REPORTLAB_IMPORT_ERROR = None
        return True
    except Exception as exc:
        _REPORTLAB_IMPORT_ERROR = exc
        return False


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    my_company: str | None = Form(default=None),
    include_preloaded_competitors: bool = Form(default=True),
    treat_upload_as_my_company: bool = Form(default=True),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported. Required columns: date, text")

    try:
        UPLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
        content = await file.read()
        incoming_df = pd.read_csv(io.BytesIO(content))
        if "date" not in incoming_df.columns or "text" not in incoming_df.columns:
            raise HTTPException(status_code=400, detail="Dataset must include required columns: date, text")

        requested_company = (my_company or "").strip()
        inferred_from_data = ""
        if "company" in incoming_df.columns:
            company_series = incoming_df["company"].fillna("").astype(str).str.strip()
            non_empty = company_series[company_series != ""]
            if not non_empty.empty:
                inferred_from_data = str(non_empty.mode().iloc[0]).strip()
        inferred_from_filename = Path(file.filename or "").stem.strip().replace("_", " ").replace("-", " ")
        chosen_company = requested_company or inferred_from_data or inferred_from_filename or "My Company"

        if treat_upload_as_my_company:
            # Force all uploaded rows to one target company label so benchmark always compares
            # "my uploaded company" versus preloaded competitors.
            incoming_df["company"] = chosen_company
        else:
            if "company" not in incoming_df.columns:
                incoming_df["company"] = chosen_company
            else:
                incoming_df["company"] = incoming_df["company"].fillna("").astype(str)
                incoming_df.loc[incoming_df["company"].str.strip() == "", "company"] = chosen_company

        # Preserve existing company data - remove old data for this company and add new data
        processed_dataset_path = PROJECT_ROOT / "backend" / "data" / "processed_dataset.csv"
        existing_df = None
        rows_removed = 0
        
        if processed_dataset_path.exists():
            try:
                existing_df = pd.read_csv(processed_dataset_path)
                # Filter out rows for the company being uploaded
                if "company" in existing_df.columns:
                    rows_before = len(existing_df)
                    existing_df = existing_df[existing_df["company"] != chosen_company]
                    rows_removed = rows_before - len(existing_df)
                    logger.info(f"Removed {rows_removed} existing rows for company '{chosen_company}' from processed dataset")
            except Exception as e:
                logger.warning(f"Could not load existing processed dataset: {e}")
                existing_df = None

        # Combine data: keep existing data for other companies + new data for this company
        if include_preloaded_competitors and PRELOADED_COMPETITORS_PATH.exists():
            competitor_df = pd.read_csv(PRELOADED_COMPETITORS_PATH)
            if "date" in competitor_df.columns and "text" in competitor_df.columns:
                incoming_df = pd.concat([incoming_df, competitor_df], ignore_index=True, sort=False)
            else:
                logger.warning("Preloaded competitor dataset skipped due to missing required columns: %s", PRELOADED_COMPETITORS_PATH)

        # Add existing data for other companies
        if existing_df is not None and len(existing_df) > 0:
            combined_df = pd.concat([incoming_df, existing_df], ignore_index=True, sort=False)
        else:
            combined_df = incoming_df

        combined_df.to_csv(UPLOAD_PATH, index=False)

        fast_upload_mode = str(os.environ.get("FAST_UPLOAD_MODE", "true")).strip().lower() not in {"0", "false", "no"}
        try:
            fast_upload_max_rows = max(500, int(os.environ.get("FAST_UPLOAD_MAX_ROWS", "1500")))
        except Exception:
            fast_upload_max_rows = 1500
        payload = PIPELINE.run(
            UPLOAD_PATH,
            fast_mode=fast_upload_mode,
            fast_max_rows=fast_upload_max_rows,
        )
        payload["metadata"]["my_company"] = chosen_company or None
        payload["metadata"]["include_preloaded_competitors"] = bool(include_preloaded_competitors)
        payload["metadata"]["treat_upload_as_my_company"] = bool(treat_upload_as_my_company)
        payload["metadata"]["preloaded_competitors_path"] = str(PRELOADED_COMPETITORS_PATH) if include_preloaded_competitors else None
        payload["metadata"]["rows_removed"] = rows_removed
        payload["metadata"]["operation"] = "update" if rows_removed > 0 else "insert"
        
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

    strategy_fast_mode = str(os.environ.get("FAST_STRATEGY_MODE", "true")).strip().lower() not in {"0", "false", "no"}
    if strategy_fast_mode:
        cached_text = (snapshot.genai_insights or {}).get("insight_text") if isinstance(snapshot.genai_insights, dict) else None
        strategy_text = (
            cached_text
            if isinstance(cached_text, str) and cached_text.strip()
            else (
                f"- Reputation score: {reputation:.3f}.\n"
                f"- Next 7-day average sentiment signal: {avg_next_7:.3f}.\n"
                "- Focus on the highest-impact features, improve negative themes quickly, and review trend weekly."
            )
        )
    else:
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
        "strategy_fast_mode": strategy_fast_mode,
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
        processed = Path(snapshot.processed_path)
        mtime = int(processed.stat().st_mtime_ns)
        benchmark_fast_mode = str(os.environ.get("FAST_BENCHMARK_MODE", "true")).strip().lower() not in {"0", "false", "no"}
        cache_key = f"{processed}:{mtime}:{company}:{int(benchmark_fast_mode)}"
        cached = BENCHMARK_CACHE.get(cache_key)
        if cached is not None:
            return cached

        df = pd.read_csv(processed)
        benchmark = CompanyBenchmarkService(df).compare_one_vs_many(company)

        if benchmark_fast_mode:
            gap_top = benchmark["peer_comparison"][0]["gap_vs_target"] if benchmark.get("peer_comparison") else 0.0
            trend = benchmark["target_metrics"].get("trend", 0.0)
            benchmark["ai_recommendation"] = (
                f"- Target company: {company}.\n"
                f"- Gap vs top peer: {gap_top:+.4f}; current trend: {trend:+.4f}.\n"
                "- Focus on peer-derived keywords and execute 30-day improvement actions."
            )
        else:
            prompt = (
                "You are an elite corporate reputation strategist. "
                f"Target company: {company}. "
                f"Target metrics: {benchmark['target_metrics']}. "
                f"Peer comparison: {benchmark['peer_comparison'][:8]}. "
                f"Peer-derived focus keywords: {benchmark['focus_keywords_from_peers']}. "
                "Analyze everything across sentiment, trend, positive-ratio, keyword gaps, and peer strengths. "
                "Goal: make the target company the top-performing peer. "
                "Return: "
                "1) top weaknesses causing peer gap, "
                "2) high-impact opportunities to overtake top peers, "
                "3) prioritized action plan (Immediate 0-30 days, 30-90 days, 90-180 days), "
                "4) KPI targets with numeric direction for each stage, "
                "5) execution risks and mitigations. "
                "Be practical, specific, and outcome-driven."
            )
            ai_text = AI_SERVICE.generate_text(prompt)
            benchmark["ai_recommendation"] = ai_text

        benchmark["benchmark_fast_mode"] = benchmark_fast_mode
        BENCHMARK_CACHE.clear()
        BENCHMARK_CACHE[cache_key] = benchmark
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


@router.get("/report/export")
def export_project_report(company: str | None = None):
    if not _ensure_reportlab():
        detail_text = "PDF export dependency missing. Install backend requirements and restart the server."
        if _REPORTLAB_IMPORT_ERROR is not None:
            detail_text = f"{detail_text} Cause: {type(_REPORTLAB_IMPORT_ERROR).__name__}: {_REPORTLAB_IMPORT_ERROR}"
        raise HTTPException(
            status_code=503,
            detail=detail_text,
        )

    snapshot = pipeline_state.snapshot()
    if not snapshot.reputation:
        raise HTTPException(status_code=404, detail="No report data available. Upload dataset first.")

    selected_company = (company or "").strip() or "My Company"
    benchmark_text = ""
    try:
        if snapshot.processed_path:
            df = pd.read_csv(snapshot.processed_path)
            if "company" in df.columns and selected_company in df["company"].astype(str).unique().tolist():
                benchmark = CompanyBenchmarkService(df).compare_one_vs_many(selected_company)
                top_peer = benchmark["peer_comparison"][0] if benchmark.get("peer_comparison") else {}
                benchmark_text = (
                    f"## Company vs Others\n"
                    f"- Target company: {selected_company}\n"
                    f"- Sentiment mean: {benchmark['target_metrics'].get('sentiment_mean')}\n"
                    f"- Trend: {benchmark['target_metrics'].get('trend')}\n"
                    f"- Positive ratio: {benchmark['target_metrics'].get('positive_ratio')}\n"
                    f"- Top peer: {top_peer.get('company', 'N/A')}\n"
                    f"- Gap vs top peer: {top_peer.get('gap_vs_target', 'N/A')}\n"
                    f"- Focus keywords: {', '.join(benchmark.get('focus_keywords_from_peers', [])[:12]) or 'N/A'}\n"
                )
    except Exception:
        benchmark_text = ""

    model_rows = snapshot.models.get("model_comparison", []) if snapshot.models else []
    sorted_models = sorted(model_rows, key=lambda x: x.get("rmse", 1e9))
    best_model = sorted_models[0] if sorted_models else {}
    second_model = sorted_models[1] if len(sorted_models) > 1 else {}
    model_justification = ""
    if best_model:
        model_justification = (
            f"## Model Justification\n"
            f"- Selected best model: {best_model.get('model')}\n"
            f"- RMSE: {best_model.get('rmse')}, MAE: {best_model.get('mae')}, R2: {best_model.get('r2')}\n"
        )
        if second_model:
            model_justification += (
                f"- Runner-up: {second_model.get('model')} (RMSE {second_model.get('rmse')})\n"
                "- Selection rule: lowest RMSE with stable MAE and competitive R2.\n"
            )

    forecast_values = [float(item.get("value", 0.0)) for item in (snapshot.forecast.get("forecast", []) if snapshot.forecast else [])]
    next_7 = forecast_values[:7]
    avg_next_7 = float(sum(next_7) / len(next_7)) if next_7 else 0.0
    risk_label = "decline risk" if avg_next_7 < 0 else "stable to positive trend"
    top_features = [item.get("feature") for item in (snapshot.models.get("feature_importance", []) if snapshot.models else [])[:5]]
    top_features_text = ", ".join([str(x) for x in top_features if x]) or "key drivers not available"
    strategy_plan = (
        "## Strategy to Improve Company Reputation\n"
        f"- Near-term signal: next 7-day average forecast is {avg_next_7:.4f} ({risk_label}).\n"
        f"- Priority model drivers: {top_features_text}.\n"
        "- Immediate (0-30 days): resolve top negative themes quickly, improve customer-response SLA, and publish weekly progress metrics.\n"
        "- Mid-term (30-90 days): align communication with top peer-performing themes and run targeted campaigns on weak sentiment clusters.\n"
        "- Long-term (90-180 days): institutionalize monthly model/forecast reviews, update initiatives by feature-impact shifts, and track peer gap reduction KPI.\n"
    )

    report_text = (
        "# ValorEdge AI - Evaluation Report\n\n"
        "## Data Preprocessing & EDA\n"
        f"- Rows processed: {snapshot.metadata.get('rows_processed') if snapshot.metadata else 'N/A'}\n"
        f"- Date range: {snapshot.eda.get('summary', {}).get('date_min', 'N/A')} to {snapshot.eda.get('summary', {}).get('date_max', 'N/A')}\n"
        f"- Correlation features: {len((snapshot.eda.get('correlation_matrix') or {}).keys())}\n\n"
        "## Dimensionality Reduction\n"
        f"- PCA components generated: {len(snapshot.pca.get('components', [])) if snapshot.pca else 0}\n"
        "- Factor analysis completed with 2 latent factors.\n\n"
        "## Clustering\n"
        f"- KMeans/Hierarchical labels: {len(snapshot.clusters.get('kmeans_labels', [])) if snapshot.clusters else 0} records\n"
        f"- Cluster keywords: {snapshot.clusters.get('interpretation', {}).get('cluster_keywords', {}) if snapshot.clusters else {}}\n\n"
        "## Predictive Modeling\n"
        f"- Best model from pipeline: {snapshot.models.get('best_model') if snapshot.models else 'N/A'}\n"
        f"- Compared models: {[m.get('model') for m in model_rows]}\n\n"
        f"{model_justification}\n"
        "## Forecast & Reputation\n"
        f"- Reputation score: {snapshot.reputation.get('final_reputation_score') if snapshot.reputation else 'N/A'}\n"
        f"- Forecast points: {len(snapshot.forecast.get('forecast', [])) if snapshot.forecast else 0}\n\n"
        "## Interpretation & Business Insights\n"
        f"- Strategy insight: {(snapshot.genai_insights or {}).get('insight_text', 'N/A') if snapshot.genai_insights else 'N/A'}\n\n"
        f"{benchmark_text}\n"
        f"{strategy_plan}\n"
        "## Conclusion\n"
        "- Project delivers full pipeline from raw text to explainable business actions.\n"
    )

    # Convert markdown text to PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles for better formatting
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor='#003366', spaceAfter=12, spaceBefore=12)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=12, textColor='#003366', spaceAfter=8, spaceBefore=8)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, leading=12)
    
    # Parse markdown and convert to reportlab elements
    lines = report_text.split('\n')
    for line in lines:
        if line.startswith('# '):
            elements.append(Paragraph(line.replace('# ', ''), title_style))
            elements.append(Spacer(1, 0.2*inch))
        elif line.startswith('## '):
            elements.append(Paragraph(line.replace('## ', ''), heading_style))
            elements.append(Spacer(1, 0.1*inch))
        elif line.strip().startswith('- '):
            bullet_text = line.strip()[2:]
            elements.append(Paragraph('• ' + bullet_text, normal_style))
        elif line.strip():
            elements.append(Paragraph(line.strip(), normal_style))
        else:
            elements.append(Spacer(1, 0.05*inch))
    
    doc.build(elements)
    pdf_buffer.seek(0)
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=valoredge_report.pdf"},
    )
