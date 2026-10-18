import json
from datetime import datetime, timezone
from sqlalchemy import select
from app.database.connection import AsyncSessionLocal
from app.database.models import User, Team, FloodSensor, ReliefCamp, Incident, RescueRoute, AgentLog
from app.core.security import get_password_hash
from app.core.logger import logger

# Realistically defined flood zones for Guwahati / River Basin scenario
FLOOD_RISK_ZONES = [
    {
        "id": "ZONE-CRIT-01",
        "name": "Brahmaputra South Embankment Sector",
        "risk_level": "EXTREME",
        "avg_depth_meters": 2.8,
        "current_speed_knots": 4.5,
        "is_navigable_by_boat": True,
        "polygon": [
            [26.168, 91.730],
            [26.175, 91.750],
            [26.165, 91.765],
            [26.155, 91.745],
            [26.168, 91.730]
        ]
    },
    {
        "id": "ZONE-CRIT-02",
        "name": "Bharalu Urban Drainage Basin",
        "risk_level": "HIGH",
        "avg_depth_meters": 1.9,
        "current_speed_knots": 2.2,
        "is_navigable_by_boat": True,
        "polygon": [
            [26.150, 91.735],
            [26.160, 91.745],
            [26.145, 91.760],
            [26.138, 91.742],
            [26.150, 91.735]
        ]
    },
    {
        "id": "ZONE-MOD-03",
        "name": "Dispur Capitol Lowlands",
        "risk_level": "MODERATE",
        "avg_depth_meters": 0.8,
        "current_speed_knots": 0.8,
        "is_navigable_by_boat": False,
        "polygon": [
            [26.130, 91.775],
            [26.142, 91.785],
            [26.135, 91.805],
            [26.122, 91.790],
            [26.130, 91.775]
        ]
    },
    {
        "id": "ZONE-SAFE-04",
        "name": "Khanapara Plateau Green Zone",
        "risk_level": "SAFE",
        "avg_depth_meters": 0.05,
        "current_speed_knots": 0.0,
        "is_navigable_by_boat": False,
        "polygon": [
            [26.115, 91.810],
            [26.125, 91.825],
            [26.110, 91.835],
            [26.102, 91.818],
            [26.115, 91.810]
        ]
    }
]


async def seed_database():
    """Seed database with realistic initial scenario data."""
    async with AsyncSessionLocal() as session:
        # 1. Check if already seeded
        result = await session.execute(select(User))
        if result.scalars().first():
            logger.info("Database already contains data, skipping seed.")
            return

        logger.info("Seeding database with realistic National Disaster Response scenario...")

        # 2. Seed Users
        users = [
            User(
                username="admin",
                email="admin@ndma.gov.in",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                full_name="Col. R. Sharma (Director Operations)"
            ),
            User(
                username="commander",
                email="commander@ndma.gov.in",
                hashed_password=get_password_hash("commander123"),
                role="commander",
                full_name="Cmdr. Anita Sen (Duty Officer, State EOC)"
            ),
            User(
                username="responder",
                email="responder@ndrf.gov.in",
                hashed_password=get_password_hash("responder123"),
                role="field_responder",
                full_name="Inspector Vikram Singha (Team Lead Bravo)"
            ),
            User(
                username="coordinator",
                email="camp@disasterrelief.gov.in",
                hashed_password=get_password_hash("coordinator123"),
                role="camp_coordinator",
                full_name="Dr. P. Barman (Relief Center Superintendent)"
            ),
        ]
        session.add_all(users)

        # 3. Seed Teams
        teams = [
            Team(
                id="TEAM-NDRF-01",
                callsign="NDRF 1st Aquatic Battalion (Alpha)",
                agency="NDRF",
                status="AVAILABLE",
                latitude=26.1602,
                longitude=91.7450,
                base_station="Pandu River Command Depot",
                personnel_count=18,
                boats_count=5,
                medical_kits=8,
                drones_count=2,
                amphibious_vehicles=2,
                contact_radio="VHF-CH-16",
            ),
            Team(
                id="TEAM-SDRF-02",
                callsign="SDRF Urban Flood Strike Unit (Bravo)",
                agency="SDRF",
                status="AVAILABLE",
                latitude=26.1350,
                longitude=91.7705,
                base_station="Dispur Civil Defense Headquarters",
                personnel_count=14,
                boats_count=3,
                medical_kits=6,
                drones_count=1,
                amphibious_vehicles=1,
                contact_radio="VHF-CH-09",
            ),
            Team(
                id="TEAM-CG-03",
                callsign="Coast Guard Riverine Rescue Divers (Charlie)",
                agency="COAST_GUARD",
                status="AVAILABLE",
                latitude=26.1750,
                longitude=91.7200,
                base_station="Brahmaputra Naval Pier",
                personnel_count=12,
                boats_count=6,
                medical_kits=4,
                drones_count=2,
                amphibious_vehicles=0,
                contact_radio="MARITIME-CH-72",
            ),
            Team(
                id="TEAM-MED-04",
                callsign="Rapid Medical Corps Mobile Trauma Unit (Delta)",
                agency="MEDICAL_CORPS",
                status="AVAILABLE",
                latitude=26.1400,
                longitude=91.7300,
                base_station="Guwahati Medical College Post",
                personnel_count=10,
                boats_count=1,
                medical_kits=20,
                drones_count=1,
                amphibious_vehicles=2,
                contact_radio="MED-NET-01",
            ),
            Team(
                id="TEAM-DRONE-05",
                callsign="Air Reconnaissance & Drone Unit (Echo)",
                agency="DRONE_RECON",
                status="AVAILABLE",
                latitude=26.1550,
                longitude=91.7850,
                base_station="Khanapara Heliport Field Base",
                personnel_count=8,
                boats_count=0,
                medical_kits=2,
                drones_count=6,
                amphibious_vehicles=1,
                contact_radio="AIR-OPS-03",
            ),
            Team(
                id="TEAM-DEFENSE-06",
                callsign="Civil Defense Volunteers & Boat Crew (Foxtrot)",
                agency="CIVIL_DEFENSE",
                status="AVAILABLE",
                latitude=26.1200,
                longitude=91.7500,
                base_station="South Guwahati Municipal Yard",
                personnel_count=22,
                boats_count=4,
                medical_kits=5,
                drones_count=0,
                amphibious_vehicles=2,
                contact_radio="CIVIL-VHF-05",
            ),
        ]
        session.add_all(teams)

        # 4. Seed Flood Sensors
        sensors = [
            FloodSensor(
                id="STN-01",
                station_code="GHY-SARAIGHAT",
                station_name="Saraighat River Gauging Post",
                river_basin="Brahmaputra Main Stem",
                latitude=26.1780,
                longitude=91.7010,
                water_level_meters=50.35,
                danger_mark_meters=49.80,
                warning_level_meters=49.00,
                trend="RISING",
                rainfall_mm_last_3h=54.2,
                discharge_cusecs=78500.0,
                status="CRITICAL"
            ),
            FloodSensor(
                id="STN-02",
                station_code="GHY-PANDU",
                station_name="Pandu Port Hydrographic Station",
                river_basin="Brahmaputra Inner Channel",
                latitude=26.1660,
                longitude=91.7250,
                water_level_meters=49.92,
                danger_mark_meters=49.50,
                warning_level_meters=48.80,
                trend="RISING",
                rainfall_mm_last_3h=48.0,
                discharge_cusecs=69200.0,
                status="CRITICAL"
            ),
            FloodSensor(
                id="STN-03",
                station_code="GHY-BHARALU",
                station_name="Bharalu Sluice Outfall Gauge",
                river_basin="Bharalu Urban Stream",
                latitude=26.1550,
                longitude=91.7410,
                water_level_meters=51.10,
                danger_mark_meters=50.20,
                warning_level_meters=49.40,
                trend="RISING",
                rainfall_mm_last_3h=62.5,
                discharge_cusecs=12400.0,
                status="CRITICAL"
            ),
            FloodSensor(
                id="STN-04",
                station_code="GHY-UZANBAZAR",
                station_name="Uzanbazar Riverfront Station",
                river_basin="Brahmaputra Main Channel",
                latitude=26.1700,
                longitude=91.7580,
                water_level_meters=49.65,
                danger_mark_meters=49.70,
                warning_level_meters=48.90,
                trend="STEADY",
                rainfall_mm_last_3h=32.0,
                discharge_cusecs=64100.0,
                status="WARNING"
            ),
            FloodSensor(
                id="STN-05",
                station_code="GHY-DEEPOR",
                station_name="Deepor Beel Ramsar Inundation Gauge",
                river_basin="Deepor Basin Lowlands",
                latitude=26.1250,
                longitude=91.6850,
                water_level_meters=47.90,
                danger_mark_meters=48.50,
                warning_level_meters=47.50,
                trend="RISING",
                rainfall_mm_last_3h=28.5,
                discharge_cusecs=8200.0,
                status="WARNING"
            ),
            FloodSensor(
                id="STN-06",
                station_code="GHY-KHANAPARA",
                station_name="Khanapara Drainage Spillway",
                river_basin="Meghalaya Foothills Drainage",
                latitude=26.1180,
                longitude=91.8150,
                water_level_meters=46.20,
                danger_mark_meters=48.00,
                warning_level_meters=47.00,
                trend="RECEDING",
                rainfall_mm_last_3h=14.0,
                discharge_cusecs=4100.0,
                status="NORMAL"
            ),
        ]
        session.add_all(sensors)

        # 5. Seed Relief Camps
        camps = [
            ReliefCamp(
                id="CAMP-01",
                name="Sarada Girls Higher Secondary School Camp",
                location_name="Uzanbazar Elevated Sector",
                latitude=26.1685,
                longitude=91.7620,
                total_capacity=600,
                current_occupancy=220,
                available_beds=380,
                food_packets=1800,
                drinking_water_liters=6500,
                doctors_on_site=4,
                status="OPEN",
                contact_person="Dr. Ranjan Nath",
                phone="+91-361-229041"
            ),
            ReliefCamp(
                id="CAMP-02",
                name="IIT North Bank Transit Shelter Complex",
                location_name="North Guwahati High Ridge",
                latitude=26.1890,
                longitude=91.6920,
                total_capacity=1500,
                current_occupancy=480,
                available_beds=1020,
                food_packets=4200,
                drinking_water_liters=18000,
                doctors_on_site=9,
                status="OPEN",
                contact_person="Prof. K. Saikia (Camp Coordinator)",
                phone="+91-361-258200"
            ),
            ReliefCamp(
                id="CAMP-03",
                name="Dispur Indoor Sports Stadium Relief Hub",
                location_name="Dispur Capital District",
                latitude=26.1360,
                longitude=91.7940,
                total_capacity=850,
                current_occupancy=340,
                available_beds=510,
                food_packets=2400,
                drinking_water_liters=9000,
                doctors_on_site=5,
                status="OPEN",
                contact_person="Officer Meera Das",
                phone="+91-361-223701"
            ),
            ReliefCamp(
                id="CAMP-04",
                name="Jalukbari Higher Secondary Safe Campus",
                location_name="Jalukbari West Ridge",
                latitude=26.1480,
                longitude=91.7020,
                total_capacity=500,
                current_occupancy=110,
                available_beds=390,
                food_packets=1200,
                drinking_water_liters=4500,
                doctors_on_site=3,
                status="OPEN",
                contact_person="Superintendent B. Gogoi",
                phone="+91-361-257014"
            ),
            ReliefCamp(
                id="CAMP-05",
                name="Sonapur Government College Emergency Camp",
                location_name="Sonapur East Highland",
                latitude=26.1120,
                longitude=91.8250,
                total_capacity=700,
                current_occupancy=160,
                available_beds=540,
                food_packets=1900,
                drinking_water_liters=7200,
                doctors_on_site=3,
                status="OPEN",
                contact_person="Coordinator Pradip Hazarika",
                phone="+91-361-282033"
            ),
        ]
        session.add_all(camps)

        # 6. Seed Realistic Pre-existing Incidents
        incidents = [
            Incident(
                id="INC-2026-001",
                raw_sos="EMERGENCY: Riverside Care Hospital basement and ground floor inundated. 5 elderly patients and 2 nurses stranded. Water depth 2.2m and rising fast. Oxygen cylinder supplies running critically low. Urgent boat rescue needed.",
                caller_contact="+91-94350-11223",
                title="Hospital ICU Inundation & Medical Evacuation",
                category="MEDICAL_URGENCY",
                severity="CRITICAL",
                priority_score=94.5,
                priority_level="CRITICAL",
                status="DISPATCHED",
                latitude=26.1620,
                longitude=91.7480,
                location_name="Riverside Care Hospital, Bharalu Ghat",
                victim_count=7,
                children_count=0,
                elderly_count=5,
                injured_count=3,
                water_depth_meters=2.2,
                hazards_json=json.dumps(["ELECTRICAL_SUBMERGED", "RAPID_WATER_RISE", "CRITICAL_OXYGEN"]),
                assigned_team_id="TEAM-NDRF-01",
                assigned_camp_id="CAMP-01"
            ),
            Incident(
                id="INC-2026-002",
                raw_sos="SOS: School bus marooned in waterlogged underpass near Zoo Road. 12 schoolchildren and driver trapped inside bus. Water level at window level (1.6m). Children terrified. Need immediate evacuation.",
                caller_contact="+91-98640-77889",
                title="School Bus Trapped in Flooded Underpass",
                category="STRANDED_RESIDENTS",
                severity="CRITICAL",
                priority_score=91.0,
                priority_level="CRITICAL",
                status="DISPATCHED",
                latitude=26.1510,
                longitude=91.7690,
                location_name="Zoo Road Overpass Underbridge",
                victim_count=13,
                children_count=12,
                elderly_count=0,
                injured_count=1,
                water_depth_meters=1.6,
                hazards_json=json.dumps(["SUBMERGED_VEHICLE", "CHILDREN_AT_RISK"]),
                assigned_team_id="TEAM-SDRF-02",
                assigned_camp_id="CAMP-03"
            ),
            Incident(
                id="INC-2026-003",
                raw_sos="Help! Water reached 1st floor of 2-storey house in Anil Nagar. 4 family members including an 80yo grandmother on roof. Structural cracking sound heard. Water 1.8m outside.",
                caller_contact="+91-91270-44556",
                title="Residential Structural Instability & Roof Trapped Family",
                category="STRUCTURAL_COLLAPSE",
                severity="HIGH",
                priority_score=78.5,
                priority_level="HIGH",
                status="TRIAGED",
                latitude=26.1575,
                longitude=91.7610,
                location_name="Anil Nagar Lane 4, House 18",
                victim_count=4,
                children_count=1,
                elderly_count=1,
                injured_count=0,
                water_depth_meters=1.8,
                hazards_json=json.dumps(["STRUCTURAL_CRACKS", "ROOF_EVACUATION"]),
                assigned_team_id=None,
                assigned_camp_id="CAMP-01"
            )
        ]
        session.add_all(incidents)

        # 7. Seed Initial Agent Audit Logs
        agent_logs = [
            AgentLog(
                incident_id="INC-2026-001",
                agent_name="Emergency Detection Agent",
                step="NLP Entity & Hazard Extraction",
                thought="Detected critical keywords: 'hospital basement inundated', '5 elderly', 'oxygen cylinder low'. High-risk medical facility.",
                action="STRUCTURE_INCIDENT",
                input_payload=json.dumps({"sos": "Riverside Care Hospital basement and ground floor inundated..."}),
                output_payload=json.dumps({"category": "MEDICAL_URGENCY", "victims": 7, "depth": 2.2}),
                confidence=0.98,
                execution_time_ms=145.2
            ),
            AgentLog(
                incident_id="INC-2026-001",
                agent_name="Priority Agent",
                step="Multi-Criteria MCDA Scoring",
                thought="Water depth > 2m (weight 0.35) + 5 elderly/oxygen dependent (weight 0.40) + rapid rise hazard (weight 0.25). Resulting score: 94.5/100.",
                action="ASSIGN_PRIORITY",
                input_payload=json.dumps({"victims": 7, "depth": 2.2, "elderly": 5}),
                output_payload=json.dumps({"score": 94.5, "level": "CRITICAL"}),
                confidence=0.96,
                execution_time_ms=88.4
            ),
            AgentLog(
                incident_id="INC-2026-001",
                agent_name="Resource Allocation Agent",
                step="Optimal Team Assignment",
                thought="Incident requires aquatic inflatable boats and paramedic support. TEAM-NDRF-01 is 1.8km away with 5 boats and available status.",
                action="DISPATCH_TEAM",
                input_payload=json.dumps({"incident": "INC-2026-001", "required_gear": ["BOATS", "AMPHIBIOUS"]}),
                output_payload=json.dumps({"assigned_team": "TEAM-NDRF-01", "eta_minutes": 8.5}),
                confidence=0.95,
                execution_time_ms=112.0
            ),
            AgentLog(
                incident_id="INC-2026-001",
                agent_name="Route Planning Agent",
                step="Flood-Avoidance A* Pathfinding",
                thought="Direct route through Bharalu Bridge is submerged > 2.5m. Routing via elevated North Loop corridor to reach hospital pier safely.",
                action="COMPUTE_SAFE_ROUTE",
                input_payload=json.dumps({"origin": [26.1602, 91.7450], "dest": [26.1620, 91.7480]}),
                output_payload=json.dumps({"waypoints_count": 5, "distance_km": 2.4, "risk": "SAFE_CORRIDOR"}),
                confidence=0.97,
                execution_time_ms=132.6
            ),
            AgentLog(
                incident_id="INC-2026-001",
                agent_name="Communication Agent",
                step="Multi-Channel Emergency Alert Dispatch",
                thought="Generated operational orders for NDRF Alpha, SMS confirmation to caller with ETA 8.5m, and bed preparation notification to Sarada Camp.",
                action="BROADCAST_ALERTS",
                input_payload=json.dumps({"incident": "INC-2026-001", "team": "TEAM-NDRF-01"}),
                output_payload=json.dumps({"channels": ["SMS_CALLER", "VHF_RADIO", "DEOC_SITREP", "CAMP_ADVISORY"]}),
                confidence=0.99,
                execution_time_ms=95.1
            ),
        ]
        session.add_all(agent_logs)

        # 8. Seed an initial route
        initial_route = RescueRoute(
            id="ROUTE-INC-001",
            incident_id="INC-2026-001",
            team_id="TEAM-NDRF-01",
            camp_id="CAMP-01",
            waypoints_json=json.dumps([
                [26.1602, 91.7450],
                [26.1610, 91.7460],
                [26.1618, 91.7472],
                [26.1620, 91.7480],
                [26.1650, 91.7550],
                [26.1685, 91.7620]
            ]),
            distance_km=2.8,
            estimated_minutes=8.5,
            flood_risk_level="SAFE_CORRIDOR",
            route_summary="Pandu Depot -> Bharalu Ghat Elevated Pier -> Hospital -> Evacuation to Sarada Girls Camp",
            status="ACTIVE"
        )
        session.add(initial_route)

        await session.commit()
        logger.info("Database successfully seeded with realistic flood disaster response scenario!")
