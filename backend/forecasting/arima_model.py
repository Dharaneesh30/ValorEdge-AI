import pandas as pd
import numpy as np

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing


class ForecastEngine:

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    # -------------------------------------
    # Moving Average
    # -------------------------------------
    def moving_average(self, column, window=3):

        self.df[f"{column}_ma"] = self.df[column].rolling(window=window).mean()

        return self.df

    # -------------------------------------
    # Exponential Smoothing
    # -------------------------------------
    def exponential_smoothing(self, column):

        model = ExponentialSmoothing(self.df[column], trend="add")

        fit_model = model.fit()

        forecast = fit_model.forecast(3)

        return forecast

    # -------------------------------------
    # ADF Test (Stationarity)
    # -------------------------------------
    def adf_test(self, column):

        result = adfuller(self.df[column])

        return {
            "ADF Statistic": result[0],
            "p-value": result[1],
            "Stationary": result[1] < 0.05
        }

    # -------------------------------------
    # Auto Regression (AR)
    # -------------------------------------
    def auto_regression(self, column, lags=3):

        model = AutoReg(self.df[column], lags=lags)

        model_fit = model.fit()

        forecast = model_fit.predict(
            start=len(self.df),
            end=len(self.df) + 3
        )

        return forecast

    # -------------------------------------
    # ARIMA Model
    # -------------------------------------
    def arima_forecast(self, column, order=(1,1,1)):

        model = ARIMA(self.df[column], order=order)

        model_fit = model.fit()

        forecast = model_fit.forecast(steps=3)

        return forecast

    # -------------------------------------
    # Multivariate Forecast
    # -------------------------------------
    def multivariate_forecast(self, columns):

        data = self.df[columns]

        forecasts = {}

        for col in columns:

            model = ARIMA(data[col], order=(1,1,1))
            model_fit = model.fit()

            forecast = model_fit.forecast(steps=3)

            forecasts[col] = forecast.tolist()

        return forecasts