import os
import logging
import sys
import importlib
from importlib import import_module

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def _safe_load_dotenv(path: str) -> None:
    try:
        dotenv_module = importlib.import_module("dotenv")
        dotenv_loader = getattr(dotenv_module, "load_dotenv", None)
        if callable(dotenv_loader):
            dotenv_loader(path)
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
_safe_load_dotenv(os.path.join(ROOT_DIR, "backend", ".env"))
_safe_load_dotenv(os.path.join(ROOT_DIR, ".env"))

ROUTE_PACKAGE = "backend.api.routes" if (__package__ or "").startswith("backend.") else "api.routes"
upload_router = import_module(f"{ROUTE_PACKAGE}.upload_routes").router
analysis_router = import_module(f"{ROUTE_PACKAGE}.analysis_routes").router
prediction_router = import_module(f"{ROUTE_PACKAGE}.prediction_routes").router
forecast_router = import_module(f"{ROUTE_PACKAGE}.forecast_routes").router
ai_router = import_module(f"{ROUTE_PACKAGE}.ai_routes").router
pipeline_router = import_module(f"{ROUTE_PACKAGE}.pipeline_routes").router

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
