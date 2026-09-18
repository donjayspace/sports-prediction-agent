from __future__ import annotations

from typing import Mapping


class FeatureAnalyzer:
    """Derives qualitative signals from engineered numeric features."""

    def summarize(self, features: Mapping[str, float]) -> dict[str, str]:
        summary: dict[str, str] = {}
        for name, value in features.items():
            if "attack" in name:
                summary[name] = "strong" if value > 1.5 else "average" if value > 0.8 else "weak"
            elif "defence" in name or "against" in name:
                summary[name] = "solid" if value < 1.0 else "leaky" if value < 1.8 else "porous"
            elif "ppg" in name:
                summary[name] = "hot" if value > 2.0 else "steady" if value > 1.2 else "cold"
        return summary
