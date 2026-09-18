from __future__ import annotations

def build_features(data: dict) -> dict[str, float]:
    return {
        "home_elo": float(data.get("home_elo", 1500)),
        "away_elo": float(data.get("away_elo", 1500)),
        "elo_diff": float(data.get("home_elo", 1500)) - float(data.get("away_elo", 1500)),
        "home_xg": max(float(data.get("home_xg", 1.0)), 0.01),
        "away_xg": max(float(data.get("away_xg", 1.0)), 0.01),
    }
