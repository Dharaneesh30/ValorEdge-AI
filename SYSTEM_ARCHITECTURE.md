# ValorEdge AI System Architecture - Visual Overview

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER UPLOAD INTERFACE                            │
│                      ( /upload page in browser )                         │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Select CSV File     │
                    │ (e.g., TCS.csv)     │
                    └──────────┬──────────┘
                              │
                              ▼
                ┌──────────────────────────────────┐
                │  BACKEND: POST /upload           │
                │  pipeline_routes.py              │
                └──────────────┬───────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
    ┌─────────┐          ┌─────────┐          ┌─────────┐
    │ Extract │          │  Check  │          │  Load   │
    │ CSV data│          │ company │          │ old data│
    │         │          │ "TCS"   │          │         │
    └────┬────┘          └────┬────┘          └────┬────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                ┌──────────────────────────────────┐
                │  DECISION LOGIC                  │
                │                                  │
                │  Is TCS in old data? (Y/N)      │
                └──────┬─────────────────┬────────┘
                       │                 │
                    YES│                 │NO
                       ▼                 ▼
              ┌─────────────────┐  ┌──────────┐
              │ Remove old TCS  │  │ Keep all │
              │ data (e.g. 45   │  │ existing │
              │ rows removed)   │  │ data     │
              └────────┬────────┘  └────┬─────┘
                       │                │
                       └────────┬───────┘
                              │
                              ▼
              ┌──────────────────────────────────┐
              │ Combine:                         │
              │ • New TCS data                   │
              │ + Old data from other companies  │
              │ + Preloaded competitors          │
              └────────────┬─────────────────────┘
                           │
                           ▼
              ┌──────────────────────────────────┐
              │  FULL ML PIPELINE EXECUTION      │
              │  (full_pipeline_service.py)      │
              │                                  │
              │  ▪ EDA & data analysis           │
              │  ▪ Sentiment analysis (NLP)      │
              │  ▪ Feature selection             │
              │  ▪ Model training & comparison   │
              │  ▪ Reputation scoring            │
              │  ▪ Forecasting (ARIMA, etc.)     │
              │  ▪ Clustering & dimensionality   │
              │  ▪ Correlation analysis          │
              └────────────┬─────────────────────┘
                           │
                           ▼
              ┌──────────────────────────────────┐
              │  RESULTS GENERATION              │
              │                                  │
              │  • reputation_score: 0.812       │
              │  • best_model: "Gradient..."     │
              │  • sentiment_trend: [...]        │
              │  • forecast: [...]               │
              │  • model_summary: [...]          │
              │  • cluster_insights: {...}       │
              │  • feature_importance: [...]     │
              │  • pca_components: [...]         │
              │  • correlation_matrix: {...}     │
              │  • root_cause_analysis: "..."    │
              └────────────┬─────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌────────────┐   ┌─────────────┐   ┌──────────────┐
    │ Save to    │   │ Return to   │   │ Store in     │
    │ processed_ │   │ /dashboard  │   │ pipeline_    │
    │ dataset.   │   │ /analytics  │   │ state (cache)│
    │ csv        │   │ /strategy   │   │              │
    │            │   │ /graphs     │   │              │
    └────────────┘   └─────────────┘   └──────────────┘
```

---

## Page-Level AI Inference Flow

```
┌────────────────────────────────────────────────────┐
│  USER NAVIGATES TO ANY PAGE (e.g., /dashboard)   │
└──────────────────┬─────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Frontend React      │
        │  PageAIInsights.jsx  │
        │  component mounts    │
        └──────────┬───────────┘
                   │
  ┌────────────────┼───────────────────┐
  │ Check: Is     │                    │
  │ selectedComp  │                    │
  │ any selected? │                    │
  └────┬──────────┴───────┬────────────┘
  NO   │                  │   YES
      │                   ▼
      │         ┌──────────────────────┐
      │         │  Prepare payload:    │
      │         │  • page: "dashboard" │
      │         │  • company: "TCS"    │
      │         │  • context_data: {   │
      │         │    reputation_score..│
      │         │    best_model...     │
      │         │  }                   │
      │         └──────────┬───────────┘
      │                   │
      │                   ▼
      │    ┌──────────────────────────────┐
      │    │  POST /api/ai/page-insights  │
      │    │  (axios request)             │
      │    └──────────┬───────────────────┘
      │               │
      │    ┌──────────▼────────────────────┐
      │    │  BACKEND: ai_routes.py        │
      │    │  page_insights() function     │
      │    └──────────┬────────────────────┘
      │               │
      │    ┌──────────▼────────────────────┐
      │    │  Load dataset                 │
      │    │  Filter for company "TCS"     │
      │    │  Build page-specific prompt   │
      │    └──────────┬────────────────────┘
      │               │
      │    ┌──────────▼────────────────────┐
      │    │  DECIDE: Use AI or Fallback   │
      │    │                               │
      │    │  If AI available:             │
      │    │    ↓ ai_service.generate_text│
      │    │                               │
      │    │  Else:                        │
      │    │    ↓ _get_fallback_insights  │
      │    └──────────┬────────────────────┘
      │               │
      │  ┌────────────┴────────────┐
      │  │                         │
      │  ▼ (AI)                   ▼ (Fallback)
      │ ┌──────────────┐  ┌──────────────────┐
      │ │ Call Ollama  │  │ Use computed     │
      │ │ llama3.1:8b  │  │ statistics &     │
      │ │ @ollama:11434│  │ actual values    │
      │ │              │  │                  │
      │ │ Generate     │  │ Format insights  │
      │ │ smart        │  │ from metrics     │
      │ │ insights     │  │                  │
      │ └──────┬───────┘  └────────┬─────────┘
      │        │                   │
      │        └─────────┬─────────┘
      │                  │
      │       ┌──────────▼──────────┐
      │       │ Parse response:     │
      │       │ Extract insights    │
      │       │ Format as JSON      │
      │       │ [                   │
      │       │  {insight: "...",   │
      │       │   category: "..."}  │
      │       │ ]                   │
      │       └──────────┬──────────┘
      │                  │
      │       ┌──────────▼──────────────┐
      │       │ Return to Frontend      │
      │       │ {insights: [...]}       │
      │       └──────────┬──────────────┘
      │                  │
      │    ┌─────────────▼────────────┐
      │    │ Frontend receives data   │
      │    │ setInsights(response)    │
      │    └──────────┬───────────────┘
      │               │
      └──────┬────────┘
             │
             ▼
   ┌──────────────────────────┐
   │  Render UI:              │
   │                          │
   │  ✨ AI Analysis & Insights
   │  • Insight 1 (CATEGORY)  │
   │  • Insight 2 (CATEGORY)  │
   │  • ...                   │
   │                          │
   │  (Styled & formatted)    │
   └──────────────────────────┘
```

---

## Data Preservation Detail

```
BEFORE UPLOAD:
┌─────────────────────────────────┐
│  processed_dataset.csv          │
├─────────────────────────────────┤
│ Company  | Date  | Text | Score │
├─────────────────────────────────┤
│ Infosys  | 2023  | ... | 0.75   │ ✓ Keep
│ Reliance | 2023  | ... | 0.68   │ ✓ Keep
│ TCS      | 2023  | ... | 0.70   │ ✗ Remove
│ TCS      | 2023  | ... | 0.71   │ ✗ Remove
│ TCS      | 2023  | ... | 0.72   │ ✗ Remove
│ HCL      | 2023  | ... | 0.73   │ ✓ Keep
└─────────────────────────────────┘


UPLOAD NEW TCS DATA:
┌─────────────────────────────────┐
│  New TCS upload (TCS_2024.csv)  │
├─────────────────────────────────┤
│ Company  | Date  | Text | Score │
├─────────────────────────────────┤
│ TCS      | 2024  | ... | 0.81   │ ← New
│ TCS      | 2024  | ... | 0.82   │ ← New
│ TCS      | 2024  | ... | 0.80   │ ← New
└─────────────────────────────────┘


PROCESSING LOGIC:
┌─────────────────┐
│ Old dataset -   │ (Remove TCS records)
│ TCS records     │ 
└────────┬────────┘
         │
         ▼ (Infosys, Reliance, HCL remain)
┌──────────────────┐
│ + Preloaded      │ (Add competitor data)
│   competitors    │
└────────┬─────────┘
         │
         ▼ (Additional companies)
┌────────────────────┐
│ + New TCS data     │ (Add fresh uploads)
└────────┬───────────┘
         │
         ▼
┌──────────────────────────────────┐
│  COMBINED DATASET               │
├──────────────────────────────────┤
│ Company  | Date  | Text | Score  │
├──────────────────────────────────┤
│ TCS      | 2024  | ... | 0.81    │ ▲ New
│ TCS      | 2024  | ... | 0.82    │ ▲ New
│ TCS      | 2024  | ... | 0.80    │ ▲ New
│ Infosys  | 2023  | ... | 0.75    │ ✓ Preserved
│ Reliance | 2023  | ... | 0.68    │ ✓ Preserved
│ HCL      | 2023  | ... | 0.73    │ ✓ Preserved
│ ...preload       | ... | ...     │ ✓ Included
└──────────────────────────────────┘
         │
         ▼
    FULL PIPELINE
         │
         ▼
    NEW RESULTS
```

---

## AI Inference Flowchart (Detailed)

```
PAGE LOADS (e.g., Dashboard)
   │
   ├─ Data available? (reputation_score, etc.)
   │  ├─ YES ✓
   │  │  └─ PageAIInsights mounts
   │  │     │
   │  │     ├─ useEffect triggered
   │  │     │
   │  │     ├─ Check: selectedCompany?
   │  │     │  ├─ NO → return null (no insights)
   │  │     │  │
   │  │     │  └─ YES ✓
   │  │     │     │
   │  │     │     ├─ POST /ai/page-insights
   │  │     │     │
   │  │     │     ├─ BACKEND ENDPOINT
   │  │     │     │  ├─ Load dataset
   │  │     │     │  ├─ Filter by company
   │  │     │     │  ├─ Build prompt
   │  │     │     │  │
   │  │     │     │  ├─ TRY: AI call
   │  │     │     │  │  ├─ ai_service.generate_text()
   │  │     │     │  │  │  ├─ Check AI provider status
   │  │     │     │  │  │  │
   │  │     │     │  │  │  ├─ Provider = Ollama?
   │  │     │     │  │  │  │  ├─ YES: Connect to http://localhost:11434
   │  │     │     │  │  │  │  │  └─ Run llama3.1:8b
   │  │     │     │  │  │  │  │
   │  │     │     │  │  │  │  └─ NO: Return fallback
   │  │     │     │  │  │  │
   │  │     │     │  │  │  ├─ Parse response
   │  │     │     │  │  │  └─ Return text
   │  │     │     │  │
   │  │     │     │  ├─ CATCH: If AI fails
   │  │     │     │  │  └─ Generate fallback insights
   │  │     │     │  │
   │  │     │     │  ├─ Parse insights
   │  │     │     │  │  ├─ Look for [CATEGORY]: text
   │  │     │     │  │  ├─ Or bullet points
   │  │     │     │  │  └─ Or sentences
   │  │     │     │  │
   │  │     │     │  └─ Return {insights: [...]}
   │  │     │     │
   │  │     │     └─ FRONTEND receives response
   │  │     │        ├─ setInsights(data)
   │  │     │        │
   │  │     │        ├─ Render component
   │  │     │        │  ├─ Check page type
   │  │     │        │  ├─ Apply styling
   │  │     │        │  └─ Display insights
   │  │     │        │
   │  │     │        └─ USER SEES
   │  │     │           Dashboard + AI insights ✓
   │  │     │
   │  │     └─ Re-run when: page, company, or data changes
   │  │
   │  └─ NO
   │     └─ PageAIInsights returns null
   │
   └─ Page renders without insights (data loading)
```

---

## API Response Structure

```
PAGE REQUEST:
POST /api/ai/page-insights
{
  "page": "dashboard",
  "company": "TCS",
  "context_data": {
    "reputation_score": 0.812,
    "best_model": "Gradient Boosting",
    "sentiment_trend": [0.65, 0.68, 0.72, 0.75],
    "forecast": [0.76, 0.77, 0.78],
    "model_summary": [
      {"model": "Linear Regression", "rmse": 0.15, "mae": 0.12, "r2": 0.82},
      {"model": "Gradient Boosting", "rmse": 0.12, "mae": 0.10, "r2": 0.88}
    ]
  }
}

SERVER RESPONSE:
200 OK
{
  "insights": [
    {
      "insight": "Reputation score 0.812 indicates strong market position",
      "category": "KPI"
    },
    {
      "insight": "Gradient Boosting outperforms with 0.88 R² accuracy",
      "category": "MODEL"
    },
    {
      "insight": "Sentiment shows upward trend from 0.65 to 0.75",
      "category": "TREND"
    },
    {
      "insight": "Forecast predicts continued improvement over next period",
      "category": "OUTLOOK"
    },
    {
      "insight": "Focus on maintaining positive sentiment momentum",
      "category": "ACTION"
    }
  ]
}

FRONTEND RENDERS:
✨ AI Analysis & Insights
• Reputation score 0.812 indicates strong market position (KPI)
• Gradient Boosting outperforms with 0.88 R² accuracy (MODEL)
• Sentiment shows upward trend from 0.65 to 0.75 (TREND)
• Forecast predicts continued improvement over next period (OUTLOOK)
• Focus on maintaining positive sentiment momentum (ACTION)
```

---

## Strategy Page Variant

```
SPECIAL FORMAT FOR STRATEGY PAGE:

API returns insights with "action" field:

{
  "insights": [
    {
      "insight": "Current score 0.812 suggests strong position",
      "category": "STRATEGIC PRIORITY",
      "action": "Review competitive positioning strategy"
    },
    {
      "insight": "12% improvement potential identified",
      "category": "QUICK WIN",
      "action": "Focus on high-impact initiatives"
    },
    {
      "insight": "Sentiment risk in Q3 requires attention",
      "category": "RISK ALERT",
      "action": "Prepare mitigation strategy"
    }
  ]
}

FRONTEND RENDERS (Strategy variants):

🤖 Overall AI Analytics & Strategy
┌─────────────────────────────────────────────────────┐
│ [STRATEGIC PRIORITY]                                │
│ Current score 0.812 suggests strong position        │
│ → Review competitive positioning strategy           │
├─────────────────────────────────────────────────────┤
│ [QUICK WIN]                                         │
│ 12% improvement potential identified                │
│ → Focus on high-impact initiatives                  │
├─────────────────────────────────────────────────────┤
│ [RISK ALERT]                                        │
│ Sentiment risk in Q3 requires attention             │
│ → Prepare mitigation strategy                       │
└─────────────────────────────────────────────────────┘
```

---

## Summary: How Everything Works Together

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPLETE USER JOURNEY                         │
└─────────────────────────────────────────────────────────────────┘

1. USER UPLOADS DATA
   ↓
   Company detected as "TCS"
   Old TCS data removed, new data added
   Preloaded competitors preserved
   ↓

2. FULL PIPELINE RUNS
   ↓
   ML models, sentiment, forecast, clustering, correlation
   Results cached in pipeline_state
   ↓

3. USER NAVIGATES TO PAGE (e.g., Dashboard)
   ↓
   Page displays: Reputation score, charts, metrics
   ↓

4. AI INFERENCE TRIGGERED
   ↓
   Frontend sends request to /ai/page-insights
   Backend generates page-specific insights using Ollama
   Or falls back to data-driven insights if Ollama offline
   ↓

5. INSIGHTS DISPLAY
   ✨ AI Analysis & Insights
   • 4-5 relevant bullets at page bottom
   ↓

6. USER SEES EVERYTHING
   ALL DATA + AI INTERPRETATION ON EVERY PAGE ✓

7. USER RE-UPLOADS TCS
   ↓
   Old TCS removed, new TCS added
   Message: "Updated: removed X records"
   Pipeline reruns with fresh data
   ↓

8. ALL PAGES UPDATE
   New metrics, new AI insights
   ↓
   Complete analysis cycle ✓
```

---

This is your **complete system in action** with all components working together!

