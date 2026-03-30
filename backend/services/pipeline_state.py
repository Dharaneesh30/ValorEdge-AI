from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional


@dataclass
class PipelineArtifacts:
    """Holds in-memory artifacts from the latest pipeline run."""

    latest_upload_path: Optional[Path] = None
    processed_path: Optional[Path] = None
    eda: Dict[str, Any] = field(default_factory=dict)
    sentiment: Dict[str, Any] = field(default_factory=dict)
    pca: Dict[str, Any] = field(default_factory=dict)
    clusters: Dict[str, Any] = field(default_factory=dict)
    models: Dict[str, Any] = field(default_factory=dict)
    forecast: Dict[str, Any] = field(default_factory=dict)
    genai_insights: Dict[str, Any] = field(default_factory=dict)
    reputation: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PipelineState:
    def __init__(self) -> None:
        self._lock = Lock()
        self._artifacts = PipelineArtifacts()

    def reset(self) -> None:
        with self._lock:
            self._artifacts = PipelineArtifacts()

    def update(self, **kwargs: Any) -> None:
        with self._lock:
            for key, value in kwargs.items():
                setattr(self._artifacts, key, value)

    def snapshot(self) -> PipelineArtifacts:
        with self._lock:
            # Lightweight copy for read-only route use.
            return PipelineArtifacts(
                latest_upload_path=self._artifacts.latest_upload_path,
                processed_path=self._artifacts.processed_path,
                eda=dict(self._artifacts.eda),
                sentiment=dict(self._artifacts.sentiment),
                pca=dict(self._artifacts.pca),
                clusters=dict(self._artifacts.clusters),
                models=dict(self._artifacts.models),
                forecast=dict(self._artifacts.forecast),
                genai_insights=dict(self._artifacts.genai_insights),
                reputation=dict(self._artifacts.reputation),
                metadata=dict(self._artifacts.metadata),
            )


pipeline_state = PipelineState()
