import pandas as pd
import numpy as np

from models.regression_models import RegressionModels
from models.logistic_model import ReputationClassifier

class PredictionService:

    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)

    def run_prediction(self):

        features = [
            "sentiment_score",
            "revenue_growth",
            "esg_score",
            "employee_rating",
            "market_share",
            "media_mentions",
            "customer_satisfaction"
        ]

        target = "reputation_score"

        regression = RegressionModels(self.df)

        result = regression.multiple_regression(features, target)

        predicted_score = float(np.mean(result["predictions"]))

        classifier = ReputationClassifier(self.df)

        self.df = classifier.create_reputation_classes(target)

        classifier.train_model(features)

        prediction = classifier.predict(
            self.df[features].iloc[-1].tolist()
        )

        return {
            "predicted_score": predicted_score,
            "reputation_class": prediction,
            "coefficients": result.get("coefficients", {})
        }