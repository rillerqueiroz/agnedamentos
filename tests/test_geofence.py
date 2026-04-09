from app.services.geofence import haversine_meters, inside_geofence


def test_haversine_distance_is_zero_for_same_point():
    assert haversine_meters(-23.55, -46.63, -23.55, -46.63) == 0


def test_inside_geofence_returns_true_for_near_point():
    assert inside_geofence(-23.5506, -46.6332, -23.55052, -46.633308, 100)


def test_inside_geofence_returns_false_for_far_point():
    assert not inside_geofence(-23.60, -46.70, -23.55052, -46.633308, 100)
