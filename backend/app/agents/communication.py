import time
from typing import Dict, Any
from app.agents.base import BaseDisasterAgent, SharedDisasterMemory
from app.services.notify_service import (
    generate_citizen_sms,
    generate_team_dispatch_order,
    generate_deoc_sitrep,
    generate_camp_intake_advisory
)


class CommunicationAgent(BaseDisasterAgent):
    """
    Agent 5: Communication Agent
    Generates multi-channel notifications across public safety, tactical responder dispatch,
    DEOC situational briefings, and relief shelter intake alerts.
    """

    def __init__(self):
        super().__init__(
            name="Communication Agent",
            role="Public Safety & Tactical Emergency Communications Officer",
            goal="Synthesize intelligence from all disaster response agents and broadcast synchronized, multi-channel alerts and operational directives."
        )

    async def execute(self, state: Dict[str, Any], memory: SharedDisasterMemory) -> Dict[str, Any]:
        start_time = time.time()
        incident = state.get("incident", {})
        incident_id = incident.get("id") or state.get("id")
        incident = memory.incidents.get(incident_id, incident)

        team = state.get("assigned_team") or memory.teams.get(incident.get("assigned_team_id"), {})
        route = state.get("route") or memory.routes.get(f"ROUTE-{incident_id}", {})
        
        camp = {
            "name": incident.get("assigned_camp_name", "Sarada Girls Higher Secondary School Camp"),
            "contact_person": "Dr. Ranjan Nath",
            "available_beds": 380
        }

        thought = (
            f"Synthesizing operational directives for Incident {incident_id}: "
            f"Broadcasting to 4 distinct emergency communication channels (Citizen SMS, VHF Tactical Order, DEOC SITREP, Camp Intake)."
        )

        eta = route.get("estimated_minutes", 10.0)

        # 1. Citizen SMS
        citizen_alert = generate_citizen_sms(incident, team, eta)

        # 2. Team Operational Order
        team_order = generate_team_dispatch_order(incident, team, route.get("route_summary", "Follow calculated safe waypoints."))

        # 3. DEOC SITREP
        deoc_sitrep = generate_deoc_sitrep(incident, team, camp)

        # 4. Camp Intake Advisory
        camp_advisory = generate_camp_intake_advisory(incident, camp)

        notifications = {
            "citizen_sms": citizen_alert,
            "team_dispatch_order": team_order,
            "deoc_sitrep": deoc_sitrep,
            "camp_advisory": camp_advisory,
            "channels_broadcasted": ["SMS_PUBLIC", "VHF_RADIO_OPS", "DEOC_TERMINAL", "CAMP_LOGISTICS"],
            "dispatched_at": time.strftime("%Y-%m-%d %H:%M:%S UTC")
        }

        incident["notifications"] = notifications
        memory.incidents[incident_id] = incident

        exec_time = round((time.time() - start_time) * 1000, 1)
        action = "BROADCAST_EMERGENCY_ALERTS"
        memory.log(
            agent_name=self.name,
            step="5. Synchronized Multi-Channel Alert Dispatch",
            thought=f"{thought} Multi-channel alerts published successfully. Team ETA: {eta}m broadcast to victim and DEOC SITREP filed.",
            action=action,
            input_data={"incident_id": incident_id, "team_id": team.get("id")},
            output_data={"channels": notifications["channels_broadcasted"], "citizen_sms_chars": len(citizen_alert)},
            confidence=0.99,
            execution_time_ms=exec_time,
            incident_id=incident_id
        )


        return {
            "incident": incident,
            "assigned_team": team,
            "route": route,
            "notifications": notifications
        }
