# ValorEdge AI - Complete Workflow Guide

## System Architecture

### Data Flow
```
User Uploads CSV
    ↓
[Pipeline identifies company name → "TCS"]
    ↓
[Check if TCS exists in previous data]
    ├─ YES: Remove old TCS data, keep preloaded competitors
    └─ NO: Add as new company
    ↓
[Combine cleaned data with preloaded dataset]
    ↓
[Run full ML pipeline]
    ↓
[Generate results: reputation score, models, sentiment, etc.]
    ↓
[Make results available across all pages]
```

---

## 1. Upload Workflow

### What Happens When You Upload

**Scenario A: First time uploading TCS data**
```
1. Select CSV file (e.g., "TCS_monthly.csv")
2. System identifies company as "TCS"
3. TCS is added to the analysis
4. Message: "New company added to dataset"
5. All pages now show TCS vs competitors
```

**Scenario B: Re-uploading TCS with new data**
```
1. Select updated TCS CSV file
2. System identifies company as "TCS"
3. Backend loads previous data:
   - Removes old TCS records (e.g., 45 rows removed)
   - Keeps preloaded competitor data intact
   - Adds new TCS records
4. Message: "Updated: removed 45 old records, added new ones"
5. All pages now use fresh TCS data + competitors
```

### Company Detection (in order)
1. **Form input**: `my_company` parameter
2. **CSV column**: company name from "company" column
3. **Filename**: detected from filename (e.g., "TCS_2023.csv" → "TCS 2023")
4. **Fallback**: "My Company"

---

## 2. Preloaded Data Handling

### File Structure
```
backend/data/
├── preloaded_competitors.csv     ← Competitor data (always included)
├── processed_dataset.csv         ← Historical data (for preservation)
└── latest_results.json           ← Last pipeline results
```

### Data Preservation Logic
```python
1. Read preloaded_competitors.csv
2. Load processed_dataset.csv (if exists)
3. Remove records for newly uploaded company
4. Keep all other company records
5. Combine: new_data + preloaded + other_companies
6. Run pipeline on combined dataset
7. Store in processed_dataset.csv
```

---

## 3. AI Inference at Page Bottom (Using Ollama)

### Current Configuration
```env
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

### How It Works On Each Page

#### Dashboard Page
**Result shown**: Reputation score, sentiment trends, forecast
**AI Inference at bottom**:
- Interprets the KPI score
- Compares to competitors
- Assesses model reliability
- Suggests focus areas

Example output:
```
✨ AI Analysis & Insights
• Current reputation score is 0.765 (SCORE)
• Best performing model is Linear Regression (MODEL)
• Ranked #2 out of 5 companies (RANK)
• Forecast shows stable upward trend (TREND)
```

#### Upload Page
**Result shown**: Rows processed, model selected, company name
**AI Inference at bottom**:
- Data quality assessment
- Coverage analysis
- Next recommended steps

Example output:
```
✨ AI Analysis & Insights
• Successfully processed 120 data rows (PROCESSED)
• Pipeline selected Random Forest as best model (MODEL)
• TCS company data is now ready for analysis (STATUS)
• Visit Dashboard to see KPI metrics (NEXT)
```

#### Graphs Page
**Result shown**: All visualizations (sentiment, forecast, models, features, PCA)
**AI Inference at bottom**:
- Trend interpretation
- Peer comparison gaps
- Visual pattern analysis

#### Analytics Page
**Result shown**: Root-cause analysis, clusters, correlations, PCA
**AI Inference at bottom**:
- Feature driver explanation
- Cluster insights
- Why differences exist vs competitors

#### Strategy/Simulation Page
**Result shown**: Current/projected scores, recommendations, what-if results
**AI Inference at bottom** (Special format):
```
🤖 Overall AI Analytics & Strategy
• Current reputation score: 0.765 (STRATEGIC PRIORITY)
• Potential improvement available: 12% (QUICK WIN)
→ Review and implement: Focus on customer service
• What-if scenarios help test strategic options (ACTION)
→ Review and implement: Test sentiment investment
```

---

## 4. Inference Fallback System

### If Ollama is Offline
The system automatically shows **data-driven insights** based on actual metrics:
- Uses computed statistics
- Extracts real values from results
- Still provides actionable information
- No error messages shown to user

### Inference Priority
1. **Try Ollama AI** → Generate smart insights
2. **If Ollama fails** → Show data-driven fallback
3. **Always return insights** → Never show errors

---

## 5. Complete Example Workflow

### Step 1: Initial Setup
```
Preloaded data: Reliance, Infosys, HCL (3 companies)
```

### Step 2: Upload TCS Data
```
Upload file: TCS_Q1_2024.csv
- 150 records with date, text columns
- Backend extracts company name: "TCS"
- Combines with preloaded data: TCS + 3 competitors = 4 companies
- Pipeline runs on all 4 datasets
- Results: reputation, models, sentiment, forecast, clusters, etc.
```

### Step 3: View Dashboard
```
Shows:
- TCS reputation score: 0.812
- Best model: Gradient Boosting
- Sentiment trend: 45 points
- Forecast: 20 upcoming values
- Forecast chart visualization

AI Inference (from Ollama):
✨ AI Analysis & Insights
• Reputation score 0.812 suggests strong market position (KPI)
• Gradient Boosting outperforms competitors with 0.92 R² (MODEL)
• Ranked #1 out of 4 companies by reputation (RANK)
• Positive sentiment trend indicates growing trust (TREND)
```

### Step 4: Upload Updated TCS Data
```
Upload file: TCS_Q2_2024.csv
- 160 new records
- Backend finds TCS already exists
- Removes 150 old TCS records
- Adds 160 new TCS records
- Preserves Reliance, Infosys, HCL data
- Pipeline re-runs on updated dataset

UI shows: "Updated: removed 150 old records, added new ones"
```

### Step 5: View Updated Results
```
All pages now show:
- Updated TCS metrics from Q2
- Competitors unchanged
- New AI inference reflecting latest data
```

---

## 6. Technical Stack

### Frontend Pages
- `/dashboard` → Reputation, sentiment, forecast, models
- `/upload` → Data ingestion, company detection
- `/graphs` → Unified visualization workspace
- `/ai-analytics` → Root-cause analysis, clusters, PCA
- `/strategy` → What-if scenarios, recommendations

### Backend Services
- **Upload Pipeline**: `pipeline_routes.py` → Company detection, data merge, preservation
- **AI Routes**: `ai_routes.py` → `/ai/page-insights` endpoint
- **AI Service**: `ai_advice_service.py` → Ollama integration
- **Full Pipeline**: `full_pipeline_service.py` → ML analysis

### AI Integration
- **Provider**: Ollama (local LLM)
- **Model**: llama3.1:8b (or llama3.2:3b fallback)
- **Endpoint**: http://127.0.0.1:11434
- **Fallback**: Data-driven insights when offline

---

## 7. API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload` | POST | Upload CSV, auto-detect company, preserve data |
| `/dashboard` | GET | KPI metrics, sentiment, forecast, models |
| `/analytics` | GET | Root-cause analysis, clusters, PCA, correlation |
| `/strategy` | GET | What-if analysis, recommendations, risk alerts |
| `/ai/page-insights` | POST | Generate page-specific AI inference |

---

## 8. Troubleshooting

### AI Inference Not Showing
**Check**:
1. Is Ollama running? → `http://127.0.0.1:11434/api/tags`
2. Model available? → Run `ollama pull llama3.1:8b`
3. Backend sees Ollama? → Check `/api/ai/status`

**Auto-fallback**: If Ollama unavailable, data-driven insights still show

### Company Not Detected Correctly
**Check**:
1. File named properly: `TCS_data.csv` (uses filename if no company column)
2. CSV has company column with values
3. Or specify via form parameter

### Data Not Being Preserved
**Check**:
1. Check `processed_dataset.csv` exists
2. Backend logs should show "Removed X existing rows for company 'TCS'"
3. Verify preloaded data still intact after upload

---

## 9. Key Features ✓

✅ **Smart Company Detection**
- Auto-detects from filename, csv column, or form input

✅ **Intelligent Data Preservation**
- Removes old data for selected company
- Preserves all other company data
- Keeps preload competitors intact

✅ **Ollama AI Integration**
- Page-specific inference at bottom
- Smart fallback if offline
- No errors shown to users

✅ **Complete Analysis Stack**
- Dashboard: KPIs & trends
- Analytics: Root causes & patterns
- Strategy: What-if scenarios
- Graphs: Unified visualization
- Upload: Data ingestion & feedback

✅ **Competitor Comparison**
- Automatic peer benchmarking
- Relative performance metrics
- Competitive positioning insights

---

## 10. Next Steps

1. **Ensure Ollama is running**:
   ```bash
   ollama serve
   ```

2. **Download model**:
   ```bash
   ollama pull llama3.1:8b
   ```

3. **Start backend**:
   ```bash
   cd backend
   python -m uvicorn api.main:app --reload
   ```

4. **Start frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

5. **Test workflow**:
   - Go to Upload page
   - Select TCS CSV
   - See company detected as "TCS"
   - View Dashboard → See AI inference at bottom
   - Re-upload TCS → See "Updated: removed X records"
   - All pages show AI insights → Powered by Ollama ✓

