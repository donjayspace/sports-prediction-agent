from __future__ import annotations

def build_features(data: dict) -> dict[str, float]:
    a = float(data.get("surface_elo_a",1500)); b = float(data.get("surface_elo_b",1500))
    return {"surface_elo_a":a,"surface_elo_b":b,"surface_elo_diff":a-b,"serve_points_won_diff":float(data.get("serve_points_won_a",.65))-float(data.get("serve_points_won_b",.65)),"return_points_won_diff":float(data.get("return_points_won_a",.35))-float(data.get("return_points_won_b",.35)),"workload_diff":float(data.get("workload_a",0))-float(data.get("workload_b",0))}
