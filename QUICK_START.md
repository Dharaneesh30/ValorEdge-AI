# Quick Start Guide - ValorEdge AI

## 🚀 Get Running in 5 Minutes

### Step 1: Ensure Ollama is Running (90 seconds)
```powershell
# Terminal 1: Start Ollama
ollama serve

# You should see: "Listening on 127.0.0.1:11434"

# Check model is available:
ollama list
# Should show: llama3.1:8b

# If not installed:
ollama pull llama3.1:8b
```

### Step 2: Start Backend (60 seconds)
```powershell
# Terminal 2: Navigate and start
cd d:\College\College\ Study\ materials\ValorEdge-AI\backend

# Start server
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# Wait for: "Uvicorn running on http://127.0.0.1:8000"
```

### Step 3: Start Frontend (60 seconds)
```bash
# Terminal 3: Navigate and start
cd d:\College\College\ Study\ materials\ValorEdge-AI\frontend

npm run dev

# Wait for: "Local: http://localhost:5173" or similar
```

### Step 4: Open App (30 seconds)
```
Browser: http://localhost:5173
```

---

## 🧪 Test It Works

### Test 1: Upload TCS Data (2 minutes)
```
1. Click "Upload and Compare" tab
2. Select your CSV file (should have "date" and "text" columns)
3. System auto-detects company name
4. Click "Upload"
5. Wait for message: "Pipeline completed"
6. Result: "New company added to dataset" OR "Updated: removed X records"
```

### Test 2: View Dashboard (1 minute)
```
1. Select "TCS" from dropdown (or your company)
2. Go to "Competitive Performance Dashboard"
3. Scroll down to BOTTOM of page
4. Look for: ✨ AI Analysis & Insights
5. Should see 4-5 bullet points with analysis
```

### Test 3: Check All Pages Have AI (2 minutes)
```
1. Dashboard        → Scroll to bottom → See AI
2. Upload          → Upload file      → See AI
3. Graphs          → Select company   → Scroll down → See AI
4. AI Analytics    → Select company   → Scroll down → See AI  
5. Strategy        → Select company   → Scroll down → See AI with actions
```

### Test 4: Re-upload (2 minutes)
```
1. Go to Upload page
2. Upload updated version of same company
3. Should say: "Updated: removed X old records, added new ones"
4. Dashboard shows new metrics
5. AI insights reflect new data
```

---

## ✅ Success Checklist

- [ ] Ollama running (see http://127.0.0.1:11434/api/tags)
- [ ] Backend running (see http://127.0.0.1:8000/)
- [ ] Frontend running (see http://localhost:5173)
- [ ] Can upload CSV file
- [ ] Can select company from dropdown
- [ ] Dashboard shows reputation score + charts
- [ ] **See "✨ AI Analysis & Insights" at bottom of Dashboard**
- [ ] See different AI insights on each page
- [ ] Re-upload shows "Updated: removed X records"
- [ ] Other companies' data preserved after re-upload

If all checkmarks pass → **You're ready to go! 🎉**

---

## 🔧 Troubleshooting Quick Fixes

### AI Insights Not Showing
**Check 1:** Is Ollama running?
```powershell
curl http://127.0.0.1:11434/api/tags
# Should return JSON with model info
```

**Fix:**
```powershell
ollama serve
```

**Check 2:** Backend logs
```
Look for: "AI provider: ollama-local"
```

**Check 3:** Company selected?
```
Go to Upload, select company,
then go to Dashboard and select same company
```

### Upload Fails
**Check:** File has "date" and "text" columns
```
CSV format: date,text,company (optional)
2024-01-15,Some text,"TCS"
2024-01-16,Other text,"TCS"
```

**Check:** Backend is running
```
Terminal: python -m uvicorn api.main:app --reload
```

### Old Data Not Removed on Re-upload
**Check:** Backend logs show:
```
"Removed X existing rows for company 'TCS'"
```

If not present:
1. Stop backend
2. Delete `backend/data/processed_dataset.csv`
3. Restart backend
4. Re-upload

---

## 📊 What Each Page Shows

| Page | Purpose | AI Insight |
|------|---------|-----------|
| **Upload** | Upload CSV, select company | Data quality assessment |
| **Dashboard** | Reputation KPI, sentiment, forecast | KPI interpretation |
| **Graphs** | All visualizations | Trend interpretation |
| **AI Analytics** | Root-cause analysis | Why differences exist |
| **Strategy** | What-if scenarios | Strategic recommendations |

---

## 🎯 Typical Workflow

```
1. Have CSV file ready
   - Columns: date,text,company (optional)
   - Example: TCS_data.csv

2. Upload page
   - Select file
   - System detects company (from filename or CSV column)
   - Click Upload
   - Wait 30-60 seconds

3. View Results
   - Go to Dashboard
   - Select company from dropdown
   - See reputation score + charts + AI insights
   - Go to other pages to explore

4. Re-upload Updated Data
   - Same process
   - Old data auto-removed
   - New data added
   - All pages update

5. Analyze with AI
   - Every page has insights at bottom
   - Run what-if scenarios on Strategy page
   - Compare with competitors automatically
```

---

## 📁 Important Files

```
Your work:
- backend/.env              ← Ollama config (already set)
- backend/data/             ← Data storage
- frontend/src/pages/       ← App pages
- frontend/src/components/  ← UI components

Key endpoints:
- http://127.0.0.1:8000        (Backend)
- http://127.0.0.1:11434       (Ollama)
- http://localhost:5173        (Frontend)
```

---

## 🚨 If Something Goes Wrong

**Step 1:** Kill all terminals
```
Ctrl+C in each terminal
```

**Step 2:** Clean start
```powershell
# Terminal 1
ollama serve

# Terminal 2 (backend directory)
python -m uvicorn api.main:app --reload

# Terminal 3 (frontend directory)
npm run dev
```

**Step 3:** Test
```
Browser: http://localhost:5173
Upload page: Try uploading a file
```

**Step 4:** If still stuck, check logs
```
Backend logs: Show error messages
Frontend console (F12): Show errors
Ollama: http://127.0.0.1:11434/api/tags
```

---

## 🎓 Key Concepts

### Company Detection
- System auto-detects from: filename, CSV column, or form input
- Example: "TCS_2024.csv" → company = "TCS"

### Data Preservation
- Upload new TCS → Old TCS removed, new TCS added
- Other companies' data stays intact
- Preloaded competitors always included

### AI Insights
- Generated using Ollama (local LLM)
- Page-specific (different for each page)
- Falls back to data-driven insights if Ollama offline
- No errors shown (graceful degradation)

### Pipeline
- Runs on combined dataset (your company + competitors)
- Produces: reputation score, models, sentiment, forecast, clusters
- Results cached and used across all pages

---

## 📞 Need Help?

1. **Check logs** (Terminal output)
2. **Verify Ollama running** (http://127.0.0.1:11434/api/tags)
3. **Browser console** (F12 → Console tab)
4. **Restart everything** (Kill terminals, start fresh)

---

## 🎉 You're Ready!

```
✅ Ollama running
✅ Backend running  
✅ Frontend running
✅ Data uploading
✅ AI analyzing
✅ Insights showing

Welcome to ValorEdge AI! 🚀
```

