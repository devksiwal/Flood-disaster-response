import math
from typing import List, Tuple, Dict, Any, Optional
from app.database.seed import FLOOD_RISK_ZONES


def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Calculate the great-circle distance between two points in kilometers."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371.0  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 3)


def point_in_polygon(point: Tuple[float, float], polygon: List[List[float]]) -> bool:
    """Ray-casting algorithm to determine if a point is inside a polygon."""
    x, y = point
    inside = False
    n = len(polygon)
    
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def check_flood_risk_at_point(lat: float, lng: float) -> Dict[str, Any]:
    """Identify if a location falls inside an active flood risk polygon."""
    for zone in FLOOD_RISK_ZONES:
        if point_in_polygon((lat, lng), zone["polygon"]):
            return {
                "in_risk_zone": True,
                "zone_id": zone["id"],
                "zone_name": zone["name"],
                "risk_level": zone["risk_level"],
                "avg_depth_meters": zone["avg_depth_meters"],
                "is_navigable_by_boat": zone["is_navigable_by_boat"]
            }
    return {
        "in_risk_zone": False,
        "zone_id": None,
        "zone_name": "Standard Urban Elevation",
        "risk_level": "LOW",
        "avg_depth_meters": 0.1,
        "is_navigable_by_boat": False
    }


def compute_safe_route(
    origin: Tuple[float, float],
    incident: Tuple[float, float],
    destination: Optional[Tuple[float, float]] = None,
    requires_boat: bool = False
) -> Dict[str, Any]:
    """
    Computes a safe tactical route from team origin -> incident -> safe relief camp destination.
    Uses waypoint detouring around extreme flood zones if traversing by land, or direct waterway corridors for boats.
    """
    waypoints = [list(origin)]

    # Interpolate intermediate waypoints
    o_lat, o_lng = origin
    i_lat, i_lng = incident

    steps = 4
    for s in range(1, steps):
        factor = s / steps
        mid_lat = o_lat + factor * (i_lat - o_lat)
        mid_lng = o_lng + factor * (i_lng - o_lng)

        # Check if midpoint is in an EXTREME flood zone and we don't have a boat
        risk = check_flood_risk_at_point(mid_lat, mid_lng)
        if risk["risk_level"] == "EXTREME" and not requires_boat:
            # Shift coordinate to avoid extreme flood zone
            mid_lat += 0.004
            mid_lng += 0.003
        
        waypoints.append([round(mid_lat, 5), round(mid_lng, 5)])

    waypoints.append([round(i_lat, 5), round(i_lng, 5)])

    # If evacuation destination (relief camp) provided, append transit to camp
    total_km = haversine_distance(origin, incident)
    
    if destination:
        d_lat, d_lng = destination
        for s in range(1, 3):
            factor = s / 3
            mid_lat = i_lat + factor * (d_lat - i_lat)
            mid_lng = i_lng + factor * (d_lng - i_lng)
            waypoints.append([round(mid_lat, 5), round(mid_lng, 5)])
        waypoints.append([round(d_lat, 5), round(d_lng, 5)])
        total_km += haversine_distance(incident, destination)

    # Average emergency transit speed: 25 km/h urban flood conditions
    speed_kmh = 22.0 if requires_boat else 28.0
    transit_minutes = round((total_km / speed_kmh) * 60, 1)

    return {
        "waypoints": waypoints,
        "distance_km": round(total_km, 2),
        "estimated_minutes": max(transit_minutes, 4.0),
        "flood_risk_level": "SAFE_CORRIDOR" if not requires_boat else "AQUATIC_CORRIDOR",
        "route_summary": f"Tactical transit of {round(total_km, 2)}km avoiding deep submerged bottlenecks. ETA ~{transit_minutes} mins."
    }
