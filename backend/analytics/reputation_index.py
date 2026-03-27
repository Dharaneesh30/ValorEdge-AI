import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class ReputationIndex:

    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    # -----------------------------
    # Simple Aggregate Index
    # -----------------------------
    def simple_aggregate_index(self, columns):
        return self.data[columns].mean(axis=1)

    # -----------------------------
    # Weighted Aggregate Index
    # -----------------------------
    def weighted_index(self, columns, weights):
        values = self.data[columns].values
        weights = np.array(weights)

        weighted_scores = np.dot(values, weights)
        normalized = weighted_scores / weights.sum()

        return normalized

    # -----------------------------
    # Laspeyres Index
    # -----------------------------
    def laspeyres_index(self, base_values, current_values, base_weights):
        numerator = np.sum(current_values * base_weights)
        denominator = np.sum(base_values * base_weights)

        return numerator / denominator

    # -----------------------------
    # Paasche Index
    # -----------------------------
    def paasche_index(self, base_values, current_values, current_weights):
        numerator = np.sum(current_values * current_weights)
        denominator = np.sum(base_values * current_weights)

        return numerator / denominator

    # -----------------------------
    # Fisher Ideal Index
    # -----------------------------
    def fisher_index(self, base_values, current_values, base_weights, current_weights):

        laspeyres = self.laspeyres_index(base_values, current_values, base_weights)
        paasche = self.paasche_index(base_values, current_values, current_weights)

        return np.sqrt(laspeyres * paasche)

    # -----------------------------
    # Automatic Weight Estimation
    # (Data-driven weights)
    # -----------------------------
    def estimate_weights(self, feature_columns, target_column):

        X = self.data[feature_columns]
        y = self.data[target_column]

        model = LinearRegression()
        model.fit(X, y)

        weights = np.abs(model.coef_)
        weights = weights / weights.sum()

        return dict(zip(feature_columns, weights))

    # -----------------------------
    # Compute Reputation Score
    # -----------------------------
    def compute_reputation_score(self, feature_columns, weights=None):

        if weights is None:
            # automatic weights
            weights = np.ones(len(feature_columns))

        scores = self.weighted_index(feature_columns, weights)

        return scores