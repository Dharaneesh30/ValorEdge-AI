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
            ["sentiment_score", "revenue_growth", "esg_score"]
        )

        return {
            "statistics": stats,
            "correlation": corr,
            "reputation_score": float(reputation.mean())
        }