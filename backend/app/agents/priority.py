import time
from typing import Dict, Any
from app.agents.base import BaseDisasterAgent, SharedDisasterMemory


class PriorityAgent(BaseDisasterAgent):
    """
    Agent 2: Priority Agent
    Calculates multi-criteria incident priority score and urgency classification.
    """

    def __init__(self):
        super().__init__(
            name="Priority Agent",
            role="Disaster Risk Assessment & MCDA Triage Commander",
            goal="Evaluate environmental risk, casualty vulnerability, water dynamics, and hazard multipliers to assign mathematical priority scores."
        )

    async def execute(self, state: Dict[str, Any], memory: SharedDisasterMemory) -> Dict[str, Any]:
        start_time = time.time()
        incident_id = state.get("id")
        incident = memory.incidents.get(incident_id, state)

        depth = incident.get("water_depth_meters", 1.0)
        victims = incident.get("victim_count", 1)
        children = incident.get("children_count", 0)
        elderly = incident.get("elderly_count", 0)
        injured = incident.get("injured_count", 0)
        hazards = incident.get("hazards", [])

        thought = (
            f"Computing MCDA Priority Score for incident {incident_id}. "
            f"Depth={depth}m, Victims={victims} (Eld={elderly}, Chd={children}, Inj={injured}), Hazards={len(hazards)}."
        )

        # 1. Water Depth Score (Max 30)
        if depth >= 2.5:
            depth_score = 30.0
        elif depth >= 1.5:
            depth_score = 22.0
        elif depth >= 0.8:
            depth_score = 14.0
        else:
            depth_score = 6.0

        # 2. Vulnerability Score (Max 40)
        vuln_score = 0.0
        vuln_score += min(elderly * 6.0, 18.0)
        vuln_score += min(children * 5.0, 15.0)
        vuln_score += min(injured * 10.0, 25.0)
        vuln_score += min(victims * 1.5, 12.0)
        vuln_score = min(vuln_score, 40.0)

        # 3. Hazard Multiplier Score (Max 30)
        hazard_score = 0.0
        hazard_weights = {
            "CRITICAL_OXYGEN_DEPLETION": 20.0,
            "STRUCTURAL_INSTABILITY": 18.0,
            "ELECTRICAL_WIRES_SUBMERGED": 15.0,
            "FAST_FLOWING_CURRENT": 12.0,
            "SUBMERGED_VEHICLE": 12.0,
            "ROOF_EVACUATION_REQUIRED": 8.0,
        }
        for h in hazards:
            hazard_score += hazard_weights.get(h, 5.0)
        hazard_score = min(hazard_score, 30.0)

        # Total Composite Score
        total_score = round(depth_score + vuln_score + hazard_score, 1)
        total_score = max(10.0, min(100.0, total_score))

        # Categorize
        if total_score >= 80.0:
            priority_level = "CRITICAL"
            severity = "CRITICAL"
            sla_minutes = 15
        elif total_score >= 60.0:
            priority_level = "HIGH"
            severity = "HIGH"
            sla_minutes = 30
        elif total_score >= 40.0:
            priority_level = "MEDIUM"
            severity = "MEDIUM"
            sla_minutes = 60
        else:
            priority_level = "LOW"
            severity = "LOW"
            sla_minutes = 120

        # Update Incident in Memory
        incident["priority_score"] = total_score
        incident["priority_level"] = priority_level
        incident["severity"] = severity
        incident["sla_minutes"] = sla_minutes
        incident["status"] = "TRIAGED"
        memory.incidents[incident_id] = incident

        exec_time = round((time.time() - start_time) * 1000, 1)
        action = "CALCULATE_PRIORITY"
        memory.log(
            agent_name=self.name,
            step="2. Multi-Criteria Priority Scoring",
            thought=f"{thought} Evaluated DepthScore={depth_score}, VulnScore={vuln_score}, HazardScore={hazard_score} => Total: {total_score} ({priority_level}).",
            action=action,
            input_data={"depth": depth, "victims": victims, "hazards": hazards},
            output_data={"score": total_score, "priority_level": priority_level, "sla_minutes": sla_minutes},
            confidence=0.98,
            execution_time_ms=exec_time,
            incident_id=incident_id
        )


        return incident
