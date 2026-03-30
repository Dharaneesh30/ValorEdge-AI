from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

import pandas as pd


class CompanyBenchmarkService:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()
        if "company" not in self.df.columns:
            self.df["company"] = "Unknown"
        self.df["company"] = self.df["company"].fillna("Unknown").astype(str)
        self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")

    def _trend(self, company_df: pd.DataFrame) -> float:
        series = company_df.sort_values("date").groupby(company_df["date"].dt.date)["sentiment_score"].mean()
        if len(series) < 2:
            return 0.0
        return float(series.iloc[-1] - series.iloc[0])

    def _company_word_profile(self, company_df: pd.DataFrame, top_n: int = 20) -> List[str]:
        words = " ".join(company_df.get("clean_text", company_df["text"]).astype(str)).split()
        if not words:
            return []
        counts = Counter(words)
        return [w for w, _ in counts.most_common(top_n)]

    def _rule_based_recommendations(self, target: Dict[str, Any], peers: List[Dict[str, Any]]) -> List[str]:
        recs: List[str] = []
        better_peers = [p for p in peers if p["sentiment_mean"] > target["sentiment_mean"]]

        if better_peers:
            recs.append("Replicate communication patterns from top-performing peers with higher sentiment momentum.")

        if target["positive_ratio"] < 0.6:
            recs.append("Increase positive narrative share through customer success stories and transparent ESG progress updates.")

        if target["trend"] < 0:
            recs.append("Run a 30-day reputation recovery sprint focused on recent negative themes and rapid response messaging.")

        if not recs:
            recs.append("Current sentiment is competitive; maintain consistency and monitor emerging negative topics weekly.")

        return recs

    def compare_one_vs_many(self, target_company: str) -> Dict[str, Any]:
        companies = sorted(self.df["company"].unique().tolist())
        if target_company not in companies:
            raise ValueError(f"Company '{target_company}' not found. Available companies: {companies}")

        stats = []
        for company, group in self.df.groupby("company"):
            stats.append(
                {
                    "company": company,
                    "sentiment_mean": float(group["sentiment_score"].mean()),
                    "trend": self._trend(group),
                    "positive_ratio": float((group["sentiment_score"] > 0).mean()),
                    "sample_size": int(len(group)),
                    "top_keywords": self._company_word_profile(group, top_n=10),
                }
            )

        target = next(item for item in stats if item["company"] == target_company)
        peers = [item for item in stats if item["company"] != target_company]

        comparison = []
        for peer in sorted(peers, key=lambda x: x["sentiment_mean"], reverse=True):
            comparison.append(
                {
                    "company": peer["company"],
                    "peer_sentiment_mean": round(peer["sentiment_mean"], 4),
                    "gap_vs_target": round(peer["sentiment_mean"] - target["sentiment_mean"], 4),
                    "peer_trend": round(peer["trend"], 4),
                    "peer_positive_ratio": round(peer["positive_ratio"], 4),
                    "top_keywords": peer["top_keywords"],
                }
            )

        better_peers = [c for c in comparison if c["gap_vs_target"] > 0]
        top_peer_keywords = []
        for peer in better_peers[:2]:
            top_peer_keywords.extend(peer["top_keywords"][:6])

        target_words = set(target["top_keywords"])
        missing_focus = [w for w in top_peer_keywords if w not in target_words]

        return {
            "target_company": target_company,
            "available_companies": companies,
            "target_metrics": {
                "sentiment_mean": round(target["sentiment_mean"], 4),
                "trend": round(target["trend"], 4),
                "positive_ratio": round(target["positive_ratio"], 4),
                "sample_size": target["sample_size"],
                "top_keywords": target["top_keywords"],
            },
            "peer_comparison": comparison,
            "focus_keywords_from_peers": list(dict.fromkeys(missing_focus))[:12],
            "rule_based_recommendations": self._rule_based_recommendations(target, peers),
        }
