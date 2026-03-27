import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


class ReputationClassifier:

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()
        self.model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000)
        )
        self.feature_columns = []

    # -----------------------------------
    # Create Target Classes
    # -----------------------------------
    def create_reputation_classes(self, score_column):

        conditions = [
            self.df[score_column] > 0.7,
            self.df[score_column] < 0.4
        ]

        choices = ["Growth", "Decline"]

        self.df["reputation_class"] = np.select(conditions, choices, default="Stable")

        return self.df

    # -----------------------------------
    # Train Logistic Model
    # -----------------------------------
    def train_model(self, feature_columns):
        self.feature_columns = feature_columns

        X = self.df[feature_columns]
        y = self.df["reputation_class"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)

        predictions = self.model.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)

        return {
            "model": self.model,
            "accuracy": accuracy,
            "report": classification_report(y_test, predictions)
        }

    # -----------------------------------
    # Predict Reputation Category
    # -----------------------------------
    def predict(self, input_data):
        if isinstance(input_data, dict):
            input_df = pd.DataFrame([input_data], columns=self.feature_columns)
        else:
            input_df = pd.DataFrame([input_data], columns=self.feature_columns)

        prediction = self.model.predict(input_df)

        return prediction[0]
