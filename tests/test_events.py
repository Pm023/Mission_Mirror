import pytest
from app.services.event_engine import EventEngine, EVENT_TEMPLATES
from app.services.simulation_engine import SimulationEngine
from app.schemas.mission import ResourceState, SystemState, CrewState

def test_all_six_events_exist():
    assert len(EVENT_TEMPLATES) == 6
    expected_keys = [
        "solar_radiation_storm",
        "water_recycling_malfunction",
        "power_generation_failure",
        "food_supply_shortage",
        "crew_medical_emergency",
        "equipment_maintenance_failure"
    ]
    for key in expected_keys:
        assert key in EVENT_TEMPLATES
        assert len(EVENT_TEMPLATES[key]["choices"]) == 3

def test_event_selection():
    event_engine = EventEngine(seed=1234)
    event = event_engine.select_event([], "moon")
    assert event.event_type in EVENT_TEMPLATES
    assert len(event.choices) == 3
    assert "[MOON]" in event.title

def test_solar_radiation_storm_tradeoffs():
    engine = SimulationEngine(seed=100)
    event_engine = EventEngine(seed=100)
    event = event_engine.select_event([], "moon")
    # Force solar radiation storm
    event.event_type = "solar_radiation_storm"

    # Choice 1: Deflector Boost (burns power, protects health)
    res1 = ResourceState(oxygen=90, water=90, food=90, energy=90, crew_health=100, system_condition=90)
    sys1 = SystemState(power_grid=90, life_support=90, water_recovery=90, greenhouse=90, radiation_shield=90, hull_integrity=90)
    crew1 = CrewState()
    res1, sys1, crew1, spares1, txt1, mentor1 = engine.apply_event_decision(event, "deflector_boost", res1, sys1, crew1, 2)
    assert res1.energy < 90.0
    assert res1.crew_health == 100.0

    # Choice 3: Passive Shielding (saves power, incurs severe radiation and health damage)
    res2 = ResourceState(oxygen=90, water=90, food=90, energy=90, crew_health=100, system_condition=90)
    sys2 = SystemState(power_grid=90, life_support=90, water_recovery=90, greenhouse=90, radiation_shield=90, hull_integrity=90)
    crew2 = CrewState()
    res2, sys2, crew2, spares2, txt2, mentor2 = engine.apply_event_decision(event, "passive_shielding", res2, sys2, crew2, 2)
    assert res2.energy == 90.0
    assert res2.crew_health <= 78.0
    assert crew2.radiation_dose_msv > 0.0

def test_water_recycling_malfunction_spares_usage():
    engine = SimulationEngine(seed=100)
    event_engine = EventEngine(seed=100)
    event = event_engine.select_event([], "mars")
    event.event_type = "water_recycling_malfunction"

    res = ResourceState(oxygen=90, water=90, food=90, energy=90, crew_health=100, system_condition=90)
    sys = SystemState(power_grid=90, life_support=90, water_recovery=40, greenhouse=90, radiation_shield=90, hull_integrity=90)
    crew = CrewState()

    res, sys, crew, spares, txt, mentor = engine.apply_event_decision(event, "replace_membrane", res, sys, crew, 2)
    assert spares == 1 # Consumed 1 spare
    assert sys.water_recovery > 70.0 # Repaired
    assert "scientific_concept" in mentor
