from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.decomposition import FactorAnalysis, PCA


class DimensionalityReducer:
    def __init__(self, tfidf_matrix, feature_names: List[str]) -> None:
        self.tfidf_matrix = tfidf_matrix
        self.feature_names = feature_names

    def run_pca(self, n_components: int = 2) -> Dict[str, Any]:
        safe_components = max(1, min(n_components, self.tfidf_matrix.shape[1], self.tfidf_matrix.shape[0]))
        pca = PCA(n_components=safe_components, random_state=42)
        values = pca.fit_transform(self.tfidf_matrix.toarray())

        components = []
        for i, row in enumerate(values):
            item = {"index": int(i)}
            for c_idx, c_val in enumerate(row):
                item[f"pc{c_idx + 1}"] = float(c_val)
            components.append(item)

        return {
            "explained_variance_ratio": [float(x) for x in pca.explained_variance_ratio_],
            "components": components,
            "model": pca,
            "matrix": values,
        }

    def run_factor_analysis(self, n_components: int = 2) -> Dict[str, Any]:
        safe_components = max(1, min(n_components, self.tfidf_matrix.shape[1], self.tfidf_matrix.shape[0]))
        fa = FactorAnalysis(n_components=safe_components, random_state=42)
        values = fa.fit_transform(self.tfidf_matrix.toarray())

        components = []
        for i, row in enumerate(values):
            item = {"index": int(i)}
            for c_idx, c_val in enumerate(row):
                item[f"factor{c_idx + 1}"] = float(c_val)
            components.append(item)

        return {
            "components": components,
            "model": fa,
            "matrix": values,
            "noise_variance": [float(x) for x in np.atleast_1d(fa.noise_variance_)],
        }

    def run(self, n_components: int = 2) -> Dict[str, Any]:
        pca_result = self.run_pca(n_components=n_components)
        fa_result = self.run_factor_analysis(n_components=n_components)
        return {
            "pca": {
                "explained_variance_ratio": pca_result["explained_variance_ratio"],
                "components": pca_result["components"],
            },
            "factor_analysis": {
                "components": fa_result["components"],
                "noise_variance": fa_result["noise_variance"],
            },
            "artifacts": {
                "pca_model": pca_result["model"],
                "pca_matrix": pca_result["matrix"],
                "fa_model": fa_result["model"],
                "fa_matrix": fa_result["matrix"],
            },
        }
