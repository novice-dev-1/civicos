from haversine import haversine, Unit


def km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    return haversine((lat1, lng1), (lat2, lng2), unit=Unit.KILOMETERS)


def eta_minutes(distance_km: float, avg_speed_kmh: float = 30.0) -> float:
    return round((distance_km / avg_speed_kmh) * 60.0, 1)
