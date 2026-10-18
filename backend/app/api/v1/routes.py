import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.connection import get_db
from app.database.models import RescueRoute

router = APIRouter(prefix="/routes", tags=["Tactical Route Planning"])


@router.get("")
async def list_routes(db: AsyncSession = Depends(get_db)):
    """Retrieve all computed tactical rescue and evacuation routes."""
    result = await db.execute(select(RescueRoute))
    routes = result.scalars().all()
    return [
        {
            "id": r.id,
            "incident_id": r.incident_id,
            "team_id": r.team_id,
            "camp_id": r.camp_id,
            "waypoints": json.loads(r.waypoints_json),
            "distance_km": r.distance_km,
            "estimated_minutes": r.estimated_minutes,
            "flood_risk_level": r.flood_risk_level,
            "route_summary": r.route_summary,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in routes
    ]


@router.get("/{incident_id}")
async def get_route_for_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RescueRoute).filter_by(incident_id=incident_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="No calculated route found for this incident")
    return {
        "id": r.id,
        "incident_id": r.incident_id,
        "team_id": r.team_id,
        "camp_id": r.camp_id,
        "waypoints": json.loads(r.waypoints_json),
        "distance_km": r.distance_km,
        "estimated_minutes": r.estimated_minutes,
        "flood_risk_level": r.flood_risk_level,
        "route_summary": r.route_summary,
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None
    }
