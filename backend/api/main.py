from models.regression_models import RegressionModels
from models.logistic_model import ReputationClassifier
from fastapi import FastAPI, UploadFile, File
from forecasting.arima_model import ForecastEngine
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

from utils.dataset_validator import DatasetValidator

app = FastAPI(title="ValorEdge AI API")

# allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # validate dataset
    validator = DatasetValidator(file_path)
    df = validator.run_validation()

    return {
        "message": "Dataset uploaded and validated successfully",
        "rows": len(df),
        "columns": list(df.columns)
    }

@app.get("/analysis")
def run_analysis():

    import pandas as pd

    df = pd.read_csv("uploads/dataset.csv")

    # Descriptive statistics
    stats_engine = DescriptiveStats(df)
    stats = stats_engine.compute()

    # Correlation matrix
    corr_engine = CorrelationAnalysis(df)
    corr = corr_engine.compute()

    # Reputation index
    rep_engine = ReputationIndex(df)
    reputation_scores = rep_engine.compute_reputation_score(
        ["sentiment_score", "revenue_growth", "esg_score"]
    )

    return {
        "descriptive_statistics": stats,
        "correlation_matrix": corr,
        "reputation_score": float(reputation_scores.mean())
    }
@app.get("/forecast")
def run_forecast():

    import pandas as pd

    df = pd.read_csv("uploads/dataset.csv")

    forecast_engine = ForecastEngine(df)

    # ARIMA forecast for reputation score
    forecast = forecast_engine.arima_forecast("reputation_score")

    # Convert to normal list for JSON response
    forecast_values = [float(x) for x in forecast]

    return {
        "forecast_values": forecast_values
    }