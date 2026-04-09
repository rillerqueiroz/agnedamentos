from math import asin, cos, radians, sin, sqrt


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_earth_m = 6_371_000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return radius_earth_m * c


def inside_geofence(
    point_lat: float,
    point_lon: float,
    company_lat: float,
    company_lon: float,
    allowed_radius_m: float,
) -> bool:
    distance = haversine_meters(point_lat, point_lon, company_lat, company_lon)
    return distance <= allowed_radius_m
