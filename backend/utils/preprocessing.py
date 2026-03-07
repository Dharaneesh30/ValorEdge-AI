import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


class DataPreprocessor:

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    # -----------------------------------
    # Handle Missing Values
    # -----------------------------------
    def handle_missing_values(self):

        for column in self.df.columns:

            if self.df[column].dtype in ['float64', 'int64']:
                self.df[column].fillna(self.df[column].mean(), inplace=True)

            else:
                self.df[column].fillna(self.df[column].mode()[0], inplace=True)

        return self.df

    # -----------------------------------
    # Remove Duplicate Rows
    # -----------------------------------
    def remove_duplicates(self):

        self.df = self.df.drop_duplicates()

        return self.df

    # -----------------------------------
    # Normalize Data (0–1 scaling)
    # -----------------------------------
    def normalize_columns(self, columns):

        for col in columns:
            min_val = self.df[col].min()
            max_val = self.df[col].max()

            self.df[col] = (self.df[col] - min_val) / (max_val - min_val)

        return self.df

    # -----------------------------------
    # Standardize Data (Z-score)
    # -----------------------------------
    def standardize_columns(self, columns):

        scaler = StandardScaler()

        self.df[columns] = scaler.fit_transform(self.df[columns])

        return self.df

    # -----------------------------------
    # Feature Engineering
    # -----------------------------------
    def create_growth_rate(self, column):

        self.df[f"{column}_growth"] = self.df[column].pct_change()

        self.df[f"{column}_growth"].fillna(0, inplace=True)

        return self.df

    # -----------------------------------
    # Full Preprocessing Pipeline
    # -----------------------------------
    def run_pipeline(self, numeric_columns):

        self.handle_missing_values()
        self.remove_duplicates()
        self.normalize_columns(numeric_columns)

        return self.df