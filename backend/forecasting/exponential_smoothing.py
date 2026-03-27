import pandas as pd

from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing


class ExponentialSmoothingModel:

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    def single_exponential(self, column, alpha=0.3):
        model = SimpleExpSmoothing(self.df[column].astype(float))
        fit_model = model.fit(smoothing_level=alpha, optimized=False)
        forecast = fit_model.forecast(3)
        return forecast.tolist()

    def double_exponential(self, column):
        model = ExponentialSmoothing(self.df[column].astype(float), trend="add", damped_trend=False)
        fit_model = model.fit(optimized=True)
        forecast = fit_model.forecast(3)
        return forecast.tolist()
