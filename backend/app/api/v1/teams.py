from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.database.models import Team
from app.core.event_bus import event_bus

router = APIRouter(prefix="/teams", tags=["Rescue Teams"])


class TeamStatusUpdate(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "AVAILABLE"})  # AVAILABLE, DISPATCHED, ON_MISSION, RETURNING


class TeamLocationUpdate(BaseModel):
    latitude: float
    longitude: float


@router.get("")
async def list_teams(
    status: Optional[str] = Query(None),
    agency: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all emergency response teams with their equipment profiles and locations."""
    query = select(Team)
    if status:
        query = query.filter_by(status=status)
    if agency:
        query = query.filter_by(agency=agency)

    result = await db.execute(query)
    teams = result.scalars().all()

    return [
        {
            "id": t.id,
            "callsign": t.callsign,
            "agency": t.agency,
            "status": t.status,
            "latitude": t.latitude,
            "longitude": t.longitude,
            "base_station": t.base_station,
            "personnel_count": t.personnel_count,
            "boats_count": t.boats_count,
            "medical_kits": t.medical_kits,
            "drones_count": t.drones_count,
            "amphibious_vehicles": t.amphibious_vehicles,
            "contact_radio": t.contact_radio,
            "current_incident_id": t.current_incident_id,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None
        }
        for t in teams
    ]


@router.get("/{team_id}")
async def get_team(team_id: str, db: AsyncSession = Depends(get_db)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return {
        "id": team.id,
        "callsign": team.callsign,
        "agency": team.agency,
        "status": team.status,
        "latitude": team.latitude,
        "longitude": team.longitude,
        "base_station": team.base_station,
        "personnel_count": team.personnel_count,
        "boats_count": team.boats_count,
        "medical_kits": team.medical_kits,
        "drones_count": team.drones_count,
        "amphibious_vehicles": team.amphibious_vehicles,
        "contact_radio": team.contact_radio,
        "current_incident_id": team.current_incident_id
    }


@router.patch("/{team_id}/status")
async def update_team_status(team_id: str, payload: TeamStatusUpdate, db: AsyncSession = Depends(get_db)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    team.status = payload.status
    if payload.status == "AVAILABLE":
        team.current_incident_id = None

    await db.commit()
    await event_bus.publish("TEAM_STATUS_CHANGED", {
        "team_id": team_id,
        "status": payload.status
    })

    return {"message": f"Team {team_id} status updated to {payload.status}"}


@router.patch("/{team_id}/location")
async def update_team_location(team_id: str, payload: TeamLocationUpdate, db: AsyncSession = Depends(get_db)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    team.latitude = payload.latitude
    team.longitude = payload.longitude
    await db.commit()

    await event_bus.publish("TEAM_TELEMETRY_UPDATED", {
        "team_id": team_id,
        "latitude": payload.latitude,
        "longitude": payload.longitude
    })

    return {"message": f"Team {team_id} telemetry updated"}
