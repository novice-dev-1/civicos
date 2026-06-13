SEVERITY_WEIGHT = {"LOW": 1, "MEDIUM": 3, "HIGH": 7, "CRITICAL": 10}
CRITICALITY_BONUS = {"cardiac": 20, "stroke": 18, "burns": 15, "trauma": 10, "general": 0}


def priority_score(
    severity: str, victims: int, minutes_waiting: float, specialty: str
) -> float:
    return (
        SEVERITY_WEIGHT.get(severity, 3)
        + 2 * max(0, victims)
        + 0.5 * max(0.0, minutes_waiting)
        + CRITICALITY_BONUS.get(specialty, 0)
    )
