import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.asyncio
async def test_get_exploration_objectives():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Test Moon
        resp = await ac.get("/api/exploration/objectives/moon")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        assert any(obj["id"] == "moon_solar_array" for obj in data)
        assert any(obj["id"] == "moon_power_fault" for obj in data)
        assert any(obj["id"] == "moon_soil_sample" for obj in data)

        # Test Mars
        resp_mars = await ac.get("/api/exploration/objectives/mars")
        assert resp_mars.status_code == 200
        mars_data = resp_mars.json()
        assert len(mars_data) == 3
        assert any(obj["id"] == "mars_rover_inspection" for obj in mars_data)

        # Test Station
        resp_st = await ac.get("/api/exploration/objectives/station")
        assert resp_st.status_code == 200
        st_data = resp_st.json()
        assert len(st_data) == 3
        assert any(obj["id"] == "station_life_support" for obj in st_data)


@pytest.mark.asyncio
async def test_sandbox_action_execution():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        req_payload = {
            "objective_id": "moon_solar_array",
            "option_id": "piezo_pulse"
        }
        resp = await ac.post("/api/exploration/sandbox/action", json=req_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["objective_id"] == "moon_solar_array"
        assert "Photoelectric Effect" in data["scientific_concept"]
        assert data["score_delta"] > 0
        assert "energy" in data["resource_deltas"]
        assert data["updated_state"]["commander_name"] == "Cadet Explorer"


@pytest.mark.asyncio
async def test_mission_exploration_action_execution():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create Moon mission
        create_resp = await ac.post("/api/missions", json={
            "destination": "moon",
            "duration_days": 10,
            "difficulty": "beginner",
            "commander_name": "Commander Armstrong"
        })
        assert create_resp.status_code == 200
        mission_id = create_resp.json()["mission_id"]

        # 2. Deploy outpost
        deploy_resp = await ac.post(f"/api/missions/{mission_id}/deploy", json={
            "life_support": 20,
            "power_generation": 25,
            "water_recycling": 20,
            "food_production": 15,
            "radiation_protection": 10,
            "emergency_reserves": 10
        })
        assert deploy_resp.status_code == 200
        initial_score = deploy_resp.json()["score"]

        # 3. Perform 3D EVA action on solar array
        eva_resp = await ac.post(f"/api/exploration/missions/{mission_id}/action", json={
            "objective_id": "moon_solar_array",
            "option_id": "piezo_pulse"
        })
        assert eva_resp.status_code == 200
        eva_data = eva_resp.json()
        assert eva_data["success"] is True
        assert eva_data["updated_state"]["score"] > initial_score
        assert "moon_solar_array" in eva_data["updated_state"]["completed_exploration_objectives"]

        # 4. Check objectives endpoint reflects completion
        objs_resp = await ac.get(f"/api/exploration/objectives/moon?mission_id={mission_id}")
        assert objs_resp.status_code == 200
        moon_objs = objs_resp.json()
        completed_array = [o for o in moon_objs if o["id"] == "moon_solar_array"][0]
        assert completed_array["completed"] is True


@pytest.mark.asyncio
async def test_exploration_static_files():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Check index HTML contains Universe and Exploration sections
        html_resp = await ac.get("/")
        assert html_resp.status_code == 200
        assert "view-universe" in html_resp.text
        assert "view-exploration" in html_resp.text
        assert "Explore Universe" in html_resp.text

        # Check JS files
        u_resp = await ac.get("/js/universe_view.js")
        assert u_resp.status_code == 200
        assert "UniverseView" in u_resp.text

        a_resp = await ac.get("/js/astronaut_controller.js")
        assert a_resp.status_code == 200
        assert "AstronautController" in a_resp.text

        e_resp = await ac.get("/js/exploration_environments.js")
        assert e_resp.status_code == 200
        assert "ExplorationEnvironments" in e_resp.text

        h_resp = await ac.get("/js/exploration_hud.js")
        assert h_resp.status_code == 200
        assert "ExplorationHUD" in h_resp.text

        # Check GLTFLoader and 3D Astronaut model
        gltf_resp = await ac.get("/js/GLTFLoader.js")
        assert gltf_resp.status_code == 200
        assert "GLTFLoader" in gltf_resp.text

        prev_resp = await ac.get("/js/astronaut_preview.js")
        assert prev_resp.status_code == 200
        assert "AstronautPreview" in prev_resp.text

        glb_resp = await ac.get("/assets/models/Astronaut.glb")
        assert glb_resp.status_code == 200
        assert len(glb_resp.content) > 2000000 # ~2.8 MB
