import time
from typing import Dict, Any, List
from app.agents.base import BaseDisasterAgent, SharedDisasterMemory
from app.services.gis_service import compute_safe_route, haversine_distance


class RoutePlanningAgent(BaseDisasterAgent):
    """
    Agent 4: Route Planning Agent
    Calculates safe, flood-avoidant navigation routes from team base -> incident -> nearest safe relief camp.
    """

    def __init__(self):
        super().__init__(
            name="Route Planning Agent",
            role="Tactical Disaster GIS & Evacuation Pathfinding Specialist",
            goal="Identify navigable corridors, circumvent impassable inundated road segments, and chart fastest safe evacuation corridors."
        )

    async def execute(self, state: Dict[str, Any], memory: SharedDisasterMemory) -> Dict[str, Any]:
        start_time = time.time()
        incident_id = state.get("incident", {}).get("id") or state.get("id")
        incident = memory.incidents.get(incident_id, state)
        team = state.get("assigned_team") or memory.teams.get(incident.get("assigned_team_id"))

        if not team:
            team_coords = (26.1602, 91.7450)
            requires_boat = True
        else:
            team_coords = (team.get("latitude") or 26.16, team.get("longitude") or 91.74)
            requires_boat = (team.get("boats_count") or 0) > 0

        inc_coords = (incident.get("latitude") or 26.155, incident.get("longitude") or 91.745)

        # Select nearest safe relief camp from memory or default
        camp_coords = (26.1685, 91.7620)
        selected_camp_id = "CAMP-01"
        selected_camp_name = "Sarada Girls Higher Secondary School Camp"

        if hasattr(memory, "camps") and memory.camps:
            closest_dist = 9999.0
            for cid, c in memory.camps.items():
                c_dist = haversine_distance(inc_coords, (c["latitude"], c["longitude"]))
                if c_dist < closest_dist and c.get("status") == "OPEN":
                    closest_dist = c_dist
                    selected_camp_id = cid
                    selected_camp_name = c["name"]
                    camp_coords = (c["latitude"], c["longitude"])

        thought = (
            f"Pathfinding for Incident {incident_id}: "
            f"Origin={team_coords}, Target={inc_coords}, EvacuationDestination={camp_coords} ({selected_camp_name}). "
            f"RequiresAquaticNavigation={requires_boat}."
        )

        # Compute safe route
        route_data = compute_safe_route(
            origin=team_coords,
            incident=inc_coords,
            destination=camp_coords,
            requires_boat=requires_boat
        )

        route_id = f"ROUTE-{incident_id}"
        route_record = {
            "id": route_id,
            "incident_id": incident_id,
            "team_id": team.get("id") if team else "TEAM-NDRF-01",
            "camp_id": selected_camp_id,
            "camp_name": selected_camp_name,
            "waypoints": route_data["waypoints"],
            "distance_km": route_data["distance_km"],
            "estimated_minutes": route_data["estimated_minutes"],
            "flood_risk_level": route_data["flood_risk_level"],
            "route_summary": route_data["route_summary"],
            "status": "ACTIVE"
        }

        # Store in Shared Memory
        memory.routes[route_id] = route_record
        incident["assigned_camp_id"] = selected_camp_id
        incident["assigned_camp_name"] = selected_camp_name
        memory.incidents[incident_id] = incident

        exec_time = round((time.time() - start_time) * 1000, 1)
        action = "COMPUTE_SAFE_ROUTE"
        memory.log(
            agent_name=self.name,
            step="4. Safe Route Computation & Evacuation Corridors",
            thought=f"{thought} Safe corridor established. Distance: {route_data['distance_km']}km, ETA: {route_data['estimated_minutes']}m. Designated Evacuation Camp: {selected_camp_name}.",
            action=action,
            input_data={"origin": team_coords, "incident": inc_coords, "camp": camp_coords},
            output_data={"route_id": route_id, "distance_km": route_data["distance_km"], "eta_minutes": route_data["estimated_minutes"], "waypoints": len(route_data["waypoints"])},
            confidence=0.97,
            execution_time_ms=exec_time,
            incident_id=incident_id
        )

        return {
            "incident": incident,
            "assigned_team": team,
            "route": route_record
        }
