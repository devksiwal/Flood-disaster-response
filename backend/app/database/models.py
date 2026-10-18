from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="commander")  # admin, commander, field_responder, camp_coordinator
    full_name = Column(String(100), default="EOC Duty Officer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(50), primary_key=True, index=True)
    raw_sos = Column(Text, nullable=False)
    caller_contact = Column(String(50), default="Citizen SOS Broadcast")
    title = Column(String(200), default="Unverified Waterlogging Incident")
    category = Column(String(50), default="FLASH_FLOOD")  # FLASH_FLOOD, STRANDED_RESIDENTS, STRUCTURAL_COLLAPSE, MEDICAL_URGENCY
    severity = Column(String(20), default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    priority_score = Column(Float, default=50.0)  # 0 to 100
    priority_level = Column(String(20), default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), default="REPORTED")  # REPORTED, TRIAGED, DISPATCHED, IN_PROGRESS, RESCUED, RESOLVED
    
    # Geolocation
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(255), default="Disaster Zone Sector")

    # Demographics & Conditions
    victim_count = Column(Integer, default=1)
    children_count = Column(Integer, default=0)
    elderly_count = Column(Integer, default=0)
    injured_count = Column(Integer, default=0)
    water_depth_meters = Column(Float, default=1.0)
    hazards_json = Column(Text, default="[]")  # JSON string list: ["ELECTRICAL_HAZARD", "FAST_CURRENT"]
    
    # Assigned Resources
    assigned_team_id = Column(String(50), nullable=True)
    assigned_camp_id = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class Team(Base):
    __tablename__ = "teams"

    id = Column(String(50), primary_key=True, index=True)
    callsign = Column(String(100), nullable=False)
    agency = Column(String(50), default="NDRF")  # NDRF, SDRF, COAST_GUARD, MEDICAL_CORPS, DRONE_RECON
    status = Column(String(30), default="AVAILABLE")  # AVAILABLE, DISPATCHED, ON_MISSION, RETURNING
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    base_station = Column(String(100), default="Central Disaster Response Hub")
    personnel_count = Column(Integer, default=12)
    boats_count = Column(Integer, default=2)
    medical_kits = Column(Integer, default=4)
    drones_count = Column(Integer, default=1)
    amphibious_vehicles = Column(Integer, default=1)
    contact_radio = Column(String(50), default="VHF-CH-16")
    current_incident_id = Column(String(50), nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class FloodSensor(Base):
    __tablename__ = "flood_sensors"

    id = Column(String(50), primary_key=True, index=True)
    station_code = Column(String(50), unique=True, index=True)
    station_name = Column(String(100), nullable=False)
    river_basin = Column(String(100), default="Brahmaputra Basin")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    water_level_meters = Column(Float, default=48.2)
    danger_mark_meters = Column(Float, default=50.0)
    warning_level_meters = Column(Float, default=49.0)
    trend = Column(String(20), default="RISING")  # RISING, STEADY, RECEDING
    rainfall_mm_last_3h = Column(Float, default=45.0)
    discharge_cusecs = Column(Float, default=65000.0)
    status = Column(String(20), default="WARNING")  # NORMAL, WARNING, CRITICAL
    last_ping = Column(DateTime, default=utcnow)


class ReliefCamp(Base):
    __tablename__ = "relief_camps"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    location_name = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    total_capacity = Column(Integer, default=500)
    current_occupancy = Column(Integer, default=180)
    available_beds = Column(Integer, default=320)
    food_packets = Column(Integer, default=1200)
    drinking_water_liters = Column(Integer, default=5000)
    doctors_on_site = Column(Integer, default=3)
    status = Column(String(20), default="OPEN")  # OPEN, FULL, STANDBY
    contact_person = Column(String(100), default="Camp Logistics Officer")
    phone = Column(String(50), default="+91-361-229011")


class RescueRoute(Base):
    __tablename__ = "rescue_routes"

    id = Column(String(50), primary_key=True, index=True)
    incident_id = Column(String(50), index=True, nullable=False)
    team_id = Column(String(50), index=True, nullable=False)
    camp_id = Column(String(50), nullable=True)
    waypoints_json = Column(Text, nullable=False)  # JSON array of [lat, lng]
    distance_km = Column(Float, default=4.5)
    estimated_minutes = Column(Float, default=12.0)
    flood_risk_level = Column(String(30), default="SAFE_CORRIDOR")  # SAFE_CORRIDOR, MODERATE_DETOUR, HAZARDOUS
    route_summary = Column(Text, default="Route computed avoiding critical flood zones.")
    status = Column(String(20), default="ACTIVE")  # ACTIVE, COMPLETED, REROUTED
    created_at = Column(DateTime, default=utcnow)


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(String(50), index=True, nullable=True)
    agent_name = Column(String(50), index=True, nullable=False)
    step = Column(String(100), nullable=False)
    thought = Column(Text, nullable=False)
    action = Column(String(100), nullable=False)
    input_payload = Column(Text, default="{}")
    output_payload = Column(Text, default="{}")
    confidence = Column(Float, default=0.95)
    execution_time_ms = Column(Float, default=120.0)
    created_at = Column(DateTime, default=utcnow)
