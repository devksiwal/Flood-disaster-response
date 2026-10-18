import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.database.models import Incident, Team, RescueRoute
from app.agents.crew import orchestrator
from app.core.event_bus import event_bus

router = APIRouter(prefix="/incidents", tags=["Incident Management"])


class SOSSubmission(BaseModel):
    raw_sos: str = Field(..., json_schema_extra={"example": "Water reached 2nd floor in Bharalu riverbank. 4 children and grandmother trapped. Need boat immediately."})
    caller_contact: Optional[str] = "+91-98765-43210"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "RESCUED"})  # REPORTED, TRIAGED, DISPATCHED, IN_PROGRESS, RESCUED, RESOLVED


@router.get("")
async def list_incidents(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve disaster incidents with optional status or priority filtering."""
    query = select(Incident).order_by(desc(Incident.created_at)).limit(limit)
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority_level=priority)

    result = await db.execute(query)
    incidents = result.scalars().all()

    output = []
    for inc in incidents:
        output.append({
            "id": inc.id,
            "title": inc.title,
            "raw_sos": inc.raw_sos,
            "category": inc.category,
            "severity": inc.severity,
            "priority_score": inc.priority_score,
            "priority_level": inc.priority_level,
            "status": inc.status,
            "latitude": inc.latitude,
            "longitude": inc.longitude,
            "location_name": inc.location_name,
            "victim_count": inc.victim_count,
            "children_count": inc.children_count,
            "elderly_count": inc.elderly_count,
            "injured_count": inc.injured_count,
            "water_depth_meters": inc.water_depth_meters,
            "hazards": json.loads(inc.hazards_json) if inc.hazards_json else [],
            "assigned_team_id": inc.assigned_team_id,
            "assigned_camp_id": inc.assigned_camp_id,
            "created_at": inc.created_at.isoformat() if inc.created_at else None,
        })
    return output


@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve detailed situational view of an incident including assigned team and route."""
    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    team = None
    if incident.assigned_team_id:
        team_obj = await db.get(Team, incident.assigned_team_id)
        if team_obj:
            team = {
                "id": team_obj.id,
                "callsign": team_obj.callsign,
                "agency": team_obj.agency,
                "status": team_obj.status,
                "latitude": team_obj.latitude,
                "longitude": team_obj.longitude,
                "boats_count": team_obj.boats_count,
                "amphibious_vehicles": team_obj.amphibious_vehicles,
                "contact_radio": team_obj.contact_radio,
            }

    route_res = await db.execute(select(RescueRoute).filter_by(incident_id=incident_id))
    route_obj = route_res.scalars().first()
    route = None
    if route_obj:
        route = {
            "id": route_obj.id,
            "waypoints": json.loads(route_obj.waypoints_json),
            "distance_km": route_obj.distance_km,
            "estimated_minutes": route_obj.estimated_minutes,
            "flood_risk_level": route_obj.flood_risk_level,
            "route_summary": route_obj.route_summary,
            "status": route_obj.status,
        }

    return {
        "incident": {
            "id": incident.id,
            "title": incident.title,
            "raw_sos": incident.raw_sos,
            "category": incident.category,
            "severity": incident.severity,
            "priority_score": incident.priority_score,
            "priority_level": incident.priority_level,
            "status": incident.status,
            "latitude": incident.latitude,
            "longitude": incident.longitude,
            "location_name": incident.location_name,
            "victim_count": incident.victim_count,
            "children_count": incident.children_count,
            "elderly_count": incident.elderly_count,
            "injured_count": incident.injured_count,
            "water_depth_meters": incident.water_depth_meters,
            "hazards": json.loads(incident.hazards_json) if incident.hazards_json else [],
            "assigned_team_id": incident.assigned_team_id,
            "assigned_camp_id": incident.assigned_camp_id,
            "created_at": incident.created_at.isoformat() if incident.created_at else None,
        },
        "assigned_team": team,
        "route": route
    }


@router.post("/sos")
async def submit_sos(data: SOSSubmission, db: AsyncSession = Depends(get_db)):
    """
    Intake citizen / EOC raw SOS message.
    Instantly triggers the 5-Agent CrewAI pipeline to triage, prioritize, allocate team, and compute safe route!
    """
    incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"

    incident_payload = {
        "id": incident_id,
        "raw_sos": data.raw_sos,
        "caller_contact": data.caller_contact,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "location_name": data.location_name,
    }

    # Execute Autonomous Multi-Agent Pipeline
    pipeline_result = await orchestrator.run_pipeline(incident_payload, db)

    return {
        "status": "PROCESSED_BY_MULTI_AGENT_SYSTEM",
        "incident_id": incident_id,
        "result": pipeline_result
    }


@router.patch("/{incident_id}/status")
async def update_incident_status(incident_id: str, payload: StatusUpdate, db: AsyncSession = Depends(get_db)):
    """Update incident progression status (e.g. IN_PROGRESS, RESCUED, RESOLVED)."""
    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = payload.status
    if payload.status in ["RESCUED", "RESOLVED"] and incident.assigned_team_id:
        team = await db.get(Team, incident.assigned_team_id)
        if team and team.current_incident_id == incident_id:
            team.status = "AVAILABLE"
            team.current_incident_id = None
            await event_bus.publish("TEAM_STATUS_CHANGED", {
                "team_id": team.id,
                "status": "AVAILABLE"
            })

    await db.commit()

    await event_bus.publish("INCIDENT_STATUS_CHANGED", {
        "incident_id": incident_id,
        "status": payload.status
    })

    return {"message": f"Incident {incident_id} status updated to {payload.status}"}
