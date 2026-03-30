from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


class ModelComparison:
    def __init__(self, feature_df: pd.DataFrame, target: pd.Series) -> None:
        self.feature_df = feature_df
        self.target = target

    def _evaluate(self, model, x_train, x_test, y_train, y_test) -> Dict[str, Any]:
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        mse = float(mean_squared_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        mae = float(mean_absolute_error(y_test, preds))
        r2 = float(r2_score(y_test, preds))
        return {
            "model": model,
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "predictions": [float(x) for x in preds.tolist()],
            "actual": [float(x) for x in y_test.tolist()],
        }

    def run(self) -> Dict[str, Any]:
        if len(self.feature_df) < 6:
            raise ValueError("Need at least 6 rows to train and evaluate predictive models.")

        x_train, x_test, y_train, y_test = train_test_split(
            self.feature_df,
            self.target,
            test_size=0.2,
            random_state=42,
        )

        linear_result = self._evaluate(LinearRegression(), x_train, x_test, y_train, y_test)
        rf_result = self._evaluate(
            RandomForestRegressor(n_estimators=250, random_state=42),
            x_train,
            x_test,
            y_train,
            y_test,
        )

        linear_model = linear_result.pop("model")
        rf_model = rf_result.pop("model")

        best_name = "random_forest" if rf_result["rmse"] <= linear_result["rmse"] else "linear_regression"

        feature_importance = [
            {"feature": feature, "importance": float(importance)}
            for feature, importance in zip(self.feature_df.columns, rf_model.feature_importances_)
        ]
        feature_importance = sorted(feature_importance, key=lambda x: x["importance"], reverse=True)

        linear_coefficients = [
            {"feature": feature, "coefficient": float(coef)}
            for feature, coef in zip(self.feature_df.columns, linear_model.coef_)
        ]

        metrics_table: List[Dict[str, Any]] = [
            {
                "model": "linear_regression",
                "mse": linear_result["mse"],
                "rmse": linear_result["rmse"],
                "mae": linear_result["mae"],
                "r2": linear_result["r2"],
            },
            {
                "model": "random_forest",
                "mse": rf_result["mse"],
                "rmse": rf_result["rmse"],
                "mae": rf_result["mae"],
                "r2": rf_result["r2"],
            },
        ]

        return {
            "models": {
                "linear_regression": linear_result,
                "random_forest": rf_result,
            },
            "model_comparison": metrics_table,
            "best_model": best_name,
            "feature_importance": feature_importance,
            "linear_coefficients": linear_coefficients,
            "artifacts": {
                "best_model": rf_model if best_name == "random_forest" else linear_model,
            },
        }
