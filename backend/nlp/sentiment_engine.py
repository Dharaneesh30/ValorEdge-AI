from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentEngine:

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_text(self, text):

        score = self.analyzer.polarity_scores(text)

        return {
            "positive": score["pos"],
            "neutral": score["neu"],
            "negative": score["neg"],
            "compound": score["compound"]
        }

    def analyze_dataset(self, texts):

        results = []

        for text in texts:
            results.append(self.analyze_text(text)["compound"])

        return results

    def batch_analyze(self, df, text_column):

        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in dataframe")

        df = df.copy()

        df["sentiment_score"] = df[text_column].fillna("").astype(str).apply(
            lambda t: self.analyze_text(t)["compound"]
        )

        return df