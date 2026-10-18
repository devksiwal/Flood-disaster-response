import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class IncidentState(BaseModel):
    id: str
    raw_sos: str
    title: str = "Unclassified Incident"
    category: str = "FLASH_FLOOD"
    severity: str = "HIGH"
    priority_score: float = 50.0
    priority_level: str = "HIGH"
    status: str = "REPORTED"
    latitude: float
    longitude: float
    location_name: str
    victim_count: int = 1
    children_count: int = 0
    elderly_count: int = 0
    injured_count: int = 0
    water_depth_meters: float = 1.0
    hazards: List[str] = Field(default_factory=list)
    assigned_team_id: Optional[str] = None
    assigned_camp_id: Optional[str] = None


class SharedDisasterMemory:
    """
    Shared state across all 5 CrewAI agents:
    - Incidents
    - Teams
    - Flood Risk
    - Routes
    - Execution Trace Logs
    """

    def __init__(self):
        self.incidents: Dict[str, Dict[str, Any]] = {}
        self.teams: Dict[str, Dict[str, Any]] = {}
        self.flood_risk: Dict[str, Any] = {}
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.camps: Dict[str, Dict[str, Any]] = {}
        self.camp_allocations: Dict[str, Dict[str, Any]] = {}
        self.logs: List[Dict[str, Any]] = []

    def log(self, agent_name: str, step: str, thought: str, action: str, 
            input_data: Any = None, output_data: Any = None, confidence: float = 0.95, execution_time_ms: float = 100.0,
            incident_id: Optional[str] = None):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "incident_id": incident_id,
            "agent_name": agent_name,
            "step": step,
            "thought": thought,
            "action": action,
            "input_data": input_data,
            "output_data": output_data,
            "confidence": confidence,
            "execution_time_ms": execution_time_ms
        }
        self.logs.append(entry)
        return entry



class BaseDisasterAgent:
    """Abstract base class for all Disaster Response agents."""

    def __init__(self, name: str, role: str, goal: str):
        self.name = name
        self.role = role
        self.goal = goal

    async def execute(self, state: Dict[str, Any], memory: SharedDisasterMemory) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement execute()")
