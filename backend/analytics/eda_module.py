from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    matplotlib = None
    plt = None
import pandas as pd


class EDAModule:
    def __init__(self, df: pd.DataFrame, output_dir: Path) -> None:
        self.df = df.copy()
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_plot(self, fig: plt.Figure, filename: str) -> str:
        plot_path = self.output_dir / filename
        fig.tight_layout()
        fig.savefig(plot_path, dpi=120)
        plt.close(fig)
        return str(plot_path)

    def sentiment_distribution_plot(self) -> str:
        if plt is None:
            return ""
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(self.df["sentiment_score"], bins=20, color="#1f77b4", alpha=0.85)
        ax.set_title("Sentiment Distribution")
        ax.set_xlabel("Sentiment Score")
        ax.set_ylabel("Frequency")
        return self._save_plot(fig, "sentiment_distribution.png")

    def time_series_trend_plot(self) -> str:
        if plt is None:
            return ""
        trend = self.df.groupby(self.df["date"].dt.date)["sentiment_score"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(trend["date"], trend["sentiment_score"], color="#ff7f0e", linewidth=2)
        ax.set_title("Daily Sentiment Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Mean Sentiment")
        ax.tick_params(axis="x", rotation=30)
        return self._save_plot(fig, "sentiment_trend.png")

    def word_frequency(self, top_n: int = 25) -> List[Dict[str, Any]]:
        words = " ".join(self.df["clean_text"].astype(str)).split()
        if not words:
            return []
        freq = pd.Series(words).value_counts().head(top_n)
        return [{"word": idx, "count": int(val)} for idx, val in freq.items()]

    def word_frequency_plot(self, top_n: int = 15) -> str:
        if plt is None:
            return ""
        freq_data = self.word_frequency(top_n=top_n)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        if freq_data:
            words = [item["word"] for item in freq_data][::-1]
            counts = [item["count"] for item in freq_data][::-1]
            ax.barh(words, counts, color="#2ca02c")
        ax.set_title("Top Word Frequencies")
        ax.set_xlabel("Count")
        return self._save_plot(fig, "word_frequency.png")

    def run(self, include_plots: bool = True) -> Dict[str, Any]:
        distribution_path = self.sentiment_distribution_plot() if include_plots else ""
        trend_path = self.time_series_trend_plot() if include_plots else ""
        word_plot_path = self.word_frequency_plot() if include_plots else ""
        word_freq = self.word_frequency()
        numeric_df = self.df.select_dtypes(include=["number"])
        trend_points = (
            self.df.groupby(self.df["date"].dt.date)["sentiment_score"]
            .mean()
            .reset_index()
            .rename(columns={"date": "date", "sentiment_score": "score"})
        )
        stats = {}
        if not numeric_df.empty:
            stats = {
                "mean": {k: float(v) for k, v in numeric_df.mean().to_dict().items()},
                "variance": {k: float(v) for k, v in numeric_df.var().to_dict().items()},
                "std_dev": {k: float(v) for k, v in numeric_df.std().to_dict().items()},
            }

        correlation_matrix = {}
        if not numeric_df.empty:
            correlation_matrix = {
                row: {col: float(val) for col, val in cols.items()}
                for row, cols in numeric_df.corr().fillna(0).to_dict().items()
            }

        return {
            "plots": {
                "sentiment_distribution": distribution_path,
                "sentiment_trend": trend_path,
                "word_frequency": word_plot_path,
            },
            "statistics": stats,
            "correlation_matrix": correlation_matrix,
            "word_frequency": word_freq,
            "trend": [
                {"date": str(row["date"]), "score": float(row["score"])}
                for _, row in trend_points.iterrows()
            ],
            "summary": {
                "row_count": int(len(self.df)),
                "company_count": int(self.df["company"].nunique()),
                "category_count": int(self.df["category"].nunique()),
                "date_min": str(self.df["date"].min().date()) if not self.df.empty else None,
                "date_max": str(self.df["date"].max().date()) if not self.df.empty else None,
            },
        }
