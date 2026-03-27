import pandas as pd
from fastapi import APIRouter, HTTPException

from services.ai_advice_service import AIAdviceService
from api.routes._paths import dataset_csv_path

router = APIRouter()
ai_service = AIAdviceService()

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
