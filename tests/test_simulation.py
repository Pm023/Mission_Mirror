import pytest
from app.services.simulation_engine import SimulationEngine
from app.schemas.mission import OutpostAllocation, ResourceState, SystemState, CrewState, ObjectiveSchema

def test_initial_outpost_calculation():
    engine = SimulationEngine(seed=42)
    alloc = OutpostAllocation(
        life_support=20,
        power_generation=25,
        water_recycling=20,
        food_production=15,
        radiation_protection=10,
        emergency_reserves=10
    )
    initial = engine.calculate_initial_state("moon", "intermediate", 10, alloc)
    assert initial["resources"].oxygen > 80.0
    assert initial["resources"].water > 80.0
    assert initial["resources"].energy > 80.0
    assert initial["resources"].crew_health == 100.0
    assert initial["emergency_spares"] >= 1
    assert len(initial["objectives"]) == 4

def test_budget_overspend_validation():
    with pytest.raises(ValueError) as excinfo:
        OutpostAllocation(
            life_support=30,
            power_generation=30,
            water_recycling=30,
            food_production=20,
            radiation_protection=10,
            emergency_reserves=10
        )
    assert "cannot exceed 100" in str(excinfo.value)

def test_daily_tick_nominal_consumption():
    engine = SimulationEngine(seed=42)
    res = ResourceState(oxygen=90.0, water=90.0, food=90.0, energy=90.0, crew_health=100.0, system_condition=90.0)
    sys = SystemState(power_grid=90.0, life_support=90.0, water_recovery=90.0, greenhouse=90.0, radiation_shield=90.0, hull_integrity=95.0)
    crew = CrewState()
    objs = [ObjectiveSchema(id="obj_survive", title="Sustain Health", description="Test", completed=False, progress=0.0)]

    res, sys, crew, objs, warnings, logs, failure = engine.advance_day_tick(
        current_day=2,
        total_days=10,
        destination="moon",
        difficulty="intermediate",
        resources=res,
        systems=sys,
        crew=crew,
        objectives=objs,
        emergency_spares=2
    )

    assert failure is None
    assert res.oxygen > 0.0
    assert res.water > 0.0
    assert sys.power_grid < 90.0 # Naturally wore down slightly
    assert crew.radiation_dose_msv > 0.0

def test_cascading_power_failure():
    engine = SimulationEngine(seed=42)
    # Start with severely depleted energy
    res = ResourceState(oxygen=90.0, water=90.0, food=90.0, energy=10.0, crew_health=100.0, system_condition=80.0)
    sys = SystemState(power_grid=40.0, life_support=80.0, water_recovery=80.0, greenhouse=80.0, radiation_shield=80.0, hull_integrity=90.0)
    crew = CrewState()
    objs = []

    res, sys, crew, objs, warnings, logs, failure = engine.advance_day_tick(
        current_day=2,
        total_days=10,
        destination="mars",
        difficulty="expert",
        resources=res,
        systems=sys,
        crew=crew,
        objectives=objs,
        emergency_spares=1
    )

    # Low energy should trigger critical brownout warning and throttle ECLSS
    assert any("CRITICAL POWER BROWNOUT" in w for w in warnings)
    assert res.oxygen < 90.0

def test_fatal_oxygen_depletion():
    engine = SimulationEngine(seed=42)
    # Start with almost no oxygen and dead life support
    res = ResourceState(oxygen=1.0, water=80.0, food=80.0, energy=80.0, crew_health=50.0, system_condition=50.0)
    sys = SystemState(power_grid=20.0, life_support=5.0, water_recovery=50.0, greenhouse=50.0, radiation_shield=50.0, hull_integrity=50.0)
    crew = CrewState()
    objs = []

    res, sys, crew, objs, warnings, logs, failure = engine.advance_day_tick(
        current_day=3,
        total_days=10,
        destination="moon",
        difficulty="expert",
        resources=res,
        systems=sys,
        crew=crew,
        objectives=objs,
        emergency_spares=0
    )

    assert failure is not None
    assert "asphyxiation" in failure.lower() or "oxygen" in failure.lower()
