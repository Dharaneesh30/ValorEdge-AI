import pandas as pd


class DatasetValidator:

    # required columns for ValorEdge AI
    REQUIRED_COLUMNS = [
        "company",
        "year",
        "month",
        "period",
        "sentiment_score",
        "revenue_growth",
        "esg_score",
        "employee_rating",
        "market_share",
        "media_mentions",
        "customer_satisfaction",
        "reputation_score",
        "event_note"
    ]

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None

    # -----------------------------
    # Load Dataset
    # -----------------------------
    def load_dataset(self):

        if self.file_path.endswith(".csv"):
            self.df = pd.read_csv(self.file_path)

        elif self.file_path.endswith(".xlsx"):
            self.df = pd.read_excel(self.file_path)

        else:
            raise ValueError("Unsupported file format. Use CSV or Excel.")

        return self.df

    # -----------------------------
    # Check Required Columns
    # -----------------------------
    def validate_columns(self):

        missing_columns = []

        for col in self.REQUIRED_COLUMNS:
            if col not in self.df.columns:
                missing_columns.append(col)

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        return True

    # -----------------------------
    # Validate Data Types
    # -----------------------------
    def validate_data_types(self):

        numeric_columns = [
            "year",
            "sentiment_score",
            "revenue_growth",
            "esg_score",
            "employee_rating",
            "market_share",
            "media_mentions",
            "customer_satisfaction",
            "reputation_score"
        ]

        # Cast numeric columns to numeric type and validate
        for col in numeric_columns:
            self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
            if self.df[col].isna().all():
                raise ValueError(f"Column '{col}' must contain numeric values")

        return True

    # -----------------------------
    # Validate Year Column
    # -----------------------------
    def validate_year(self):

        self.df["year"] = pd.to_numeric(self.df["year"], errors="coerce")
        if self.df["year"].isna().all():
            raise ValueError("Year column must contain numeric values")

        return True

    # -----------------------------
    # Run Full Validation
    # -----------------------------
    def run_validation(self):

        self.load_dataset()

        self.validate_columns()
        self.validate_data_types()
        self.validate_year()

        return self.df