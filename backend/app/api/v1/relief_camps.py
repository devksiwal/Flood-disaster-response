from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.database.models import ReliefCamp
from app.core.event_bus import event_bus

router = APIRouter(prefix="/camps", tags=["Relief Camp Operations"])


class CampIntakeUpdate(BaseModel):
    admit_evacuees: int = Field(default=0)
    food_packets_delta: int = Field(default=0)


@router.get("")
async def list_camps(db: AsyncSession = Depends(get_db)):
    """Retrieve all safe relief shelters, occupancy rates, and logistics inventory."""
    result = await db.execute(select(ReliefCamp))
    camps = result.scalars().all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "location_name": c.location_name,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "total_capacity": c.total_capacity,
            "current_occupancy": c.current_occupancy,
            "available_beds": c.available_beds,
            "occupancy_rate_percent": round((c.current_occupancy / c.total_capacity) * 100, 1) if c.total_capacity > 0 else 0,
            "food_packets": c.food_packets,
            "drinking_water_liters": c.drinking_water_liters,
            "doctors_on_site": c.doctors_on_site,
            "status": c.status,
            "contact_person": c.contact_person,
            "phone": c.phone
        }
        for c in camps
    ]


@router.patch("/{camp_id}/intake")
async def admit_evacuees(camp_id: str, payload: CampIntakeUpdate, db: AsyncSession = Depends(get_db)):
    """Record evacuee arrival and adjust bed and ration balances."""
    camp = await db.get(ReliefCamp, camp_id)
    if not camp:
        raise HTTPException(status_code=404, detail="Relief camp not found")

    camp.current_occupancy += payload.admit_evacuees
    camp.available_beds = max(0, camp.total_capacity - camp.current_occupancy)
    camp.food_packets += payload.food_packets_delta

    if camp.available_beds == 0:
        camp.status = "FULL"
    else:
        camp.status = "OPEN"

    await db.commit()

    await event_bus.publish("CAMP_OCCUPANCY_CHANGED", {
        "camp_id": camp_id,
        "name": camp.name,
        "current_occupancy": camp.current_occupancy,
        "available_beds": camp.available_beds,
        "status": camp.status
    })

    return {
        "message": f"Recorded {payload.admit_evacuees} evacuees at {camp.name}",
        "new_occupancy": camp.current_occupancy,
        "available_beds": camp.available_beds,
        "status": camp.status
    }
