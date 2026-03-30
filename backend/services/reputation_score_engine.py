from __future__ import annotations

from typing import Dict

import pandas as pd


class ReputationScoreEngine:
    """Combines sentiment, trend, and cluster strength into a final score."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy().sort_values("date")

    def compute(self) -> Dict[str, float]:
        sentiment_component = float(((self.df["sentiment_score"] + 1.0) / 2.0).mean())

        daily = self.df.groupby(self.df["date"].dt.date)["sentiment_score"].mean()
        trend_component = 0.5
        if len(daily) >= 2:
            slope = float(daily.iloc[-1] - daily.iloc[0])
            trend_component = max(0.0, min(1.0, 0.5 + slope / 2.0))

        cluster_component = 0.5
        if "kmeans_cluster" in self.df.columns:
            cluster_avg = self.df.groupby("kmeans_cluster")["sentiment_score"].mean()
            cluster_share = self.df["kmeans_cluster"].value_counts(normalize=True)
            weighted_cluster = 0.0
            for cluster_id, share in cluster_share.items():
                weighted_cluster += ((cluster_avg.get(cluster_id, 0.0) + 1.0) / 2.0) * float(share)
            cluster_component = max(0.0, min(1.0, float(weighted_cluster)))

        final_score = (0.55 * sentiment_component) + (0.25 * trend_component) + (0.20 * cluster_component)

        return {
            "sentiment_component": round(sentiment_component, 4),
            "trend_component": round(trend_component, 4),
            "cluster_component": round(cluster_component, 4),
            "final_reputation_score": round(float(final_score), 4),
        }
