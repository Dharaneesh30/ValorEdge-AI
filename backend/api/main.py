from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from analytics.reputation_index import ReputationIndex

app = FastAPI(title="ValorEdge AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "ValorEdge AI Backend Running"}


@app.get("/reputation-score")
def reputation_score():

    df = pd.read_csv("data/sample_dataset.csv")

    engine = ReputationIndex(df)

    scores = engine.compute_reputation_score(
        ["sentiment_score", "revenue_growth", "esg_score"]
    )

    return {
        "reputation_score": float(scores.mean())
    }