import pandas as pd

from forecasting.arima_model import ForecastEngine

class ForecastService:

    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)

    def run_forecast(self):

        engine = ForecastEngine(self.df)

        arima_forecast = engine.arima_forecast("reputation_score")
        smoothing_forecast = engine.exponential_smoothing("reputation_score")

        trend = "Increasing" if arima_forecast[-1] > arima_forecast[0] else "Declining"

        return {
            "arima_forecast": [float(x) for x in arima_forecast],
            "smoothing_forecast": [float(x) for x in smoothing_forecast],
            "trend": trend
        }