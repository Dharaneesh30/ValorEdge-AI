# ValorEdge AI

End-to-end corporate reputation intelligence platform.

Upload a text dataset and the system runs a full pipeline:
- preprocessing + sentiment analysis
- EDA + dimensionality reduction
- clustering + model comparison
- 30-day forecasting
- strategy insights (GenAI + local fallbacks)
- one-company-vs-peers benchmarking

## Tech Stack
- Backend: FastAPI, pandas, scikit-learn, statsmodels, VADER
- Frontend: React + Vite + Tailwind + Recharts
- AI providers: Ollama, Gemini, Hugging Face (configurable)

## Core Features
- Single-click full pipeline from CSV upload
- Dashboard (`/dashboard`): KPI, forecast, model summary
- AI Analytics (`/ai-analytics`): root-cause, clusters, feature importance, PCA, correlation
- Graph Workspace (`/graphs`): all major charts in one page
- Strategy Studio (`/strategy`): recommendations + simulation + GenAI insight panel
- Company Benchmark (`/company-benchmark`): compare one company against all peers and generate improvement actions

## Dataset Requirements
Required columns:
- `date`
- `text`

Optional columns:
- `company`
- `category`

## Project Structure
```text
ValorEdge-AI/
  backend/
    api/routes/                 # FastAPI routes
    services/                   # business logic / orchestration
    analytics/                  # EDA / clustering / reduction
    forecasting/                # ARIMA forecasting
    nlp/                        # sentiment engine
    models/                     # model comparison
    data/                       # generated artifacts
    uploads/                    # uploaded CSV files
  frontend/
    src/components/             # reusable UI components
    src/pages/                  # Upload, Dashboard, Analytics, Graphs, Strategy
```

## API Endpoints
Pipeline + views:
- `POST /upload`
- `GET /dashboard`
- `GET /analytics`
- `GET /strategy`
- `GET /genai-insights`

Artifacts:
- `GET /eda`
- `GET /sentiment`
- `GET /pca`
- `GET /clusters`
- `GET /models`
- `GET /forecast`
- `POST /clusters/assign`

Competitive benchmarking:
- `GET /companies`
- `GET /company-benchmark?company=<name>`

Simulation:
- `POST /scenario-simulate`

AI utilities:
- `GET /api/ai/status`
- `POST /api/ai/ask`

## Setup

### 1) Backend

PowerShell:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Bash:
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend default API base URL:
- `http://127.0.0.1:8000`

Override with:
- `frontend/.env` -> `VITE_API_BASE_URL=http://<host>:<port>`

## Environment Configuration (Backend)

Copy and edit:
```bash
cp backend/.env.example backend/.env
```

### AI Provider Selection
```env
AI_PROVIDER=ollama
```

Supported values:
- `ollama`
- `gemini`
- `huggingface`

### Ollama (recommended local setup)
```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_FALLBACK_MODEL=llama3.1:8b
OLLAMA_TIMEOUT_SECONDS=180
```

Then:
```bash
ollama pull llama3.2:3b
```

### Gemini
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.0-flash
GEMINI_FALLBACK_MODEL=gemini-2.0-flash-lite
```

### Hugging Face
```env
AI_PROVIDER=huggingface
HF_API_TOKEN=your_token
HF_MODEL=google/flan-t5-large
HF_API_BASE=https://api-inference.huggingface.co/models
```

## Typical Workflow
1. Open `/upload`
2. Upload CSV and run full pipeline
3. Explore:
   - `/dashboard`
   - `/ai-analytics`
   - `/graphs`
   - `/strategy`
4. Use **One Company vs Others** panel to benchmark and generate competitive actions

## Troubleshooting

### `No strategy data available. Upload dataset first.`
Upload dataset via `POST /upload` first.

### Ollama 404 / model not found
- Ensure Ollama server is running
- Pull selected model:
  - `ollama pull llama3.2:3b`
- Verify `OLLAMA_BASE_URL` and `OLLAMA_MODEL`

### Ollama timeout
- Increase `OLLAMA_TIMEOUT_SECONDS`
- Use a lighter model (`llama3.2:3b`)

### Gemini quota exceeded (429)
- Enable billing or switch provider
- Use Ollama for local/offline flow

## Notes
- `backend/data/` and `backend/uploads/` contain generated runtime artifacts.
- Keep secrets only in local `.env` files.
