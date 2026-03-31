from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from analytics.clustering_module import ClusteringModule
    from analytics.dimensionality_reduction import DimensionalityReducer
    from analytics.eda_module import EDAModule
    from forecasting.reputation_forecaster import ReputationForecaster
    from models.model_comparison import ModelComparison
    from nlp.sentiment_engine import SentimentEngine
    from services.ai_advice_service import AIAdviceService
    from services.pipeline_state import pipeline_state
    from services.reputation_score_engine import ReputationScoreEngine
    from services.text_preprocessing_service import TextPreprocessor
except ModuleNotFoundError:
    from backend.analytics.clustering_module import ClusteringModule
    from backend.analytics.dimensionality_reduction import DimensionalityReducer
    from backend.analytics.eda_module import EDAModule
    from backend.forecasting.reputation_forecaster import ReputationForecaster
    from backend.models.model_comparison import ModelComparison
    from backend.nlp.sentiment_engine import SentimentEngine
    from backend.services.ai_advice_service import AIAdviceService
    from backend.services.pipeline_state import pipeline_state
    from backend.services.reputation_score_engine import ReputationScoreEngine
    from backend.services.text_preprocessing_service import TextPreprocessor


logger = logging.getLogger(__name__)


class FullPipelineService:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.backend_dir = project_root / "backend"
        self.upload_dir = self.backend_dir / "uploads"
        self.data_dir = self.backend_dir / "data"
        self.plots_dir = self.data_dir / "plots"
        self.results_path = self.data_dir / "latest_results.json"
        self.preprocessor = TextPreprocessor()
        self.sentiment_engine = SentimentEngine()
        self.ai_service = AIAdviceService()

        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir.mkdir(parents=True, exist_ok=True)

    def _persist_results(self, payload: Dict[str, Any]) -> None:
        self.results_path.parent.mkdir(parents=True, exist_ok=True)
        with self.results_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True, indent=2)

    @staticmethod
    def _local_insight_fallback(
        reputation_score: float,
        cluster_keywords: Dict[str, Any],
        model_rows: Any,
        forecast_rows: Any,
    ) -> str:
        top_cluster = None
        if isinstance(cluster_keywords, dict) and cluster_keywords:
            top_cluster = next(iter(cluster_keywords.items()))
        top_cluster_text = (
            f"Top cluster drivers: {', '.join((top_cluster[1] or [])[:6])}."
            if top_cluster
            else "Top cluster drivers are not yet available."
        )
        trend = "stable"
        if forecast_rows:
            try:
                first = float(forecast_rows[0].get("value", 0.0))
                last = float(forecast_rows[min(len(forecast_rows) - 1, 6)].get("value", 0.0))
                trend = "improving" if last > first else "declining" if last < first else "stable"
            except Exception:
                trend = "stable"

        best_model = ""
        if isinstance(model_rows, list) and model_rows:
            sorted_rows = sorted(model_rows, key=lambda x: x.get("rmse", 1e9))
            best_model = sorted_rows[0].get("model", "")

        return (
            f"Current reputation score is {reputation_score:.3f}, with a {trend} near-term trajectory. "
            f"{top_cluster_text} "
            f"Best-performing predictive model is {best_model or 'available model'} based on RMSE. "
            "Recommended actions: improve response quality on negative themes, align communication with top positive peer topics, "
            "and monitor weekly sentiment/forecast shifts to trigger rapid mitigation."
        )

    def run(self, uploaded_path: Path) -> Dict[str, Any]:
        logger.info("Pipeline started for upload: %s", uploaded_path)

        raw_df = pd.read_csv(uploaded_path)
        logger.info("Loaded raw dataset with %s rows", len(raw_df))

        cleaned_df = self.preprocessor.preprocess(raw_df)
        logger.info("Preprocessing complete. Rows after cleaning: %s", len(cleaned_df))

        cleaned_df = self.sentiment_engine.batch_analyze(cleaned_df, "clean_text")
        logger.info("Sentiment scoring complete")

        vectorizer = TfidfVectorizer(max_features=400, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(cleaned_df["clean_text"])
        feature_names = vectorizer.get_feature_names_out().tolist()
        logger.info("TF-IDF complete with %s features", len(feature_names))

        reducer = DimensionalityReducer(tfidf_matrix, feature_names)
        reduction = reducer.run(n_components=2)
        pca_matrix = reduction["artifacts"]["pca_matrix"]
        pca_model = reduction["artifacts"]["pca_model"]
        logger.info("PCA and Factor Analysis complete")

        cluster_mod = ClusteringModule(pca_matrix, tfidf_matrix, feature_names, n_clusters=min(4, max(2, len(cleaned_df) // 8 or 2)))
        cluster_result = cluster_mod.run()
        cleaned_df["kmeans_cluster"] = cluster_result["kmeans_labels"]
        cleaned_df["hierarchical_cluster"] = cluster_result["hierarchical_labels"]
        logger.info("Clustering complete")

        # Hybrid feature engineering: TF-IDF + available numeric columns from dataset.
        text_features = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
        numeric_cols = [
            col
            for col in cleaned_df.select_dtypes(include=["number"]).columns
            if col not in {"sentiment_score", "kmeans_cluster", "hierarchical_cluster", "reputation_score"}
        ]
        numeric_features = cleaned_df[numeric_cols].reset_index(drop=True) if numeric_cols else pd.DataFrame(index=cleaned_df.index)
        model_features = pd.concat([text_features.reset_index(drop=True), numeric_features], axis=1)

        target_col = "reputation_score" if "reputation_score" in cleaned_df.columns else "sentiment_score"
        target = cleaned_df[target_col]
        model_results = ModelComparison(model_features, target).run()
        logger.info("Model training and evaluation complete")

        forecast_results = ReputationForecaster(cleaned_df).forecast(days=30)
        logger.info("Forecasting complete")

        reputation = ReputationScoreEngine(cleaned_df).compute()
        logger.info("Reputation score computation complete")

        eda = EDAModule(cleaned_df, self.plots_dir).run()
        logger.info("EDA complete")

        # Build sentiment API payload.
        sentiment_payload = {
            "summary": {
                "min": float(cleaned_df["sentiment_score"].min()),
                "max": float(cleaned_df["sentiment_score"].max()),
                "mean": float(cleaned_df["sentiment_score"].mean()),
            },
            "records": [
                {
                    "date": str(row["date"].date()),
                    "company": row["company"],
                    "category": row["category"],
                    "text": row["text"],
                    "sentiment_score": float(row["sentiment_score"]),
                }
                for _, row in cleaned_df.head(500).iterrows()
            ],
        }

        # GenAI summary from outputs.
        prompt = (
            "You are a corporate reputation analyst. "
            "Summarize current reputation status, 30-day outlook, business impact, and 5 actionable recommendations. "
            f"Reputation score: {reputation['final_reputation_score']}. "
            f"Top cluster keywords: {cluster_result['interpretation']['cluster_keywords']}. "
            f"Model comparison: {model_results['model_comparison']}. "
            f"Forecast sample: {forecast_results['forecast'][:5]}."
        )
        genai_text = self.ai_service.generate_text(prompt)
        if self.ai_service._is_provider_failure(genai_text):
            genai_text = self._local_insight_fallback(
                reputation_score=float(reputation["final_reputation_score"]),
                cluster_keywords=cluster_result["interpretation"]["cluster_keywords"],
                model_rows=model_results["model_comparison"],
                forecast_rows=forecast_results["forecast"],
            )
        genai_payload = {
            "insight_text": genai_text,
            "provider_status": self.ai_service.status(),
        }

        processed_path = self.data_dir / "processed_dataset.csv"
        TextPreprocessor.save_processed(cleaned_df, processed_path)

        full_payload: Dict[str, Any] = {
            "eda": eda,
            "sentiment": sentiment_payload,
            "pca": {
                **reduction["pca"],
                "factor_analysis": reduction["factor_analysis"],
            },
            "clusters": {
                "kmeans_labels": cluster_result["kmeans_labels"],
                "hierarchical_labels": cluster_result["hierarchical_labels"],
                "points": cluster_result["points"],
                "interpretation": cluster_result["interpretation"],
            },
            "models": {
                "model_comparison": model_results["model_comparison"],
                "best_model": model_results["best_model"],
                "feature_importance": model_results["feature_importance"],
                "linear_coefficients": model_results["linear_coefficients"],
                "target_column": target_col,
                "numeric_feature_columns": numeric_cols,
            },
            "forecast": forecast_results,
            "reputation": reputation,
            "genai_insights": genai_payload,
            "metadata": {
                "rows_processed": int(len(cleaned_df)),
                "columns": cleaned_df.columns.tolist(),
                "upload_path": str(uploaded_path),
                "processed_path": str(processed_path),
            },
        }

        pipeline_state.update(
            latest_upload_path=uploaded_path,
            processed_path=processed_path,
            eda=full_payload["eda"],
            sentiment=full_payload["sentiment"],
            pca=full_payload["pca"],
            clusters=full_payload["clusters"],
            models=full_payload["models"],
            forecast=full_payload["forecast"],
            reputation=full_payload["reputation"],
            genai_insights=full_payload["genai_insights"],
            metadata=full_payload["metadata"],
        )

        self._persist_results(full_payload)
        logger.info("Pipeline completed successfully")

        return full_payload

    def assign_text_to_cluster(self, text: str) -> Dict[str, Any]:
        snapshot = pipeline_state.snapshot()
        if not snapshot.processed_path or not snapshot.pca or not snapshot.clusters:
            raise ValueError("Pipeline has not been run yet.")

        df = pd.read_csv(snapshot.processed_path)
        vectorizer = TfidfVectorizer(max_features=400, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(df["clean_text"])
        pca_model = DimensionalityReducer(tfidf_matrix, vectorizer.get_feature_names_out().tolist()).run(n_components=2)["artifacts"]["pca_model"]

        # Rebuild kmeans model from saved labels/points so endpoint is deterministic.
        kmeans = ClusteringModule(
            pca_model.transform(tfidf_matrix.toarray()),
            tfidf_matrix,
            vectorizer.get_feature_names_out().tolist(),
            n_clusters=len(set(snapshot.clusters.get("kmeans_labels", [0, 1]))),
        ).run()["artifacts"]["kmeans_model"]

        clean_text = self.preprocessor.clean_text(text)
        cluster_id = ClusteringModule.assign_new_text_cluster(clean_text, vectorizer, pca_model, kmeans)
        keywords = snapshot.clusters.get("interpretation", {}).get("cluster_keywords", {}).get(str(cluster_id), [])

        return {
            "input_text": text,
            "clean_text": clean_text,
            "assigned_cluster": cluster_id,
            "cluster_keywords": keywords,
        }

    def simulate_scenario(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        snapshot = pipeline_state.snapshot()
        if not snapshot.processed_path:
            raise ValueError("Pipeline has not been run yet.")

        text = str((payload or {}).get("text", "")).strip()
        slider_effect = float((payload or {}).get("sentiment_adjustment", 0.0))
        cluster_weight_adjustment = float((payload or {}).get("cluster_weight_adjustment", 0.0))

        if not text:
            raise ValueError("text is required for scenario simulation.")

        cluster_result = self.assign_text_to_cluster(text)
        sentiment_score = self.sentiment_engine.analyze_text(self.preprocessor.clean_text(text))["compound"]

        base_reputation = float(snapshot.reputation.get("final_reputation_score", 0.5))
        forecast_values = [item.get("value", 0.0) for item in snapshot.forecast.get("forecast", [])[:7]]
        trend_signal = float(np.mean(forecast_values)) if forecast_values else 0.0

        # Convert sentiment to [0,1], include cluster and trend influence.
        sentiment_component = (sentiment_score + 1.0) / 2.0
        cluster_component = 0.5 + (cluster_weight_adjustment / 100.0)
        trend_component = (trend_signal + 1.0) / 2.0

        predicted_reputation = (0.55 * sentiment_component) + (0.25 * trend_component) + (0.20 * cluster_component)
        predicted_reputation = max(0.0, min(1.0, predicted_reputation + (slider_effect / 100.0)))

        prompt = (
            "You are a corporate reputation advisor. "
            f"Scenario text: {text}. "
            f"Assigned cluster: {cluster_result['assigned_cluster']} with keywords {cluster_result['cluster_keywords']}. "
            f"Scenario sentiment: {sentiment_score:.3f}. "
            f"Predicted reputation score: {predicted_reputation:.3f}. "
            "Provide concise business impact and 3 actions."
        )
        insight = self.ai_service.generate_text(prompt)

        return {
            "base_reputation_score": base_reputation,
            "scenario_sentiment_score": float(sentiment_score),
            "assigned_cluster": cluster_result["assigned_cluster"],
            "cluster_keywords": cluster_result["cluster_keywords"],
            "forecast_reference": snapshot.forecast.get("forecast", [])[:7],
            "predicted_reputation_score": round(float(predicted_reputation), 4),
            "ai_insight": insight,
        }
