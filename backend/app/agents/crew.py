import json
import asyncio
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.logger import logger
from app.core.event_bus import event_bus
from app.agents.base import SharedDisasterMemory
from app.agents.emergency_detection import EmergencyDetectionAgent
from app.agents.priority import PriorityAgent
from app.agents.resource_allocation import ResourceAllocationAgent
from app.agents.route_planning import RoutePlanningAgent
from app.agents.relief_camp_logistics import ReliefCampLogisticsAgent
from app.agents.communication import CommunicationAgent
from app.database.models import Incident, Team, RescueRoute, AgentLog, ReliefCamp

# Optional CrewAI imports if installed in environment
try:
    from crewai import Agent as CrewAIAgent, Task as CrewAITask, Crew as CrewAICrew, Process as CrewAIProcess
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False


def create_crewai_crew(incident_raw_sos: str):
    """
    CrewAI declarative definition of the 5 Disaster Response Agents and Tasks.
    Complies with official CrewAI syntax and multi-agent hierarchical orchestration.
    """
    if not CREWAI_AVAILABLE:
        return None

    # 1. Emergency Detection Agent
    detection_agent = CrewAIAgent(
        role="Emergency Detection & NLP Incident Extraction Officer",
        goal="Extract structured situational incident data from unstructured citizen distress transmissions.",
        backstory="Veteran disaster communications specialist trained to decipher frantic emergency transmissions under stress.",
        verbose=True,
        allow_delegation=False
    )

    # 2. Priority Agent
    priority_agent = CrewAIAgent(
        role="Disaster Priority & Multi-Criteria Triage Specialist",
        goal="Calculate mathematical priority scores using water depth, vulnerability, and environmental hazards.",
        backstory="Former military disaster analyst specialized in triage prioritization under limited resource constraints.",
        verbose=True,
        allow_delegation=False
    )

    # 3. Resource Allocation Agent
    resource_agent = CrewAIAgent(
        role="Disaster Logistics & Rescue Team Dispatch Commander",
        goal="Assign the most suitable and closest rescue battalion equipped with necessary gear.",
        backstory="National Disaster Response Force logistics commander with real-time visibility over fleet equipment manifests.",
        verbose=True,
        allow_delegation=False
    )

    # 4. Route Planning Agent
    route_agent = CrewAIAgent(
        role="Tactical GIS & Flood-Avoidant Pathfinding Navigator",
        goal="Calculate safe navigation corridors avoiding impassable submerged choke points.",
        backstory="Hydrographic geospatial engineer with expertise in urban flood simulations and emergency evacuation routing.",
        verbose=True,
        allow_delegation=False
    )

    # 5. Relief Camp & Supply Logistics Agent
    camp_logistics_agent = CrewAIAgent(
        role="Relief Camp Logistics & Humanitarian Supply Chain Commander",
        goal="Ensure emergency shelter capacity, calculate water/food/medical quotas, and execute supply rebalancing.",
        backstory="Veteran disaster humanitarian relief officer expert in Sphere Standards and shelter supply chain logistics.",
        verbose=True,
        allow_delegation=False
    )

    # 6. Communication Agent
    comm_agent = CrewAIAgent(
        role="Emergency Public Safety & Operations Communications Chief",
        goal="Broadcast synchronized alerts to citizens, field teams, DEOC operators, and relief shelters.",
        backstory="Civil defense communications officer responsible for multi-channel incident messaging and public alerts.",
        verbose=True,
        allow_delegation=False
    )

    # Tasks
    task1 = CrewAITask(
        description=f"Process raw SOS message: '{incident_raw_sos}'. Extract victims, water depth, coordinates, and hazards.",
        expected_output="Structured incident JSON object with validated situational entities.",
        agent=detection_agent
    )

    task2 = CrewAITask(
        description="Calculate multi-criteria priority score (0-100) and urgency SLA for the structured incident.",
        expected_output="Priority analysis with score, urgency class (CRITICAL/HIGH/MED/LOW), and dispatch SLA.",
        agent=priority_agent
    )

    task3 = CrewAITask(
        description="Evaluate fleet inventory and assign the closest capable rescue squad with matching boats and medical gear.",
        expected_output="Team assignment record with callsign, distance, and mission directives.",
        agent=resource_agent
    )

    task4 = CrewAITask(
        description="Plot safe navigation waypoints from team base to incident and designated safe relief camp.",
        expected_output="Safe corridor waypoint coordinates and ETA avoiding high flood risk sectors.",
        agent=route_agent
    )

    task5 = CrewAITask(
        description="Calculate shelter intake quota, bed assignments, food rations, drinking water requirements, and supply rebalancing.",
        expected_output="Relief shelter allocation manifest with supply inventory updates and emergency requisitions.",
        agent=camp_logistics_agent
    )

    task6 = CrewAITask(
        description="Synthesize multi-channel alerts: Citizen SMS, Team Tactical Order, DEOC SITREP, and Camp Intake Advisory.",
        expected_output="Broadcast alert packages for all 4 emergency channels.",
        agent=comm_agent
    )

    crew = CrewAICrew(
        agents=[detection_agent, priority_agent, resource_agent, route_agent, camp_logistics_agent, comm_agent],
        tasks=[task1, task2, task3, task4, task5, task6],
        process=CrewAIProcess.sequential,
        verbose=2
    )

    return crew


class AutonomousDisasterOrchestrator:
    """
    Main Multi-Agent Orchestrator.
    Executes the 6 agents sequentially with shared memory, persists state transactionally,
    and streams live agent step logs over the WebSocket event bus.
    """

    def __init__(self):
        self.emergency_detector = EmergencyDetectionAgent()
        self.priority_evaluator = PriorityAgent()
        self.resource_allocator = ResourceAllocationAgent()
        self.route_planner = RoutePlanningAgent()
        self.camp_logistics = ReliefCampLogisticsAgent()
        self.communicator = CommunicationAgent()

    async def run_pipeline(self, incident_input: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Run the end-to-end 5-agent disaster response pipeline."""
        memory = SharedDisasterMemory()

        # Preload teams from DB into shared memory
        result = await db.execute(select(Team))
        teams = result.scalars().all()
        for t in teams:
            memory.teams[t.id] = {
                "id": t.id,
                "callsign": t.callsign,
                "agency": t.agency,
                "status": t.status,
                "latitude": t.latitude,
                "longitude": t.longitude,
                "boats_count": t.boats_count,
                "amphibious_vehicles": t.amphibious_vehicles,
                "medical_kits": t.medical_kits,
                "drones_count": t.drones_count,
                "contact_radio": t.contact_radio,
            }

        # Preload relief camps
        camps_res = await db.execute(select(ReliefCamp))
        camps = camps_res.scalars().all()
        memory.camps = {
            c.id: {
                "id": c.id,
                "name": c.name,
                "latitude": c.latitude,
                "longitude": c.longitude,
                "available_beds": c.available_beds,
                "status": c.status
            }
            for c in camps
        }

        # Notify pipeline start
        incident_id = incident_input.get("id")
        await event_bus.publish("PIPELINE_STARTED", {
            "incident_id": incident_id,
            "raw_sos": incident_input.get("raw_sos"),
            "status": "INITIATING_AGENTS"
        })

        # --- STEP 1: Emergency Detection Agent ---
        step1_res = await self.emergency_detector.execute(incident_input, memory)
        await event_bus.publish("AGENT_STEP_COMPLETED", memory.logs[-1])
        await asyncio.sleep(0.05)

        # --- STEP 2: Priority Agent ---
        step2_res = await self.priority_evaluator.execute(step1_res, memory)
        await event_bus.publish("AGENT_STEP_COMPLETED", memory.logs[-1])
        await asyncio.sleep(0.05)

        # --- STEP 3: Resource Allocation Agent ---
        step3_res = await self.resource_allocator.execute(step2_res, memory)
        await event_bus.publish("AGENT_STEP_COMPLETED", memory.logs[-1])
        await asyncio.sleep(0.05)

        # --- STEP 4: Route Planning Agent ---
        step4_res = await self.route_planner.execute(step3_res, memory)
        await event_bus.publish("AGENT_STEP_COMPLETED", memory.logs[-1])
        await asyncio.sleep(0.05)

        # --- STEP 5: Relief Camp Logistics Agent ---
        step5_res = await self.camp_logistics.execute(step4_res, memory)
        await event_bus.publish("AGENT_STEP_COMPLETED", memory.logs[-1])
        await asyncio.sleep(0.05)

        # --- STEP 6: Communication Agent ---
        step6_res = await self.communicator.execute(step5_res, memory)
        await event_bus.publish("AGENT_STEP_COMPLETED", memory.logs[-1])

        # --- PERSIST RESULTS TO DATABASE ---
        final_incident_data = memory.incidents[incident_id]
        final_route_data = memory.routes.get(f"ROUTE-{incident_id}")

        # 1. Update or Insert Incident in DB
        db_inc = await db.get(Incident, incident_id)
        if not db_inc:
            db_inc = Incident(id=incident_id, raw_sos=final_incident_data.get("raw_sos", ""))
            db.add(db_inc)

        db_inc.title = final_incident_data.get("title", db_inc.title)
        db_inc.category = final_incident_data.get("category", db_inc.category)
        db_inc.severity = final_incident_data.get("severity", db_inc.severity)
        db_inc.priority_score = final_incident_data.get("priority_score", 50.0)
        db_inc.priority_level = final_incident_data.get("priority_level", "HIGH")
        db_inc.status = "DISPATCHED"
        db_inc.latitude = final_incident_data.get("latitude")
        db_inc.longitude = final_incident_data.get("longitude")
        db_inc.location_name = final_incident_data.get("location_name")
        db_inc.victim_count = final_incident_data.get("victim_count", 1)
        db_inc.children_count = final_incident_data.get("children_count", 0)
        db_inc.elderly_count = final_incident_data.get("elderly_count", 0)
        db_inc.injured_count = final_incident_data.get("injured_count", 0)
        db_inc.water_depth_meters = final_incident_data.get("water_depth_meters", 1.0)
        db_inc.hazards_json = json.dumps(final_incident_data.get("hazards", []))
        db_inc.assigned_team_id = final_incident_data.get("assigned_team_id")
        db_inc.assigned_camp_id = final_incident_data.get("assigned_camp_id")

        # 2. Update Team in DB
        if db_inc.assigned_team_id:
            assigned_team = await db.get(Team, db_inc.assigned_team_id)
            if assigned_team:
                assigned_team.status = "DISPATCHED"
                assigned_team.current_incident_id = incident_id

        # 3. Insert or Update Rescue Route in DB
        if final_route_data:
            existing_route = await db.get(RescueRoute, final_route_data["id"])
            if not existing_route:
                new_route = RescueRoute(
                    id=final_route_data["id"],
                    incident_id=incident_id,
                    team_id=final_route_data["team_id"],
                    camp_id=final_route_data.get("camp_id"),
                    waypoints_json=json.dumps(final_route_data["waypoints"]),
                    distance_km=final_route_data["distance_km"],
                    estimated_minutes=final_route_data["estimated_minutes"],
                    flood_risk_level=final_route_data["flood_risk_level"],
                    route_summary=final_route_data["route_summary"],
                    status="ACTIVE"
                )
                db.add(new_route)
            else:
                existing_route.team_id = final_route_data["team_id"]
                existing_route.camp_id = final_route_data.get("camp_id")
                existing_route.waypoints_json = json.dumps(final_route_data["waypoints"])
                existing_route.distance_km = final_route_data["distance_km"]
                existing_route.estimated_minutes = final_route_data["estimated_minutes"]
                existing_route.flood_risk_level = final_route_data["flood_risk_level"]
                existing_route.route_summary = final_route_data["route_summary"]
                existing_route.status = "ACTIVE"


        # 4. Save Agent Logs in DB
        for l in memory.logs:
            db_log = AgentLog(
                incident_id=incident_id,
                agent_name=l["agent_name"],
                step=l["step"],
                thought=l["thought"],
                action=l["action"],
                input_payload=json.dumps(l["input_data"]),
                output_payload=json.dumps(l["output_data"]),
                confidence=l["confidence"],
                execution_time_ms=l["execution_time_ms"]
            )
            db.add(db_log)

        await db.commit()

        # 5. Update Camp Occupancy in DB
        if db_inc.assigned_camp_id:
            camp_record = await db.get(ReliefCamp, db_inc.assigned_camp_id)
            if camp_record:
                allocated = final_incident_data.get("camp_allocation", {}).get("allocated_beds", db_inc.victim_count)
                camp_record.current_occupancy = min(camp_record.total_capacity, camp_record.current_occupancy + allocated)
                camp_record.available_beds = max(0, camp_record.total_capacity - camp_record.current_occupancy)

        await db.commit()

        # Broadcast pipeline finished event
        await event_bus.publish("PIPELINE_COMPLETED", {
            "incident_id": incident_id,
            "incident": final_incident_data,
            "assigned_team": memory.teams.get(db_inc.assigned_team_id),
            "route": final_route_data,
            "camp_allocation": final_incident_data.get("camp_allocation"),
            "notifications": step6_res.get("notifications")
        })

        return {
            "incident": final_incident_data,
            "team": memory.teams.get(db_inc.assigned_team_id),
            "route": final_route_data,
            "camp_allocation": final_incident_data.get("camp_allocation"),
            "notifications": step6_res.get("notifications"),
            "agent_logs": memory.logs
        }


# Global orchestrator singleton
orchestrator = AutonomousDisasterOrchestrator()
