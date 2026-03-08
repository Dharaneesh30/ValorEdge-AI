from fastapi import FastAPI, UploadFile, File
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