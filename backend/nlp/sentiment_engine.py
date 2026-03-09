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