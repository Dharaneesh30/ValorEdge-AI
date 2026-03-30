from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller


class ReputationForecaster:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.sort_values("date").copy()

    def _daily_series(self) -> pd.Series:
        series = self.df.set_index("date")["sentiment_score"].resample("D").mean().interpolate("linear")
        return series

    def forecast(self, days: int = 30) -> Dict[str, Any]:
        series = self._daily_series()
        adf = {"statistic": None, "p_value": None, "is_stationary": None}
        if len(series) >= 5:
            try:
                adf_result = adfuller(series.dropna())
                adf = {
                    "statistic": float(adf_result[0]),
                    "p_value": float(adf_result[1]),
                    "is_stationary": bool(adf_result[1] < 0.05),
                }
            except Exception:
                pass
        if len(series) < 8:
            last = float(series.iloc[-1]) if len(series) else 0.0
            future_dates = pd.date_range(start=self.df["date"].max() + pd.Timedelta(days=1), periods=days, freq="D")
            return {
                "method": "naive",
                "adf_test": adf,
                "forecast": [{"date": str(d.date()), "value": last} for d in future_dates],
            }

        model = ARIMA(series, order=(1, 1, 1))
        fit = model.fit()
        pred = fit.forecast(steps=days)

        forecast_items: List[Dict[str, Any]] = []
        for date, value in pred.items():
            forecast_items.append({"date": str(pd.to_datetime(date).date()), "value": float(value)})

        return {
            "method": "arima(1,1,1)",
            "adf_test": adf,
            "forecast": forecast_items,
            "history": [
                {"date": str(idx.date()), "value": float(val)}
                for idx, val in series.items()
            ],
        }
