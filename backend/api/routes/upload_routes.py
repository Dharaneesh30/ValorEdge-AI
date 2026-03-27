import os
import pandas as pd
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from utils.dataset_validator import DatasetValidator
from services.ai_advice_service import AIAdviceService

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ai_service = AIAdviceService()

@router.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        if file.content_type not in ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        dest_path = os.path.join(UPLOAD_DIR, "dataset.csv")

        content = await file.read()

        if file.filename.lower().endswith(".xlsx"):
            temp_path = os.path.join(UPLOAD_DIR, "dataset.xlsx")
            with open(temp_path, "wb") as f:
                f.write(content)
            validator = DatasetValidator(temp_path)
        else:
            with open(dest_path, "wb") as f:
                f.write(content)
            validator = DatasetValidator(dest_path)

        df = validator.run_validation()

        columns = df.columns.tolist()
        row_count = len(df)

        # detect optional missing columns
        optional_columns = ["media_mentions", "customer_satisfaction"]
        missing_cols = [c for c in optional_columns if c not in columns]

        ai_advice = ai_service.get_upload_advice(columns, row_count, missing_cols)

        preview_df = df.head(5).astype(object)
        clean_preview_df = preview_df.where(pd.notna(preview_df), None)
        preview = clean_preview_df.to_dict(orient="records")

        return JSONResponse({
            "message": "Dataset uploaded and validated successfully",
            "rows": row_count,
            "columns": columns,
            "preview": preview,
            "ai_advice": ai_advice
        })

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
