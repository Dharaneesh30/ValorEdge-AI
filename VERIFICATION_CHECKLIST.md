# ValorEdge AI System - Verification Checklist

## Pre-Launch Checklist

### ✅ Backend Configuration
- [ ] `.env` has `AI_PROVIDER=ollama`
- [ ] `.env` has `OLLAMA_MODEL=llama3.1:8b`
- [ ] `.env` has `OLLAMA_BASE_URL=http://127.0.0.1:11434`
- [ ] `/backend/data/preloaded_competitors.csv` exists
- [ ] `/backend/uploads` directory exists or will be auto-created
- [ ] `/backend/data/processed_dataset.csv` exists (or will be created on first upload)

### ✅ Frontend Setup
- [ ] `/frontend/src/components/PageAIInsights.jsx` exists
- [ ] All pages import PageAIInsights:
  - [ ] Dashboard.jsx
  - [ ] UploadPage.jsx
  - [ ] GraphsPage.jsx
  - [ ] AIAnalyticsPage.jsx
  - [ ] SimulationPage.jsx
- [ ] API base URL configured: `http://127.0.0.1:8000`

### ✅ AI Integration
- [ ] Ollama service running: `ollama serve`
- [ ] Model downloaded: `ollama list` shows `llama3.1:8b`
- [ ] Ollama accessible: `curl http://127.0.0.1:11434/api/tags`

### ✅ API Endpoints
- [ ] `POST /upload` → Handles company detection & data preservation
- [ ] `GET /dashboard` → Returns reputation, sentiment, forecast, models
- [ ] `GET /analytics` → Returns root-cause, clusters, PCA, correlation
- [ ] `GET /strategy` → Returns recommendations, what-if analysis
- [ ] `POST /ai/page-insights` → AI inference endpoint

---

## Quick Test Guide

### Test 1: Upload New Company
```
1. Go to /upload page
2. Select a CSV file (e.g., TCS_2024.csv)
3. Click "Upload"
4. Expected result:
   ✓ Company name auto-detected as "TCS"
   ✓ Message shows "New company added to dataset"
   ✓ Pipeline completes successfully
   ✓ Best model is selected
```

### Test 2: View Dashboard with AI
```
1. Go to /dashboard
2. Select "TCS" from company dropdown
3. Expected result:
   ✓ Reputation score displays
   ✓ Sentiment trend chart shows
   ✓ Forecast chart shows
   ✓ Model comparison shows
   ✓ 📊 AI Analysis & Insights appears at bottom
   ✓ Shows 4-5 bullet points with insights
```

### Test 3: View Other Pages with AI
```
1. Visit each page: /upload, /graphs, /ai-analytics, /strategy
2. Select "TCS" company
3. Expected result:
   ✓ Each page shows relevant data
   ✓ AI insights appear at page bottom
   ✓ Insights are page-specific and relevant
```

### Test 4: Re-upload Same Company
```
1. Prepare updated TCS CSV with different data
2. Upload again
3. Expected result:
   ✓ Message shows "Updated: removed X old records"
   ✓ New data replaces old TCS data
   ✓ Other companies' data unchanged
   ✓ Dashboard shows updated metrics
   ✓ AI insights reflect new data
```

### Test 5: Verify Data Preservation
```
1. Upload Company A (100 records)
2. View Dashboard → See Company A metrics
3. Upload Company A again (50 new records)
4. Expected result:
   ✓ Old Company A data removed
   ✓ New Company A data added
   ✓ Preloaded companies still present
   ✓ Competitor comparisons work correctly
```

### Test 6: Ollama Fallback
```
1. Stop Ollama service
2. Upload data and navigate to a page
3. Expected result:
   ✓ No error shown
   ✓ Data-driven insights still appear
   ✓ System gracefully falls back
4. Restart Ollama
5. Expected result:
   ✓ Smart AI insights return
```

---

## Startup Commands

### Terminal 1: Ollama (Required for AI)
```bash
ollama serve
# Wait for "Listening on 127.0.0.1:11434"
# Then in another terminal:
ollama pull llama3.1:8b
```

### Terminal 2: Backend
```bash
cd d:\College\College\ Study\ materials\ValorEdge-AI\backend
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
# Wait for "Uvicorn running on http://127.0.0.1:8000"
```

### Terminal 3: Frontend
```bash
cd d:\College\College\ Study\ materials\ValorEdge-AI\frontend
npm run dev
# Wait for "Local: http://localhost:5173" or similar
```

### Access the App
- Open browser: `http://localhost:5173`
- Upload → Dashboard → See AI insights at bottom ✓

---

## System Components Status

### Pages with AI Insights ✓
```
✅ Dashboard       → KPI + AI interpretation
✅ Upload        → Data quality + AI observations
✅ Graphs        → Visualization + AI patterns
✅ Analytics     → Root-cause + AI explanation
✅ Strategy      → Recommendations + AI strategy
```

### Data Handling ✓
```
✅ Company detection    → Auto from filename/CSV/form
✅ Data preservation    → Remove old, keep others, add new
✅ Preload integration  → Always includes competitors
✅ Pipeline execution   → Full ML analysis on combined data
```

### AI Integration ✓
```
✅ Ollama configured    → llama3.1:8b ready
✅ Endpoint created     → /ai/page-insights
✅ Fallback system      → Data-driven if offline
✅ All pages with AI    → Every page shows insights
```

---

## Logs to Check

### Backend Logs
```
Look for:
- "Upload pipeline failed: X" → Check input data
- "Removed X existing rows for company 'TCS'" → Data preservation working
- "AI provider: ollama-local" → Ollama detected
- "Failed to generate insights" → Check Ollama connection
```

### Frontend Console (Browser F12)
```
Look for:
- Errors in Network tab → Check API connectivity
- Errors in Console tab → Check component issues
- 200 responses for /ai/page-insights → API working
```

### Ollama Status
```
curl http://127.0.0.1:11434/api/tags
# Should show: llama3.1:8b in response
```

---

## Common Issues & Fixes

| Issue | Check | Fix |
|-------|-------|-----|
| AI insights not showing | Is Ollama running? | `ollama serve` |
| Company not auto-detected | CSV filename or column | Add "company" column to CSV |
| Old data not removed | Check backend logs | Verify processed_dataset.csv exists |
| 500 error on upload | Check backend logs | Ensure preloaded_competitors.csv exists |
| API not responding | Check backend running | `python -m uvicorn api.main:app --reload` |
| Insights show "Data loaded" | Ollama timing out | Increase OLLAMA_TIMEOUT_SECONDS in .env |

---

## Success Criteria ✓

You'll know everything is working when:

1. ✅ **Upload page**: File uploaded, company detected, "New company added" message
2. ✅ **Dashboard page**: Reputation score + sentiment + forecast visible + AI insights at bottom
3. ✅ **Graphs page**: All charts display + AI pattern analysis at bottom
4. ✅ **Analytics page**: Root-cause analysis + clusters + AI insights at bottom
5. ✅ **Strategy page**: What-if scenarios + AI recommendations at bottom with action items
6. ✅ **Re-upload test**: Upload same company → "Updated: removed X records" message
7. ✅ **Data integrity**: Other companies' data preserved when you re-upload
8. ✅ **AI quality**: Insights are relevant to page content and actual data

---

## Files Modified ✓

```
✅ backend/api/routes/pipeline_routes.py    → Data preservation logic
✅ backend/api/routes/ai_routes.py          → Page-insights endpoint
✅ frontend/src/components/PageAIInsights.jsx → AI display component
✅ frontend/src/pages/Dashboard.jsx         → Integrated PageAIInsights
✅ frontend/src/pages/UploadPage.jsx        → Integrated PageAIInsights
✅ frontend/src/pages/GraphsPage.jsx        → Integrated PageAIInsights
✅ frontend/src/pages/AIAnalyticsPage.jsx   → Integrated PageAIInsights
✅ frontend/src/pages/SimulationPage.jsx    → Integrated PageAIInsights
✅ .env                                      → Ollama configuration
```

---

## Support

For any issues:
1. Check logs in backend terminal
2. Verify Ollama is running: `curl http://127.0.0.1:11434/api/tags`
3. Check browser console (F12)
4. Verify API is accessible: `curl http://127.0.0.1:8000/`
5. Check that CSV has required columns: "date" and "text"

