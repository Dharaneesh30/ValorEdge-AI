import pandas as pd


class CorrelationAnalysis:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def compute(self):
        numeric_data = self.data.select_dtypes(include=["number"])
        if numeric_data.empty:
            return {}

        corr = numeric_data.corr(method='pearson')
        return corr.fillna(0).to_dict()
