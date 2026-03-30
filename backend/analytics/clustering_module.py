from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans


class ClusteringModule:
    def __init__(self, reduced_matrix, tfidf_matrix, feature_names: List[str], n_clusters: int = 3) -> None:
        self.reduced_matrix = reduced_matrix
        self.tfidf_matrix = tfidf_matrix
        self.feature_names = feature_names
        self.n_clusters = max(2, min(n_clusters, len(reduced_matrix)))

    def _interpret_clusters(self, labels: np.ndarray, top_n: int = 6) -> Dict[str, Any]:
        dense = self.tfidf_matrix.toarray()
        cluster_keywords: Dict[str, List[str]] = {}
        cluster_sizes: Dict[str, int] = {}
        for cluster_id in sorted(set(labels.tolist())):
            idx = np.where(labels == cluster_id)[0]
            cluster_sizes[str(cluster_id)] = int(len(idx))
            if len(idx) == 0:
                cluster_keywords[str(cluster_id)] = []
                continue
            centroid = dense[idx].mean(axis=0)
            top_terms_idx = np.argsort(centroid)[-top_n:][::-1]
            cluster_keywords[str(cluster_id)] = [self.feature_names[i] for i in top_terms_idx if centroid[i] > 0]

        return {
            "cluster_sizes": cluster_sizes,
            "cluster_keywords": cluster_keywords,
        }

    def run(self) -> Dict[str, Any]:
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        kmeans_labels = kmeans.fit_predict(self.reduced_matrix)

        hierarchical = AgglomerativeClustering(n_clusters=self.n_clusters)
        hierarchical_labels = hierarchical.fit_predict(self.reduced_matrix)

        interpretations = self._interpret_clusters(kmeans_labels)

        points = []
        for i, row in enumerate(self.reduced_matrix):
            x = float(row[0]) if len(row) > 0 else 0.0
            y = float(row[1]) if len(row) > 1 else 0.0
            points.append(
                {
                    "index": int(i),
                    "x": x,
                    "y": y,
                    "kmeans_label": int(kmeans_labels[i]),
                    "hierarchical_label": int(hierarchical_labels[i]),
                }
            )

        return {
            "kmeans_labels": [int(x) for x in kmeans_labels.tolist()],
            "hierarchical_labels": [int(x) for x in hierarchical_labels.tolist()],
            "points": points,
            "interpretation": interpretations,
            "artifacts": {
                "kmeans_model": kmeans,
            },
        }

    @staticmethod
    def assign_new_text_cluster(clean_text: str, vectorizer, pca_model, kmeans_model) -> int:
        tfidf = vectorizer.transform([clean_text])
        reduced = pca_model.transform(tfidf.toarray())
        return int(kmeans_model.predict(reduced)[0])
