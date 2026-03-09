import pandas as pd

from models.regression_models import RegressionModels
from models.logistic_model import ReputationClassifier


class PredictionService:

    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)

    def run_prediction(self):

        features = [
            "sentiment_score",
            "revenue_growth",
            "esg_score"
        ]

        target = "reputation_score"

        regression = RegressionModels(self.df)

        result = regression.multiple_regression(features, target)

        predicted_score = result["predictions"].mean()

        classifier = ReputationClassifier(self.df)

        self.df = classifier.create_reputation_classes(target)

        classifier.train_model(features)

        prediction = classifier.predict(
            self.df[features].iloc[-1].tolist()
        )

        return {
            "predicted_score": float(predicted_score),
            "prediction": prediction
        }