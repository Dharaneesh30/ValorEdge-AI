import pandas as pd

class ScenarioSimulation:

    def __init__(self, dataframe):
        self.df = dataframe.copy()

    def simulate_growth(self, column, change_percent):

        simulated = self.df[column] * (1 + change_percent / 100)

        return simulated.mean()

    def simulate_decline(self, column, change_percent):

        simulated = self.df[column] * (1 - change_percent / 100)

        return simulated.mean()

    def simulate_custom(self, column, new_value):

        simulated = self.df[column].copy()
        simulated[:] = new_value

        return simulated.mean()