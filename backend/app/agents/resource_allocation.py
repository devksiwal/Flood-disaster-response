import time
from typing import Dict, Any, List
from app.agents.base import BaseDisasterAgent, SharedDisasterMemory
from app.services.gis_service import haversine_distance


class ResourceAllocationAgent(BaseDisasterAgent):
    """
    Agent 3: Resource Allocation Agent
    Matches triaged incidents with the optimal available rescue team based on capability, proximity, and gear.
    """

    def __init__(self):
        super().__init__(
            name="Resource Allocation Agent",
            role="Emergency Response Logistics & Resource Commander",
            goal="Identify required rescue capabilities (amphibious, diving, medical, drone) and assign the closest capable rescue squad."
        )

    async def execute(self, state: Dict[str, Any], memory: SharedDisasterMemory) -> Dict[str, Any]:
        start_time = time.time()
        incident_id = state.get("id")
        incident = memory.incidents.get(incident_id, state)

        inc_lat = incident.get("latitude") or 26.155
        inc_lng = incident.get("longitude") or 91.745
        depth = incident.get("water_depth_meters", 1.0)
        injured = incident.get("injured_count", 0)
        category = incident.get("category", "")
        hazards = incident.get("hazards", [])

        # Identify required equipment flags
        requires_boats = depth >= 1.2 or "FAST_FLOWING_CURRENT" in hazards
        requires_medical = injured > 0 or category == "MEDICAL_URGENCY"
        requires_drones = "ROOF_EVACUATION_REQUIRED" in hazards or incident.get("priority_level") == "CRITICAL"

        thought = (
            f"Evaluating tactical requirements for Incident {incident_id}: "
            f"RequiresBoats={requires_boats}, RequiresMedical={requires_medical}, RequiresDrones={requires_drones}."
        )

        candidates = list(memory.teams.values())
        if not candidates:
            # Fallback mock team if memory is empty
            best_team = {
                "id": "TEAM-NDRF-01",
                "callsign": "NDRF 1st Aquatic Battalion (Alpha)",
                "agency": "NDRF",
                "status": "AVAILABLE",
                "latitude": 26.1602,
                "longitude": 91.7450,
                "boats_count": 5,
                "amphibious_vehicles": 2,
                "medical_kits": 8,
                "drones_count": 2,
                "contact_radio": "VHF-CH-16"
            }
            memory.teams[best_team["id"]] = best_team
            candidates = [best_team]

        scored_teams = []
        for team in candidates:
            t_lat = team.get("latitude", 26.15)
            t_lng = team.get("longitude", 91.75)
            dist_km = haversine_distance((t_lat, t_lng), (inc_lat, inc_lng))

            # Base score inversely proportional to distance (closer is better)
            score = 100.0 - min(dist_km * 8.0, 70.0)

            # Availability bonus
            if team.get("status") == "AVAILABLE":
                score += 30.0
            else:
                score -= 40.0

            # Equipment matching bonuses
            if requires_boats and team.get("boats_count", 0) > 0:
                score += 25.0
            if requires_medical and team.get("medical_kits", 0) >= 4:
                score += 25.0
            if requires_drones and team.get("drones_count", 0) > 0:
                score += 15.0
            if team.get("amphibious_vehicles", 0) > 0 and depth >= 1.0:
                score += 15.0

            scored_teams.append({
                "team": team,
                "distance_km": dist_km,
                "suitability_score": round(score, 1)
            })

        # Sort descending by suitability
        scored_teams.sort(key=lambda x: x["suitability_score"], reverse=True)
        selected_match = scored_teams[0]
        chosen_team = selected_match["team"]

        # Update Team and Incident state
        chosen_team["status"] = "DISPATCHED"
        chosen_team["current_incident_id"] = incident_id
        memory.teams[chosen_team["id"]] = chosen_team

        incident["assigned_team_id"] = chosen_team["id"]
        incident["assigned_team_callsign"] = chosen_team["callsign"]
        incident["status"] = "DISPATCHED"
        memory.incidents[incident_id] = incident

        exec_time = round((time.time() - start_time) * 1000, 1)
        action = "DISPATCH_RESCUE_TEAM"
        memory.log(
            agent_name=self.name,
            step="3. Resource Allocation & Team Dispatch",
            thought=f"{thought} Evaluated {len(candidates)} teams. Assigned {chosen_team['callsign']} (Distance: {selected_match['distance_km']}km, Suitability: {selected_match['suitability_score']}).",
            action=action,
            input_data={"incident_id": incident_id, "required_gear": ["BOATS" if requires_boats else "TRUCKS", "MEDICAL" if requires_medical else "PARAMEDIC"]},
            output_data={"assigned_team_id": chosen_team["id"], "distance_km": selected_match["distance_km"], "callsign": chosen_team["callsign"]},
            confidence=0.96,
            execution_time_ms=exec_time,
            incident_id=incident_id
        )

        return {
            "incident": incident,
            "assigned_team": chosen_team,
            "distance_km": selected_match["distance_km"]
        }
