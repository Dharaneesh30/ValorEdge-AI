import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, mean_absolute_error


class RegressionModels:

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()
        self.model = None

    # ----------------------------------
    # Prepare Data
    # ----------------------------------
    def prepare_data(self, feature_columns, target_column):

        X = self.df[feature_columns]
        y = self.df[target_column]

        return X, y

    # ----------------------------------
    # Linear Regression
    # ----------------------------------
    def linear_regression(self, feature_columns, target_column):

        X, y = self.prepare_data(feature_columns, target_column)

        model = LinearRegression()
        model.fit(X, y)

        predictions = model.predict(X)

        return {
            "model": model,
            "predictions": predictions,
            "mse": mean_squared_error(y, predictions),
            "mae": mean_absolute_error(y, predictions)
        }

    # ----------------------------------
    # Multiple Regression
    # ----------------------------------
    def multiple_regression(self, feature_columns, target_column):

        X, y = self.prepare_data(feature_columns, target_column)

        model = LinearRegression()
        model.fit(X, y)

        predictions = model.predict(X)

        return {
            "model": model,
            "coefficients": dict(zip(feature_columns, model.coef_)),
            "predictions": predictions
        }

    # ----------------------------------
    # Polynomial Regression
    # ----------------------------------
    def polynomial_regression(self, feature_columns, target_column, degree=2):

        X, y = self.prepare_data(feature_columns, target_column)

        poly = PolynomialFeatures(degree=degree)
        X_poly = poly.fit_transform(X)

        model = LinearRegression()
        model.fit(X_poly, y)

        predictions = model.predict(X_poly)

        return {
            "model": model,
            "predictions": predictions,
            "mse": mean_squared_error(y, predictions)
        }

    # ----------------------------------
    # Evaluate Model
    # ----------------------------------
    def evaluate_model(self, actual, predicted):

        mse = mean_squared_error(actual, predicted)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(actual, predicted)

        return {
            "MSE": mse,
            "RMSE": rmse,
            "MAE": mae
        }