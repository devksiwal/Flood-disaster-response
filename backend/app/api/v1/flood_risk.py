from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.database.models import FloodSensor
from app.database.seed import FLOOD_RISK_ZONES
from app.core.event_bus import event_bus

router = APIRouter(prefix="/flood", tags=["Flood Risk & Hydrology Monitoring"])


class SensorTelemetryUpdate(BaseModel):
    water_level_meters: float = Field(..., json_schema_extra={"example": 50.8})
    trend: str = Field(..., json_schema_extra={"example": "RISING"})  # RISING, STEADY, RECEDING
    rainfall_mm_last_3h: float = Field(default=35.0)


@router.get("/sensors")
async def list_sensors(db: AsyncSession = Depends(get_db)):
    """Retrieve all river gauging stations and hydrologic sensors."""
    result = await db.execute(select(FloodSensor))
    sensors = result.scalars().all()
    return [
        {
            "id": s.id,
            "station_code": s.station_code,
            "station_name": s.station_name,
            "river_basin": s.river_basin,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "water_level_meters": s.water_level_meters,
            "danger_mark_meters": s.danger_mark_meters,
            "warning_level_meters": s.warning_level_meters,
            "trend": s.trend,
            "rainfall_mm_last_3h": s.rainfall_mm_last_3h,
            "discharge_cusecs": s.discharge_cusecs,
            "status": s.status,
            "last_ping": s.last_ping.isoformat() if s.last_ping else None
        }
        for s in sensors
    ]


@router.get("/zones")
async def get_flood_zones():
    """Retrieve flood risk polygon boundaries, water depth, and navigation status for Leaflet overlays."""
    return FLOOD_RISK_ZONES


@router.post("/sensor/{sensor_id}/telemetry")
async def update_sensor_telemetry(sensor_id: str, payload: SensorTelemetryUpdate, db: AsyncSession = Depends(get_db)):
    """Simulate or ingest river station telemetry reading."""
    sensor = await db.get(FloodSensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor station not found")

    sensor.water_level_meters = payload.water_level_meters
    sensor.trend = payload.trend
    sensor.rainfall_mm_last_3h = payload.rainfall_mm_last_3h

    # Re-evaluate status against danger mark
    if payload.water_level_meters >= sensor.danger_mark_meters:
        sensor.status = "CRITICAL"
    elif payload.water_level_meters >= sensor.warning_level_meters:
        sensor.status = "WARNING"
    else:
        sensor.status = "NORMAL"

    await db.commit()

    # Broadcast event
    await event_bus.publish("SENSOR_TELEMETRY_UPDATED", {
        "sensor_id": sensor_id,
        "station_name": sensor.station_name,
        "water_level_meters": payload.water_level_meters,
        "status": sensor.status,
        "trend": payload.trend
    })

    return {
        "message": f"Sensor {sensor_id} telemetry updated",
        "current_level": payload.water_level_meters,
        "status": sensor.status
    }
