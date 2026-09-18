from __future__ import annotations
import math

def logistic_distribution(score: float) -> dict[str, float]:
    home=1.0/(1.0+math.exp(-score)); return {"home":home,"away":1.0-home}
