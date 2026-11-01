import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Junior Astronaut" in data["app"]

@pytest.mark.asyncio
async def test_science_resources(async_client):
    response = await async_client.get("/api/science/resources")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    assert any("ECLSS" in d["title"] for d in data)
    assert any("Radiation" in d["title"] for d in data)

@pytest.mark.asyncio
async def test_mission_lifecycle_api(async_client):
    # 1. Create Mission
    create_payload = {
        "destination": "moon",
        "duration_days": 10,
        "difficulty": "beginner",
        "commander_name": "Cadet Armstrong",
        "seed": 12345
    }
    resp = await async_client.post("/api/missions", json=create_payload)
    assert resp.status_code == 200
    mission_data = resp.json()
    mission_id = mission_data["mission_id"]
    assert mission_data["status"] == "planning"

    # 2. Deploy Outpost with valid budget
    alloc_payload = {
        "life_support": 25,
        "power_generation": 25,
        "water_recycling": 20,
        "food_production": 15,
        "radiation_protection": 10,
        "emergency_reserves": 5
    }
    deploy_resp = await async_client.post(f"/api/missions/{mission_id}/deploy", json=alloc_payload)
    assert deploy_resp.status_code == 200
    state = deploy_resp.json()
    assert state["status"] == "active"
    assert state["current_day"] == 1
    assert state["resources"]["oxygen"] >= 80

    # 3. Get Systems Dependency Graph
    sys_resp = await async_client.get(f"/api/missions/{mission_id}/systems")
    assert sys_resp.status_code == 200
    graph = sys_resp.json()
    assert len(graph["nodes"]) >= 5
    assert len(graph["edges"]) >= 5

    # 4. Advance Day
    adv_resp = await async_client.post(f"/api/missions/{mission_id}/advance")
    assert adv_resp.status_code == 200
    adv_state = adv_resp.json()
    assert adv_state["current_day"] == 2

    # 5. Get Report
    rep_resp = await async_client.get(f"/api/missions/{mission_id}/report")
    assert rep_resp.status_code == 200
    report = rep_resp.json()
    assert report["days_survived"] == 2
    assert "telemetry_history" in report

    # 6. Trigger Replay
    replay_resp = await async_client.post(f"/api/missions/{mission_id}/replay")
    assert replay_resp.status_code == 200
    replay_state = replay_resp.json()
    assert replay_state["is_replay"] is True
    assert replay_state["parent_mission_id"] == mission_id

    # 7. Compare missions
    comp_resp = await async_client.get(f"/api/missions/{mission_id}/compare/{replay_state['mission_id']}")
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert comp_data["is_counterfactual"] is True

@pytest.mark.asyncio
async def test_mentor_explain_api(async_client):
    payload = {
        "event_title": "Solar Radiation Storm",
        "decision_title": "Shelter in Regolith Bunker",
        "destination": "moon",
        "current_day": 3,
        "what_changed": "Crew health dropped 5% due to stress; radiation absorbed is zero.",
        "why_it_changed": "Subterranean regolith blocks high-energy cosmic protons.",
        "scientific_concept": "Passive In-Situ Radiation Shielding",
        "affected_systems": ["crew_health", "radiation_shield"],
        "what_to_monitor": "Astronaut fatigue and cabin air."
    }
    resp = await async_client.post("/api/mentor/explain", json=payload)
    assert resp.status_code == 200
    advice = resp.json()
    assert "Passive In-Situ" in advice["scientific_concept"]
    assert advice["source"] in ["rule_based", "ai_model"]
