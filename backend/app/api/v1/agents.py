import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database.connection import get_db
from app.database.models import Incident, AgentLog
from app.agents.crew import orchestrator, CREWAI_AVAILABLE
from app.core.config import settings

router = APIRouter(prefix="/agents", tags=["Agentic AI Framework"])


@router.get("/status")
async def get_agent_status():
    """Retrieve operational status and capabilities of the 5 CrewAI agents."""
    return {
        "engine_mode": settings.AI_ENGINE_MODE,
        "crewai_library_installed": CREWAI_AVAILABLE,
        "active_agents": [
            {
                "id": 1,
                "name": "Emergency Detection Agent",
                "role": "Disaster SOS Triage & NLP Classification Specialist",
                "status": "OPERATIONAL",
                "description": "Ingests raw SOS streams and extracts casualty count, depth, geolocation, and hazards."
            },
            {
                "id": 2,
                "name": "Priority Agent",
                "role": "Disaster Risk Assessment & MCDA Triage Commander",
                "status": "OPERATIONAL",
                "description": "Calculates multi-criteria priority score (0-100) based on water dynamics and casualty vulnerability."
            },
            {
                "id": 3,
                "name": "Resource Allocation Agent",
                "role": "Emergency Response Logistics & Resource Commander",
                "status": "OPERATIONAL",
                "description": "Matches incident with best available rescue team (NDRF, SDRF, Coast Guard, Medical)."
            },
            {
                "id": 4,
                "name": "Route Planning Agent",
                "role": "Tactical Disaster GIS & Evacuation Pathfinding Specialist",
                "status": "OPERATIONAL",
                "description": "Calculates safe transit corridors avoiding impassable inundated road segments."
            },
            {
                "id": 5,
                "name": "Relief Camp Logistics Agent",
                "role": "Relief Shelter Intake & Humanitarian Supply Commander",
                "status": "OPERATIONAL",
                "description": "Calculates shelter bed capacity, food rations, potable water quotas, and dynamic inter-camp supply rebalancing."
            },
            {
                "id": 6,
                "name": "Communication Agent",
                "role": "Public Safety & Tactical Emergency Communications Officer",
                "status": "OPERATIONAL",
                "description": "Dispatches multi-channel alerts across Citizen SMS, VHF Team Orders, and DEOC SITREPs."
            }
        ]
    }


@router.get("/logs")
async def get_agent_logs(
    incident_id: Optional[str] = Query(None),
    agent_name: Optional[str] = Query(None),
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve structured agent audit logs, thoughts, actions, and performance metrics."""
    query = select(AgentLog).order_by(desc(AgentLog.created_at)).limit(limit)
    if incident_id:
        query = query.filter_by(incident_id=incident_id)
    if agent_name:
        query = query.filter(AgentLog.agent_name.ilike(f"%{agent_name}%"))

    result = await db.execute(query)
    logs = result.scalars().all()

    output = []
    for l in logs:
        output.append({
            "id": l.id,
            "incident_id": l.incident_id,
            "agent_name": l.agent_name,
            "step": l.step,
            "thought": l.thought,
            "action": l.action,
            "input_payload": json.loads(l.input_payload) if l.input_payload else {},
            "output_payload": json.loads(l.output_payload) if l.output_payload else {},
            "confidence": l.confidence,
            "execution_time_ms": l.execution_time_ms,
            "created_at": l.created_at.isoformat() if l.created_at else None
        })
    return output


@router.post("/trigger/{incident_id}")
async def trigger_pipeline_for_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Manually re-run the 5-Agent multi-agent workflow for an existing incident."""
    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    payload = {
        "id": incident.id,
        "raw_sos": incident.raw_sos,
        "caller_contact": incident.caller_contact,
        "latitude": incident.latitude,
        "longitude": incident.longitude,
        "location_name": incident.location_name,
    }

    result = await orchestrator.run_pipeline(payload, db)
    return {
        "message": f"Autonomous multi-agent pipeline executed for incident {incident_id}",
        "result": result
    }
