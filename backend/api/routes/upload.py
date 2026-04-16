import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from utils.dataset_validator import DatasetValidator

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        if file.content_type not in ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        dest_path = os.path.join(UPLOAD_DIR, "dataset.csv")

        content = await file.read()

        # Save raw file data and optionally convert excel to csv
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

        preview = df.head(5).to_dict(orient="records")

        return JSONResponse({
            "rows": len(df),
            "columns": df.columns.tolist(),
            "preview": preview
        })

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
