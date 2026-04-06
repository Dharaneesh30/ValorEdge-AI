from __future__ import annotations

import re
import string
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


class TextPreprocessor:
    REQUIRED_COLUMNS = ("date", "text")

    def __init__(self) -> None:
        self.stopwords = set(ENGLISH_STOP_WORDS)

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [str(c).strip().lower() for c in df.columns]
        # If upload contains case-variant duplicate names (e.g., Company + company),
        # keep first occurrence to avoid DataFrame-returning column selection later.
        df = df.loc[:, ~df.columns.duplicated()].copy()
        return df

    def validate_schema(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        return len(missing) == 0, missing

    def clean_text(self, text: str) -> str:
        text = str(text or "").lower()
        text = re.sub(r"http\S+|www\.\S+", " ", text)
        text = text.translate(str.maketrans("", "", string.punctuation))
        text = re.sub(r"\s+", " ", text).strip()
        tokens = [token for token in text.split() if token not in self.stopwords]
        return " ".join(tokens)

    def preprocess(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        df = self._normalize_columns(raw_df)
        is_valid, missing = self.validate_schema(df)
        if not is_valid:
            raise ValueError(f"Missing required columns: {missing}. Expected columns include 'date' and 'text'.")

        if "company" not in df.columns:
            df["company"] = "Unknown"
        if "category" not in df.columns:
            df["category"] = "General"

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).copy()

        df["text"] = df["text"].fillna("").astype(str)
        df["clean_text"] = df["text"].apply(self.clean_text)
        df = df[df["clean_text"].str.len() > 0].copy()

        for col in ("company", "category"):
            df[col] = df[col].fillna("Unknown").astype(str)

        df = df.sort_values("date").drop_duplicates(subset=["date", "text", "company", "category"])
        df = df.reset_index(drop=True)
        return df

    @staticmethod
    def save_processed(df: pd.DataFrame, output_path: Path) -> str:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        return str(output_path)
