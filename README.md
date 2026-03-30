# ValorEdge AI - Corporate Reputation Analytics and Forecasting Platform

## Problem Statement
Enterprises receive large volumes of unstructured text from news, social media, customer feedback, and analyst commentary. Turning this into a measurable and forecastable reputation signal is difficult without a unified AI pipeline.

## Objective
Build a full end-to-end platform that automatically:
- ingests uploaded text datasets,
- computes sentiment and reputation intelligence,
- performs EDA and dimensionality reduction,
- clusters discussion patterns,
- compares predictive models,
- forecasts future reputation trend,
- and generates GenAI business insights.

## Dataset Format
Required CSV columns:
- `date` (mandatory)
- `text` (mandatory)

Optional columns:
- `company`
- `category`

## Methods Used
### NLP
- VADER sentiment analysis (`sentiment_score` in range `-1` to `+1`)
- Text cleaning: lowercase, punctuation removal, stopword removal

### Feature Extraction
- TF-IDF vectorization (`max_features=400`, 1-2 grams)
- Hybrid feature matrix: TF-IDF + optional numeric columns

### EDA
- Sentiment distribution histogram
- Time-series sentiment trend plot
- Word-frequency bar chart
- Saved in `backend/data/plots/`

### Dimensionality Reduction
- PCA (2 components)
- Factor Analysis (2 components)

### Clustering
- KMeans clustering
- Hierarchical clustering (Agglomerative)
- Cluster interpretation via top TF-IDF keywords
- New text cluster assignment endpoint included

### Predictive Models
- Linear Regression
- Random Forest Regressor
- Evaluation metrics:
  - MSE
  - RMSE
  - MAE
  - R^2 score
- Best model selected by lowest RMSE
- Random Forest feature importance returned for dashboard

### Forecasting
- ADF stationarity test
- ARIMA(1,1,1) sentiment forecast for next 30 days
- Naive fallback for very small datasets

### Reputation Score Engine
Composite score formula combining:
- Sentiment component (55%)
- Trend component (25%)
- Cluster-weighted component (20%)

### GenAI Insights
- Uses existing `AIAdviceService` provider stack (Gemini/HuggingFace/Ollama fallback logic)
- Produces:
  - current reputation explanation,
  - future outlook,
  - business impact,
  - actionable recommendations.

## Architecture (Text Diagram)
1. Frontend uploads CSV -> `POST /upload`
2. Backend pipeline orchestrator runs all steps automatically:
   - preprocessing -> sentiment -> TF-IDF -> PCA/FA -> clustering -> models -> forecast -> reputation score -> GenAI insights
3. Results are stored in memory (`pipeline_state`) and persisted to `backend/data/latest_results.json`
4. Decision UI flow:
   - Dashboard (`WHAT`) -> `/dashboard`
   - AI Analytics (`WHY`) -> `/analytics`
   - Strategy (`WHAT TO DO`) -> `/strategy`

## API Endpoints
- `POST /upload`
- `GET /eda`
- `GET /sentiment`
- `GET /pca`
- `GET /clusters`
- `POST /clusters/assign`
- `GET /models`
- `GET /forecast`
- `GET /genai-insights`
- `GET /dashboard`
- `GET /analytics`
- `GET /strategy`
- `GET /companies`
- `GET /company-benchmark?company=<name>`
- `POST /scenario-simulate`

## Storage
- Uploaded files: `backend/uploads/`
- Processed data and artifacts: `backend/data/`
- Plot images: `backend/data/plots/`

## How to Run
### 1. Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend defaults to backend URL `http://127.0.0.1:8000`.

## Resume-Worthy Highlights
- Fully automated pipeline triggered immediately after upload
- Modular backend architecture (services, analytics, models, forecasting, nlp)
- End-to-end model comparison with MSE, RMSE, MAE, and R^2
- Random Forest feature importance in dashboard
- One-vs-many company benchmarking with AI improvement recommendations
- Strategy simulator combining text sentiment, clustering, forecast context, and GenAI advice
- GenAI-generated strategy summary integrated into workflow

## Future Scope
- Add streaming ingestion for near real-time reputation monitoring
- Add topic modeling and named-entity trend tracking
- Add Prophet/LSTM ensemble forecasting
- Add experiment tracking (MLflow) and model registry
- Add role-based access and multi-tenant company workspaces
