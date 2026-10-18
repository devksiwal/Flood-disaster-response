import time
from typing import Dict, Any, List, Optional
from app.agents.base import BaseDisasterAgent, SharedDisasterMemory


class ReliefCampLogisticsAgent(BaseDisasterAgent):
    """
    Agent 5: Relief Camp & Supply Logistics Agent
    Specialized in shelter bed allocation, humanitarian supply budgeting (potable water,
    dry food rations, medical kits, pediatric/geriatric supplies), and dynamic supply rebalancing.
    """

    def __init__(self):
        super().__init__(
            name="Relief Camp Logistics Agent",
            role="Relief Camp Logistics & Humanitarian Supply Commander",
            goal="Manage emergency shelter intake, allocate beds, calculate humanitarian food/water/medical quotas, and execute inter-camp supply rebalancing."
        )

    async def execute(self, state: Dict[str, Any], memory: SharedDisasterMemory) -> Dict[str, Any]:
        start_time = time.time()
        incident_id = state.get("incident", {}).get("id") or state.get("id")
        incident = memory.incidents.get(incident_id, state.get("incident", state))

        victim_count = int(incident.get("victim_count") or 1)
        elderly_count = int(incident.get("elderly_count") or 0)
        children_count = int(incident.get("children_count") or 0)
        injured_count = int(incident.get("injured_count") or 0)

        assigned_camp_id = incident.get("assigned_camp_id") or "CAMP-01"
        camp = memory.camps.get(assigned_camp_id) if hasattr(memory, "camps") else None

        if not camp:
            # Fallback camp details if not loaded
            camp = {
                "id": assigned_camp_id,
                "name": incident.get("assigned_camp_name", "Primary Evacuation Relief Camp"),
                "total_capacity": 500,
                "current_occupancy": 180,
                "available_beds": 320,
                "food_packets": 1200,
                "drinking_water_liters": 5000,
                "doctors_on_site": 3,
                "status": "OPEN"
            }

        available_beds = camp.get("available_beds", 100)
        current_occupancy = camp.get("current_occupancy", 100)
        total_capacity = camp.get("total_capacity", 500)

        # Humanitarian Supply Standards (Sphere Standards)
        # Minimum 4 liters water / person / day
        # 3 ration packets / person / day
        water_req_liters = victim_count * 4
        food_req_packets = victim_count * 3
        medical_req = "URGENT_TRAUMA_TRIAGE" if injured_count > 0 else "ROUTINE_HEALTH_SCREEN"

        # Specialized supply requirements
        special_supplies = []
        if children_count > 0:
            special_supplies.append(f"{children_count * 2} Pediatric Hydration & Baby Formula Kits")
        if elderly_count > 0:
            special_supplies.append(f"{elderly_count} Mobility Assists & Chronic Illness Emergency Packs")
        if injured_count > 0:
            special_supplies.append(f"{injured_count} Trauma Dressings & IV Saline Units")

        # Capacity & Overflow Evaluation
        overflow_warning = False
        rebalance_order = None
        allocated_beds = min(victim_count, available_beds)

        if victim_count > available_beds:
            overflow_warning = True
            # Search for neighboring camp with remaining bed capacity
            overflow_camp = None
            if hasattr(memory, "camps"):
                for cid, c in memory.camps.items():
                    if cid != assigned_camp_id and c.get("available_beds", 0) >= victim_count:
                        overflow_camp = c
                        break

            if overflow_camp:
                rebalance_order = f"REROUTE_OVERFLOW to {overflow_camp['name']} (ID: {overflow_camp['id']}, Beds: {overflow_camp['available_beds']})"
            else:
                rebalance_order = "DEPLOY_EMERGENCY_WEATHERPROOF_TENTS (+50 Capacity At Camp Perimeter)"

        # Supply Depletion & Replenishment Checks
        supply_status = "OPTIMAL"
        supply_actions = []

        remaining_food = camp.get("food_packets", 1000) - food_req_packets
        remaining_water = camp.get("drinking_water_liters", 5000) - water_req_liters

        if remaining_food < 300:
            supply_actions.append("DISPATCH_CENTRAL_DEPOT_FOOD_TRUCK (+600 Dry Rations)")
            supply_status = "LOW_FOOD_ALERT"

        if remaining_water < 1500:
            supply_actions.append("DISPATCH_MOBILE_WATER_PURIFIER_TANKER (5000L)")
            supply_status = "CRITICAL_WATER_RESERVE"

        if injured_count > max(1, camp.get("doctors_on_site", 1) * 2):
            supply_actions.append("REQUEST_RAPID_MEDICAL_CORPS_PHYSICIANS (+2 Doctors)")

        utilization_pct = round(((current_occupancy + allocated_beds) / max(total_capacity, 1)) * 100, 1)

        allocation_manifest = {
            "camp_id": assigned_camp_id,
            "camp_name": camp.get("name"),
            "intake_evacuees": victim_count,
            "demographics": {
                "adults": max(0, victim_count - children_count - elderly_count),
                "children": children_count,
                "elderly": elderly_count,
                "injured": injured_count
            },
            "allocated_beds": allocated_beds,
            "allocated_water_liters": water_req_liters,
            "allocated_food_packets": food_req_packets,
            "medical_protocol": medical_req,
            "special_supplies": special_supplies,
            "camp_utilization_after": utilization_pct,
            "overflow_warning": overflow_warning,
            "supply_status": supply_status,
            "supply_actions": supply_actions,
            "rebalance_order": rebalance_order
        }

        # Store in Shared Memory
        if hasattr(memory, "camp_allocations"):
            memory.camp_allocations[incident_id] = allocation_manifest
        incident["camp_allocation"] = allocation_manifest
        memory.incidents[incident_id] = incident

        thought = (
            f"Relief Camp Logistics for Incident {incident_id} -> {camp.get('name')}: "
            f"Allocated {allocated_beds}/{victim_count} beds. Projected Occupancy: {utilization_pct}%. "
            f"Allocated {water_req_liters}L potable water, {food_req_packets} meal packets. "
            f"Supply Status: {supply_status}. Special Care: {len(special_supplies)} custom bundles prepared."
        )

        exec_time = round((time.time() - start_time) * 1000, 1)
        action = "ALLOCATE_CAMP_RESOURCES"
        memory.log(
            agent_name=self.name,
            step="5. Relief Shelter Intake & Supply Rebalancing",
            thought=thought,
            action=action,
            input_data={
                "camp_id": assigned_camp_id,
                "evacuees": victim_count,
                "special_needs": {"elderly": elderly_count, "children": children_count, "injured": injured_count}
            },
            output_data=allocation_manifest,
            confidence=0.98,
            execution_time_ms=exec_time,
            incident_id=incident_id
        )

        return {
            "incident": incident,
            "camp_allocation": allocation_manifest,
            "assigned_team": state.get("assigned_team") or memory.teams.get(incident.get("assigned_team_id")),
            "route": state.get("route") or memory.routes.get(f"ROUTE-{incident_id}")
        }
