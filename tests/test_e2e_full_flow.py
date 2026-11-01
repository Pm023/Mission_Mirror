import json
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
async def test_static_files_served(async_client):
    # Test index.html served at root
    resp = await async_client.get("/")
    assert resp.status_code == 200
    assert "MISSION MIRROR" in resp.text
    assert "Junior Astronaut" in resp.text

    # Test CSS served
    css_resp = await async_client.get("/css/style.css")
    assert css_resp.status_code == 200
    assert "--cyan-accent" in css_resp.text

    # Test JS served
    js_resp = await async_client.get("/js/app.js")
    assert js_resp.status_code == 200
    assert "DOMContentLoaded" in js_resp.text

@pytest.mark.asyncio
async def test_full_mission_counterfactual_lifecycle(async_client):
    # 1. Create a mission on Mars for 10 days on intermediate difficulty
    create_res = await async_client.post("/api/missions", json={
        "destination": "mars",
        "duration_days": 10,
        "difficulty": "intermediate",
        "commander_name": "Cadet Sally",
        "seed": 8888
    })
    assert create_res.status_code == 200
    orig_mission = create_res.json()
    orig_id = orig_mission["mission_id"]

    # 2. Deploy outpost with balanced allocation
    deploy_res = await async_client.post(f"/api/missions/{orig_id}/deploy", json={
        "life_support": 20,
        "power_generation": 25,
        "water_recycling": 20,
        "food_production": 15,
        "radiation_protection": 10,
        "emergency_reserves": 10
    })
    assert deploy_res.status_code == 200
    state = deploy_res.json()
    assert state["status"] == "active"
    assert state["current_day"] == 1

    # 3. Advance days until event or day 4
    for _ in range(4):
        state_check = await async_client.get(f"/api/missions/{orig_id}/state")
        st = state_check.json()
        if st["active_event"]:
            # Make decision A
            evt = st["active_event"]
            choice_a = evt["choices"][0]["id"]
            dec_res = await async_client.post(f"/api/missions/{orig_id}/decisions", json={"choice_id": choice_a})
            assert dec_res.status_code == 200
            st = dec_res.json()
            assert st["mentor_advice"] is not None
            assert st["mentor_advice"]["scientific_concept"] != ""
        
        if st["status"] == "active":
            adv_res = await async_client.post(f"/api/missions/{orig_id}/advance")
            assert adv_res.status_code == 200

    # 4. Debrief Report for original run
    rep_res = await async_client.get(f"/api/missions/{orig_id}/report")
    assert rep_res.status_code == 200
    orig_report = rep_res.json()
    assert orig_report["days_survived"] >= 2
    assert len(orig_report["telemetry_history"]) >= 2

    # 5. Launch Counterfactual Replay
    replay_res = await async_client.post(f"/api/missions/{orig_id}/replay")
    assert replay_res.status_code == 200
    replay_state = replay_res.json()
    assert replay_state["is_replay"] is True
    assert replay_state["parent_mission_id"] == orig_id
    assert replay_state["current_day"] == 1
    replay_id = replay_state["mission_id"]

    # 6. Compare runs
    comp_res = await async_client.get(f"/api/missions/{orig_id}/compare/{replay_id}")
    assert comp_res.status_code == 200
    comp = comp_res.json()
    assert comp["is_counterfactual"] is True
    assert "Simulated Counterfactual" in comp["disclaimer"]
    assert "original_run" in comp
    assert "counterfactual_run" in comp

