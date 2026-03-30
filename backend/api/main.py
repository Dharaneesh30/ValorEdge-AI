import os
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if load_dotenv is not None:
    load_dotenv(os.path.join(ROOT_DIR, "backend", ".env"))
    load_dotenv(os.path.join(ROOT_DIR, ".env"))

try:
    from api.routes.upload_routes import router as upload_router
    from api.routes.analysis_routes import router as analysis_router
    from api.routes.prediction_routes import router as prediction_router
    from api.routes.forecast_routes import router as forecast_router
    from api.routes.ai_routes import router as ai_router
    from api.routes.pipeline_routes import router as pipeline_router
except ModuleNotFoundError:
    from backend.api.routes.upload_routes import router as upload_router
    from backend.api.routes.analysis_routes import router as analysis_router
    from backend.api.routes.prediction_routes import router as prediction_router
    from backend.api.routes.forecast_routes import router as forecast_router
    from backend.api.routes.ai_routes import router as ai_router
    from backend.api.routes.pipeline_routes import router as pipeline_router

app = FastAPI(title="ValorEdge AI")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api/upload", tags=["upload"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis"])
app.include_router(prediction_router, prefix="/api/predict", tags=["prediction"])
app.include_router(forecast_router, prefix="/api/forecast", tags=["forecast"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
app.include_router(pipeline_router, tags=["pipeline"])


@app.get("/")
def health_check():
    return {"status": "ValorEdge AI is running"}
