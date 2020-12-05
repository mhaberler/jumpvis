import gpxpy


def get_bounds(points):
    """
    return bounding box of a list of gpxpy points
    """
    min_lat = None
    max_lat = None
    min_lon = None
    max_lon = None
    min_ele = None
    max_ele = None

    for point in points:
        if min_lat is None or point.latitude < min_lat:
            min_lat = point.latitude
        if max_lat is None or point.latitude > max_lat:
            max_lat = point.latitude
        if min_lon is None or point.longitude < min_lon:
            min_lon = point.longitude
        if max_lon is None or point.longitude > max_lon:
            max_lon = point.longitude
        if min_ele is None or point.elevation < min_ele:
            min_ele = point.elevation
        if max_ele is None or point.elevation > max_ele:
            max_ele = point.elevation

    if min_lat and max_lat and min_lon and max_lon:
        return {'min_latitude': min_lat, 'max_latitude': max_lat,
                'min_longitude': min_lon, 'max_longitude': max_lon,
                'min_elevation': min_ele, 'max_elevation': max_ele,
                }
    return None
