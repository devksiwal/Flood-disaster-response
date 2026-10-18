import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.connection import init_db
from app.database.seed import seed_database
from starlette.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    with TestClient(app) as client:
        # Triggers lifespan (init_db and seed_database)
        response = client.get("/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_root_and_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "OPERATIONAL"
        assert data["active_agents"] == 5

        hr = await ac.get("/health")
        assert hr.status_code == 200
        assert hr.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_auth_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test login with seeded commander user
        login_res = await ac.post("/api/v1/auth/login", data={"username": "commander", "password": "commander123"})
        assert login_res.status_code == 200
        token_data = login_res.json()
        assert "access_token" in token_data
        token = token_data["access_token"]

        # Test auth/me with token
        me_res = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["username"] == "commander"

        # Test login failure
        bad_login = await ac.post("/api/v1/auth/login", data={"username": "commander", "password": "wrongpassword"})
        assert bad_login.status_code == 401

        # Test register
        import uuid
        test_user = f"responder_{uuid.uuid4().hex[:6]}"
        reg_res = await ac.post("/api/v1/auth/register", json={
            "username": test_user,
            "email": f"{test_user}@ndma.gov.in",
            "password": "Password123!",
            "role": "field_responder",
            "full_name": "Test Field Responder"
        })
        assert reg_res.status_code == 200
        assert "access_token" in reg_res.json()


@pytest.mark.asyncio
async def test_incidents_crud_and_sos_pipeline():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. List existing incidents
        list_res = await ac.get("/api/v1/incidents")
        assert list_res.status_code == 200
        incidents = list_res.json()
        assert len(incidents) > 0

        # 2. Submit new SOS
        sos_payload = {
            "raw_sos": "CRITICAL EMERGENCY: 6 victims stranded on rooftop near Bharalu Bridge. Water level 2.5 meters. Submerged electric wires sparking. Need boat!",
            "caller_contact": "+91-99887-76655",
            "latitude": 26.1595,
            "longitude": 91.7482,
            "location_name": "Bharalu Bridge Sector"
        }
        sos_res = await ac.post("/api/v1/incidents/sos", json=sos_payload)
        assert sos_res.status_code == 200
        sos_data = sos_res.json()
        assert sos_data["status"] == "PROCESSED_BY_MULTI_AGENT_SYSTEM"
        incident_id = sos_data["incident_id"]

        # 3. Get incident details
        detail_res = await ac.get(f"/api/v1/incidents/{incident_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["incident"]["id"] == incident_id
        assert detail["incident"]["status"] == "DISPATCHED"
        assert detail["assigned_team"] is not None
        assert detail["route"] is not None
        assert len(detail["route"]["waypoints"]) > 0

        # 4. Update status to RESCUED
        update_res = await ac.patch(f"/api/v1/incidents/{incident_id}/status", json={"status": "RESCUED"})
        assert update_res.status_code == 200

        # 5. Non-existent incident
        bad_inc = await ac.get("/api/v1/incidents/NON_EXISTENT_ID")
        assert bad_inc.status_code == 404


@pytest.mark.asyncio
async def test_teams_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        teams_res = await ac.get("/api/v1/teams")
        assert teams_res.status_code == 200
        teams = teams_res.json()
        assert len(teams) > 0
        team_id = teams[0]["id"]

        # Get team by ID
        t_res = await ac.get(f"/api/v1/teams/{team_id}")
        assert t_res.status_code == 200
        assert t_res.json()["id"] == team_id

        # Update team status
        stat_res = await ac.patch(f"/api/v1/teams/{team_id}/status", json={"status": "AVAILABLE"})
        assert stat_res.status_code == 200

        # Update team location
        loc_res = await ac.patch(f"/api/v1/teams/{team_id}/location", json={"latitude": 26.165, "longitude": 91.755})
        assert loc_res.status_code == 200


@pytest.mark.asyncio
async def test_flood_sensors_and_zones():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        sensors_res = await ac.get("/api/v1/flood/sensors")
        assert sensors_res.status_code == 200
        sensors = sensors_res.json()
        assert len(sensors) > 0
        sensor_id = sensors[0]["id"]

        # Update telemetry
        tel_res = await ac.post(f"/api/v1/flood/sensor/{sensor_id}/telemetry", json={
            "water_level_meters": 51.5,
            "trend": "RISING",
            "rainfall_mm_last_3h": 60.0
        })
        assert tel_res.status_code == 200
        assert tel_res.json()["status"] == "CRITICAL"

        # Check zones
        zones_res = await ac.get("/api/v1/flood/zones")
        assert zones_res.status_code == 200
        assert len(zones_res.json()) > 0


@pytest.mark.asyncio
async def test_camps_and_routes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        camps_res = await ac.get("/api/v1/camps")
        assert camps_res.status_code == 200
        camps = camps_res.json()
        assert len(camps) > 0
        camp_id = camps[0]["id"]

        # Admit evacuees
        intake_res = await ac.patch(f"/api/v1/camps/{camp_id}/intake", json={
            "admit_evacuees": 15,
            "food_packets_delta": -15
        })
        assert intake_res.status_code == 200
        assert intake_res.json()["new_occupancy"] >= 15

        # Check routes
        routes_res = await ac.get("/api/v1/routes")
        assert routes_res.status_code == 200


@pytest.mark.asyncio
async def test_agents_status_logs_and_trigger():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Agent status
        status_res = await ac.get("/api/v1/agents/status")
        assert status_res.status_code == 200
        assert len(status_res.json()["active_agents"]) == 6

        # Agent logs
        logs_res = await ac.get("/api/v1/agents/logs")
        assert logs_res.status_code == 200

        # Trigger agent pipeline on existing incident
        incidents_res = await ac.get("/api/v1/incidents")
        first_incident_id = incidents_res.json()[0]["id"]

        trig_res = await ac.post(f"/api/v1/agents/trigger/{first_incident_id}")
        assert trig_res.status_code == 200
        assert "result" in trig_res.json()


def test_websockets_connection_and_event_broadcast():
    client = TestClient(app)
    # Test connection to the primary /ws/events route used by frontend
    with client.websocket_connect("/ws/events") as ws:
        init_data = ws.receive_json()
        assert init_data["type"] == "CONNECTION_ESTABLISHED"

        # Test ping pong
        ws.send_text("ping")
        resp = ws.receive_json()
        assert resp["type"] == "PONG"

    # Test /events/ws route
    with client.websocket_connect("/events/ws") as ws:
        init_data = ws.receive_json()
        assert init_data["type"] == "CONNECTION_ESTABLISHED"


@pytest.mark.asyncio
async def test_sos_pipeline_edge_cases():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Edge case 1: SOS with no coordinates (should auto-generate valid coordinates)
        res1 = await ac.post("/api/v1/incidents/sos", json={
            "raw_sos": "Water in compound, 3 people needing assistance."
        })
        assert res1.status_code == 200
        inc1 = res1.json()["result"]["incident"]
        assert inc1["latitude"] is not None
        assert inc1["longitude"] is not None
        assert inc1["victim_count"] >= 3

        # Edge case 2: Extreme medical emergency SOS with multiple hazards
        res2 = await ac.post("/api/v1/incidents/sos", json={
            "raw_sos": "Hospital basement flooded 3 meters. Power cables sparking in water, roof cracking, 10 patients on oxygen!",
            "latitude": 26.162,
            "longitude": 91.748
        })
        assert res2.status_code == 200
        inc2 = res2.json()["result"]["incident"]
        assert inc2["category"] == "MEDICAL_URGENCY"
        assert inc2["priority_level"] == "CRITICAL"
        assert inc2["priority_score"] >= 80
        assert "ELECTRICAL_WIRES_SUBMERGED" in inc2["hazards"]
        assert "CRITICAL_OXYGEN_DEPLETION" in inc2["hazards"]


@pytest.mark.asyncio
async def test_incident_status_frees_team():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create an incident that dispatches a team
        res = await ac.post("/api/v1/incidents/sos", json={
            "raw_sos": "Trapped in house with rising water 2m. Need rescue boat."
        })
        inc = res.json()["result"]["incident"]
        team_id = inc["assigned_team_id"]
        assert team_id is not None

        # Check team is DISPATCHED
        t_res = await ac.get(f"/api/v1/teams/{team_id}")
        assert t_res.json()["status"] == "DISPATCHED"

        # Update incident status to RESCUED
        patch_res = await ac.patch(f"/api/v1/incidents/{inc['id']}/status", json={"status": "RESCUED"})
        assert patch_res.status_code == 200

        # Team should now be freed and AVAILABLE
        t_res2 = await ac.get(f"/api/v1/teams/{team_id}")
        assert t_res2.json()["status"] == "AVAILABLE"
        assert t_res2.json()["current_incident_id"] is None

