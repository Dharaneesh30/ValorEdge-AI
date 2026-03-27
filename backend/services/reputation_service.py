import pandas as pd

from analytics.descriptive_stats import DescriptiveStats
from analytics.correlation_analysis import CorrelationAnalysis
from analytics.reputation_index import ReputationIndex


class ReputationService:

    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)

    def run_analysis(self):

        stats = DescriptiveStats(self.df).compute()

        corr = CorrelationAnalysis(self.df).compute()

        reputation = ReputationIndex(self.df).compute_reputation_score(
            ["sentiment_score", "revenue_growth", "esg_score", "employee_rating", "market_share"]
        )

        # top correlations to reputation_score
        numeric_df = self.df.select_dtypes(include=["number"])
        correlation_values = (
            numeric_df.corr().get("reputation_score", pd.Series(dtype=float)).drop("reputation_score", errors="ignore")
        )
        top_correlations = correlation_values.abs().sort_values(ascending=False).head(3).to_dict()

        weak_areas = []
        mean_score = self.df["reputation_score"].mean()
        for col in ["sentiment_score", "revenue_growth", "esg_score", "employee_rating", "market_share", "media_mentions", "customer_satisfaction"]:
            if col in self.df.columns and self.df[col].mean() < self.df[col].mean() * 0.9:
                weak_areas.append(col)

        return {
            "statistics": stats,
            "correlation": corr,
            "reputation_score": float(reputation.mean()),
            "top_correlations": {k: float(v) for k, v in top_correlations.items()},
            "weak_areas": weak_areas
        }
