from __future__ import annotations

def build_features(data: dict) -> dict[str, float]:
    home_off = float(data.get("home_offensive_rating", 110))
    away_off = float(data.get("away_offensive_rating", 110))
    home_def = float(data.get("home_defensive_rating", 110))
    away_def = float(data.get("away_defensive_rating", 110))
    return {"home_offensive_rating": home_off, "away_offensive_rating": away_off, "home_defensive_rating": home_def, "away_defensive_rating": away_def, "net_rating_diff": (home_off-home_def)-(away_off-away_def), "pace": float(data.get("pace",100)), "rest_days_home": float(data.get("rest_days_home",1)), "rest_days_away": float(data.get("rest_days_away",1))}
