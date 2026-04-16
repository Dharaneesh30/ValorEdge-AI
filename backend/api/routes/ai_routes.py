import logging
import pandas as pd
from fastapi import APIRouter, HTTPException

try:
    from api.routes._paths import dataset_csv_path
    from services.ai_advice_service import AIAdviceService
except ModuleNotFoundError:
    from backend.api.routes._paths import dataset_csv_path
    from backend.services.ai_advice_service import AIAdviceService

router = APIRouter()
ai_service = AIAdviceService()
logger = logging.getLogger(__name__)

@router.get("/status")
def ai_status():
    return ai_service.status()


@router.get("/company-scores")
def company_scores():
    try:
        df = pd.read_csv(dataset_csv_path())
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")

        if "company" not in df.columns or "reputation_score" not in df.columns:
            raise HTTPException(status_code=400, detail="Dataset must contain company and reputation_score columns")

        scores = (
            df.groupby("company")["reputation_score"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
            .rename(columns={"reputation_score": "score"})
        )

        data = [{"company": row["company"], "score": float(row["score"])} for _, row in scores.iterrows()]
        return {"rankings": data, "companies": [item["company"] for item in data]}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask")
def ask_ai(payload: dict):
    question = payload.get("question")
    context = payload.get("context")

    if not question or not context:
        raise HTTPException(status_code=400, detail="question and context are required")

    prompt = f"You are ValorEdge AI analyst. Context: {context}. Question: {question}. Answer in max 200 words with bullet points where helpful."

    try:
        answer = ai_service.generate_text(prompt)
        if ai_service._is_provider_failure(answer):
            answer = ai_service.get_generic_fallback_answer(question=question, context=context)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
def insights():
    try:
        df = pd.read_csv(dataset_csv_path())
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")

        # Build dataset summary
        company_scores = df.groupby("company")["reputation_score"].mean().sort_values(ascending=False)
        top_companies = company_scores.head(3).to_dict()
        bottom_companies = company_scores.tail(3).to_dict()

        prompt = (
            f"Generate 5 key insights from this corporate reputation dataset. "
            f"Companies top performers: {top_companies}. "
            f"Bottom performers: {bottom_companies}. "
            "Each insight should be 1-2 sentences. Format as JSON array with fields: insight, company, type (positive/warning/caution/opportunity)."
        )

        response_text = ai_service.generate_text(prompt)

        try:
            insights_json = pd.read_json(response_text, orient="records")
            insights = insights_json.to_dict(orient="records")
        except Exception:
            # try to parse fallback from raw text
            insights = [{"insight": response_text, "company": "", "type": "opportunity"}]

        return {"insights": insights}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview")
def overview():
    try:
        df = pd.read_csv(dataset_csv_path())
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")

        stats = df.describe(include="all").to_dict()
        top_performer = df.groupby("company")["reputation_score"].mean().idxmax()
        needs_attention = df.groupby("company")["reputation_score"].mean().idxmin()

        prompt = (
            f"You are a corporate reputation analyst for ValorEdge AI. "
            f"Dataset summary stats: {stats}. "
            f"Top performer: {top_performer}, needs attention: {needs_attention}. "
            "Provide an overall analysis of the dataset in max 150 words."
        )

        analysis = ai_service.generate_text(prompt)

        return {
            "analysis": analysis,
            "top_performer": top_performer,
            "needs_attention": needs_attention
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
def compare_companies(payload: dict):
    company1 = payload.get("company1")
    company2 = payload.get("company2")

    if not company1 or not company2:
        raise HTTPException(status_code=400, detail="company1 and company2 are required")

    try:
        df = pd.read_csv(dataset_csv_path())
        subgroup = df[(df["company"] == company1) | (df["company"] == company2)]

        prompt = (
            f"Compare companies {company1} and {company2} across all metrics using dataset values. "
            f"Data points: {subgroup.to_dict(orient='records')}. "
            "Provide a concise comparison."
        )

        comparison = ai_service.generate_text(prompt)

        return {"comparison": comparison}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deep-dive")
def deep_dive(payload: dict):
    company = payload.get("company")

    if not company:
        raise HTTPException(status_code=400, detail="company is required")

    try:
        df = pd.read_csv(dataset_csv_path())
        company_df = df[df["company"] == company]

        if company_df.empty:
            raise HTTPException(status_code=404, detail="Company not found")

        prompt = (
            f"You are a corporate reputation analyst for ValorEdge AI. "
            f"Company: {company}. "
            f"Data: {company_df.to_dict(orient='records')}. "
            "Provide a full analysis including strengths, weaknesses, trend, and recommendations."
        )

        analysis = ai_service.generate_text(prompt)

        return {"analysis": analysis}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/page-insights")
def page_insights(payload: dict):
    """Generate page-specific AI insights based on context data."""
    page = payload.get("page", "dashboard")
    company = payload.get("company")
    context_data = payload.get("context_data", {})

    if not company:
        raise HTTPException(status_code=400, detail="company is required")

    try:
        df = pd.read_csv(dataset_csv_path())
        company_df = df[df["company"] == company]

        if company_df.empty:
            raise HTTPException(status_code=404, detail="Company not found")

        # Build page-specific prompts
        prompts_by_page = {
            "dashboard": _build_dashboard_insights_prompt(company, context_data, company_df, df),
            "upload": _build_upload_insights_prompt(company, context_data, company_df),
            "graphs": _build_graphs_insights_prompt(company, context_data, company_df, df),
            "analytics": _build_analytics_insights_prompt(company, context_data, company_df, df),
            "strategy": _build_strategy_insights_prompt(company, context_data, company_df, df),
            "simulation": _build_strategy_insights_prompt(company, context_data, company_df, df),
        }

        prompt = prompts_by_page.get(page, prompts_by_page["dashboard"])
        response_text = ai_service.generate_text(prompt)

        # If AI service failed, use fallback insights
        if not response_text or ai_service._is_provider_failure(response_text):
            insights = _get_fallback_insights(page, company, context_data, company_df, df)
        else:
            # Parse insights from response
            insights = _parse_insights_from_text(response_text, page)
        insights = _attach_improvement_actions(page, insights, context_data)

        return {"insights": insights}
    except HTTPException as he:
        raise he
    except Exception as e:
        # On error, return fallback insights instead of failing completely
        try:
            df = pd.read_csv(dataset_csv_path())
            company_df = df[df["company"] == company]
            fallback = _get_fallback_insights(page, company, context_data, company_df, df)
            fallback = _attach_improvement_actions(page, fallback, context_data)
            return {"insights": fallback}
        except Exception:
            raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")


def _build_dashboard_insights_prompt(company: str, context_data: dict, company_df: pd.DataFrame, all_df: pd.DataFrame) -> str:
    """Build prompt for dashboard page insights."""
    reputation_score = context_data.get("reputation_score", "N/A")
    best_model = context_data.get("best_model", "Unknown")
    
    avg_score = all_df.groupby("company")["reputation_score"].mean() if "reputation_score" in all_df.columns else None
    company_rank = (avg_score.rank(ascending=False)[company] if avg_score is not None and company in avg_score.index else "N/A")
    total_companies = len(avg_score) if avg_score is not None else 0

    prompt = (
        f"You are ValorEdge AI analyst. Provide 4-5 KEY INSIGHTS for the Dashboard page. "
        f"Company: {company}. "
        f"Current Reputation Score: {reputation_score}. "
        f"Best Model: {best_model}. "
        f"Rank: {company_rank}/{total_companies}. "
        f"Data points: {len(company_df)}. "
        f"Page result payload keys: {list((context_data or {}).keys())}. "
        "Format each insight as: [INSIGHT]: brief observation | ACTION: specific score-improvement step. "
        "Include one explicit [IMPROVEMENT STATUS] line that states improving/stable/declining and why. "
        "Focus on: KPI interpretation, trend implications, model reliability, and how this company changed versus peer companies. "
        "Keep insights concise and actionable."
    )
    return prompt


def _build_upload_insights_prompt(company: str, context_data: dict, company_df: pd.DataFrame) -> str:
    """Build prompt for upload page insights."""
    rows_processed = context_data.get("rows_processed", 0)
    best_model = context_data.get("best_model", "Unknown")

    prompt = (
        f"You are ValorEdge AI analyst reviewing a newly uploaded dataset. "
        f"Company: {company}. "
        f"Rows processed: {rows_processed}. "
        f"Best model selected: {best_model}. "
        "Provide 3-4 INITIAL OBSERVATIONS about the data quality, coverage, and what analysis steps to take next. "
        "Format each as: [OBSERVATION]: brief note | ACTION: clear next step "
        "Focus on: data completeness, sentiment distribution, date range coverage, next recommended actions."
    )
    return prompt


def _build_graphs_insights_prompt(company: str, context_data: dict, company_df: pd.DataFrame, all_df: pd.DataFrame) -> str:
    """Build prompt for graphs page insights."""
    sentiment_data = context_data.get("sentiment_trend", [])
    forecast_data = context_data.get("forecast", [])
    
    prompt = (
        f"You are ValorEdge AI analyst. Analyze visualization insights for {company}. "
        f"Sentiment records: {len(sentiment_data)}. "
        f"Forecast points: {len(forecast_data)}. "
        f"Your company vs {len(all_df['company'].unique())} total companies. "
        f"Page result payload keys: {list((context_data or {}).keys())}. "
        "Provide 4-5 GRAPH INTERPRETATION INSIGHTS about trends, patterns, and what they mean. "
        "Format each as: [GRAPH INSIGHT]: observation | ACTION: specific score-improvement step. "
        "Include one [IMPROVEMENT STATUS] line using trend direction from graph data. "
        "Focus on: sentiment momentum, forecast confidence, model variance, and comparison gaps against other companies."
    )
    return prompt


def _build_analytics_insights_prompt(company: str, context_data: dict, company_df: pd.DataFrame, all_df: pd.DataFrame) -> str:
    """Build prompt for analytics page insights."""
    feature_importance = context_data.get("feature_importance", [])
    cluster_insights = context_data.get("cluster_insights", {})

    prompt = (
        f"You are ValorEdge AI analyst. Provide ROOT-CAUSE ANALYSIS insights for {company}. "
        f"Top features: {feature_importance[:5] if feature_importance else 'N/A'}. "
        f"Clusters identified: {len(cluster_insights)}. "
        f"Page result payload keys: {list((context_data or {}).keys())}. "
        "Generate 4-5 ANALYTICAL INSIGHTS explaining why your company differs from peers. "
        "Format each as: [REASON]: explanation | ACTION: specific score-improvement step. "
        "Include one [IMPROVEMENT STATUS] line based on root-cause signals (improving/stable/declining). "
        "Focus on: feature drivers, cluster membership implications, correlation patterns, and competitive differentiation from other companies."
    )
    return prompt


def _build_strategy_insights_prompt(company: str, context_data: dict, company_df: pd.DataFrame, all_df: pd.DataFrame) -> str:
    """Build prompt for strategy/simulation page insights."""
    current_score = context_data.get("current_reputation_score", "N/A")
    projected_score = context_data.get("projected_reputation_score", "N/A")
    improvements = context_data.get("relative_improvement_percent", 0)

    prompt = (
        f"You are ValorEdge AI strategic advisor for {company}. "
        f"Current Score: {current_score}. "
        f"Projected (if scenario applied): {projected_score}. "
        f"Potential Improvement: {improvements}%. "
        f"Total companies in market: {len(all_df['company'].unique())}. "
        f"Page result payload keys: {list((context_data or {}).keys())}. "
        "Provide 5-6 STRATEGIC AI RECOMMENDATIONS with categories: "
        "[IMPROVEMENT STATUS] - overall trajectory and whether strategy improves score, "
        "[STRATEGIC PRIORITY] - critical changes, "
        "[COMPETITIVE ADVANTAGE] - differentiation opportunities, "
        "[RISK ALERT] - concerning trends, "
        "[QUICK WIN] - easy improvements, "
        "[MARKET POSITION] - positioning advice, "
        "[DATA-DRIVEN ACTION] - what the metrics tell us to do. "
        "Each should be 1-2 sentences max and include a concrete improvement action. "
        "Focus on actionable, data-backed recommendations and how to outperform peer companies."
    )
    return prompt


def _parse_insights_from_text(text: str, page: str) -> list:
    """Parse insights from AI-generated text."""
    insights = []
    
    lines = text.split("\n")
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Try to extract formatted insights
        if "[" in line and "]" in line:
            try:
                bracket_end = line.index("]")
                category = line[1:bracket_end].strip()
                insight_text = line[bracket_end + 1:].strip().lstrip("-:").strip()
                action_text = ""
                if "|" in insight_text and "ACTION:" in insight_text.upper():
                    left, right = insight_text.split("|", 1)
                    insight_text = left.strip()
                    action_text = right.replace("ACTION:", "").replace("action:", "").strip()
                elif " ACTION:" in insight_text:
                    left, right = insight_text.split(" ACTION:", 1)
                    insight_text = left.strip()
                    action_text = right.strip()
                
                if insight_text:
                    insight_obj = {
                        "insight": insight_text,
                        "category": category,
                    }
                    if action_text:
                        insight_obj["action"] = action_text
                    
                    insights.append(insight_obj)
            except (ValueError, IndexError):
                # If parsing fails, treat as plain insight
                if len(line) > 10:
                    insights.append({
                        "insight": line,
                        "category": "INSIGHT" if page not in ["strategy", "simulation"] else "ACTION",
                    })
        elif line.startswith("•") or line.startswith("-"):
            # Handle bullet points
            insight_text = line.lstrip("•-").strip()
            if insight_text:
                insights.append({
                    "insight": insight_text,
                    "category": "INSIGHT",
                })

    # Return at least some insights even if parsing is incomplete
    if not insights and text:
        # Fallback: split text into sentences
        sentences = text.split(". ")
        for sentence in sentences[:5]:
            cleaned = sentence.strip().rstrip(".")
            if cleaned and len(cleaned) > 10:
                insights.append({
                    "insight": cleaned + ".",
                    "category": "INSIGHT" if page not in ["strategy", "simulation"] else "STRATEGY",
                })

    return insights[:6]  # Return max 6 insights


def _default_action_for_insight(page: str, category: str, context_data: dict) -> str:
    cat = (category or "").upper()
    if cat in {"IMPROVEMENT STATUS", "SCORE", "KPI"}:
        return "Improve response quality on negative themes and review sentiment movement weekly."
    if cat in {"MODEL", "DATA-DRIVEN ACTION"}:
        return "Prioritize top model drivers and track RMSE/MAE changes after each update cycle."
    if cat in {"RANK", "MARKET POSITION", "COMPETITIVE ADVANTAGE"}:
        return "Benchmark against the top peer weekly and close the largest keyword/sentiment gap first."
    if cat in {"FEATURES", "REASON", "ROOTCAUSE", "CLUSTERS"}:
        return "Target the highest-impact root causes first and assign measurable 30-day KPI owners."
    if cat in {"FORECAST", "TREND", "RISK ALERT"}:
        return "Set a 7-day alert threshold and trigger corrective actions when trend weakens."
    if cat in {"QUICK WIN", "STRATEGIC PRIORITY", "ACTION", "STRATEGY", "GUIDANCE"}:
        return "Execute this as a 2-week sprint item and review score impact before the next cycle."
    if page in {"strategy", "simulation"}:
        return "Implement one high-impact change now and re-run simulation to validate score lift."
    if page == "analytics":
        return "Translate this insight into one root-cause fix and monitor feature importance change."
    if page == "graphs":
        return "Use trend and forecast changes to prioritize interventions for the next reporting window."
    return "Apply this insight as a measurable improvement step and monitor score trend weekly."


def _attach_improvement_actions(page: str, insights: list, context_data: dict) -> list:
    enriched = []
    for item in insights or []:
        if not isinstance(item, dict):
            continue
        category = str(item.get("category", "INSIGHT"))
        action = item.get("action")
        if not isinstance(action, str) or not action.strip():
            action = _default_action_for_insight(page, category, context_data or {})
        enriched.append(
            {
                "insight": str(item.get("insight", "")).strip(),
                "category": category,
                "action": action.strip(),
            }
        )
    return enriched[:6]


def _get_fallback_insights(page: str, company: str, context_data: dict, company_df: pd.DataFrame, all_df: pd.DataFrame) -> list:
    """Return data-driven fallback insights when AI service is unavailable."""
    insights = []
    
    try:
        if page == "dashboard":
            reputation_score = context_data.get("reputation_score", 0)
            best_model = context_data.get("best_model", "Unknown")
            
            insights = [
                {"insight": f"Current reputation score is {reputation_score:.3f}", "category": "SCORE"},
                {"insight": f"Best performing model is {best_model}", "category": "MODEL"},
                {"insight": f"Total data points: {len(company_df)} records", "category": "DATA"},
            ]
            
            # Add competitive rank if available
            try:
                avg_scores = all_df.groupby("company")["reputation_score"].mean().sort_values(ascending=False)
                if company in avg_scores.index:
                    rank = list(avg_scores.index).index(company) + 1
                    total = len(avg_scores)
                    insights.append({
                        "insight": f"Ranked #{rank} out of {total} companies",
                        "category": "RANK"
                    })
            except Exception:
                pass
                
        elif page == "upload":
            rows = context_data.get("rows_processed", 0)
            best_model = context_data.get("best_model", "Unknown")
            
            insights = [
                {"insight": f"Successfully processed {rows} data rows", "category": "PROCESSED"},
                {"insight": f"Pipeline selected {best_model} as best model", "category": "MODEL"},
                {"insight": "Company data is now ready for analysis", "category": "STATUS"},
                {"insight": "Visit Dashboard to see KPI metrics", "category": "NEXT"},
            ]
            
        elif page == "graphs":
            sentiment_count = len(context_data.get("sentiment_trend", []))
            forecast_count = len(context_data.get("forecast", []))
            
            insights = [
                {"insight": f"Showing {sentiment_count} sentiment data points", "category": "SENTIMENT"},
                {"insight": f"Forecast horizon includes {forecast_count} predicted values", "category": "FORECAST"},
                {"insight": "Compare trends with peer companies in the visualizations", "category": "ACTION"},
                {"insight": "Feature importance shows key drivers of performance", "category": "FEATURES"},
            ]
            
        elif page == "analytics":
            features = context_data.get("feature_importance", [])
            clusters = len(context_data.get("cluster_insights", {}))
            
            insights = [
                {"insight": f"Top {min(5, len(features))} features identified as key drivers", "category": "FEATURES"},
                {"insight": f"{clusters} distinct clusters detected in the data", "category": "CLUSTERS"},
                {"insight": "Root-cause analysis shows why your company differs", "category": "ROOTCAUSE"},
                {"insight": "PCA visualization reveals 2D structure of the data", "category": "STRUCTURE"},
            ]
            
        elif page in ["strategy", "simulation"]:
            current = context_data.get("current_reputation_score", "N/A")
            projected = context_data.get("projected_reputation_score", "N/A")
            improvement = context_data.get("relative_improvement_percent", 0)
            
            insights = [
                {"insight": f"Current reputation score: {current}", "category": "STRATEGIC PRIORITY"},
                {"insight": f"Potential improvement available: {improvement}%", "category": "QUICK WIN"},
                {"insight": "What-if scenarios help test strategic options", "category": "ACTION"},
                {"insight": "Use interactive sliders to simulate different scenarios", "category": "GUIDANCE"},
            ]
            if projected != "N/A":
                insights.insert(1, {
                    "insight": f"Projected score: {projected}",
                    "category": "STRATEGIC PRIORITY"
                })
        
        return insights if insights else [{"insight": "Data loaded successfully", "category": "STATUS"}]
        
    except Exception as e:
        logger.warning(f"Fallback insights generation failed: {e}")
        return [{"insight": "Analysis data available. Navigate to Dashboard for metrics.", "category": "STATUS"}]
