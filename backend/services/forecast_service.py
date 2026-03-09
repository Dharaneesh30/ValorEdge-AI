import pandas as pd

from forecasting.arima_model import ForecastEngine


class ForecastService:

    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)

    def run_forecast(self):

        engine = ForecastEngine(self.df)

        forecast = engine.arima_forecast("reputation_score")

        return [float(x) for x in forecast]