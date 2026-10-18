import pytest
import asyncio
from app.agents.base import SharedDisasterMemory
from app.agents.emergency_detection import EmergencyDetectionAgent
from app.agents.priority import PriorityAgent
from app.agents.resource_allocation import ResourceAllocationAgent
from app.agents.route_planning import RoutePlanningAgent
from app.agents.communication import CommunicationAgent
from app.services.gis_service import haversine_distance, compute_safe_route, point_in_polygon


@pytest.mark.asyncio
async def test_emergency_detection_agent():
    agent = EmergencyDetectionAgent()
    memory = SharedDisasterMemory()
    
    input_state = {
        "id": "INC-TEST-001",
        "raw_sos": "CRITICAL: 5 elderly patients and 2 children stranded on 2nd floor near Medical Hospital. Submerged electric wires sparking.",
        "latitude": 26.158,
        "longitude": 91.750,
        "location_name": "Medical Hospital Road"
    }

    result = await agent.execute(input_state, memory)
    assert result["id"] == "INC-TEST-001"
    assert result["category"] == "MEDICAL_URGENCY"
    assert result["victim_count"] >= 5
    assert result["elderly_count"] >= 1
    assert result["water_depth_meters"] >= 2.0
    assert "ELECTRICAL_WIRES_SUBMERGED" in result["hazards"]
    assert "INC-TEST-001" in memory.incidents


@pytest.mark.asyncio
async def test_priority_agent():
    agent = PriorityAgent()
    memory = SharedDisasterMemory()
    memory.incidents["INC-TEST-001"] = {
        "id": "INC-TEST-001",
        "water_depth_meters": 2.5,
        "victim_count": 8,
        "elderly_count": 3,
        "children_count": 2,
        "injured_count": 1,
        "hazards": ["ELECTRICAL_WIRES_SUBMERGED", "STRUCTURAL_INSTABILITY"]
    }

    result = await agent.execute({"id": "INC-TEST-001"}, memory)
    assert result["priority_score"] >= 80.0
    assert result["priority_level"] == "CRITICAL"
    assert result["sla_minutes"] == 15


@pytest.mark.asyncio
async def test_resource_allocation_agent():
    agent = ResourceAllocationAgent()
    memory = SharedDisasterMemory()
    memory.incidents["INC-TEST-001"] = {
        "id": "INC-TEST-001",
        "latitude": 26.160,
        "longitude": 91.745,
        "water_depth_meters": 2.2,
        "injured_count": 2,
        "category": "FLASH_FLOOD",
        "hazards": ["FAST_FLOWING_CURRENT"],
        "priority_level": "CRITICAL"
    }
    memory.teams["TEAM-ALPHA"] = {
        "id": "TEAM-ALPHA",
        "callsign": "NDRF Inflatable Boat Squad",
        "status": "AVAILABLE",
        "latitude": 26.162,
        "longitude": 91.747,
        "boats_count": 4,
        "medical_kits": 6,
        "drones_count": 1,
        "amphibious_vehicles": 2
    }

    result = await agent.execute({"id": "INC-TEST-001"}, memory)
    assert result["assigned_team"]["id"] == "TEAM-ALPHA"
    assert result["assigned_team"]["status"] == "DISPATCHED"


def test_gis_calculations():
    # Test distance
    d = haversine_distance((26.16, 91.74), (26.17, 91.75))
    assert d > 0.0 and d < 10.0

    # Test route generator
    route = compute_safe_route((26.16, 91.74), (26.165, 91.748), (26.17, 91.76))
    assert len(route["waypoints"]) >= 5
    assert route["distance_km"] > 0
    assert route["estimated_minutes"] > 0


@pytest.mark.asyncio
async def test_relief_camp_logistics_agent():
    from app.agents.relief_camp_logistics import ReliefCampLogisticsAgent
    agent = ReliefCampLogisticsAgent()
    memory = SharedDisasterMemory()
    memory.camps["CAMP-01"] = {
        "id": "CAMP-01",
        "name": "Sarada Girls Higher Secondary School Camp",
        "total_capacity": 500,
        "current_occupancy": 150,
        "available_beds": 350,
        "food_packets": 1000,
        "drinking_water_liters": 4000,
        "doctors_on_site": 3,
        "status": "OPEN"
    }
    input_incident = {
        "id": "INC-TEST-001",
        "victim_count": 10,
        "elderly_count": 2,
        "children_count": 3,
        "injured_count": 1,
        "assigned_camp_id": "CAMP-01",
        "assigned_camp_name": "Sarada Girls Higher Secondary School Camp"
    }
    result = await agent.execute({"incident": input_incident}, memory)
    alloc = result["camp_allocation"]
    assert alloc["camp_id"] == "CAMP-01"
    assert alloc["allocated_beds"] == 10
    assert alloc["allocated_water_liters"] == 40
    assert alloc["allocated_food_packets"] == 30
    assert "INC-TEST-001" in memory.camp_allocations
