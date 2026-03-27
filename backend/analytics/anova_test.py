import pandas as pd
from scipy.stats import f_oneway


class AnovaTest:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def run(self):
        if "company" not in self.data.columns:
            raise ValueError("'company' column required for ANOVA test")

        numeric_columns = [
            col for col in self.data.select_dtypes(include=["number"]).columns
            if col != "year"
        ]

        result = {}

        grouped = self.data.groupby("company")

        for col in numeric_columns:
            groups = [group[col].dropna().values for _, group in grouped]
            if len(groups) < 2:
                result[col] = {"f_statistic": None, "p_value": None}
                continue

            try:
                f_stat, p_val = f_oneway(*groups)
                result[col] = {
                    "f_statistic": float(f_stat) if f_stat is not None else None,
                    "p_value": float(p_val) if p_val is not None else None,
                }
            except Exception as e:
                result[col] = {"f_statistic": None, "p_value": None, "error": str(e)}

        return result
