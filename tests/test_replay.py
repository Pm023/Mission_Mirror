import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.mission import Mission, DayLog, DecisionRecord
from app.services.replay_service import ReplayService
from app.schemas.mission import OutpostAllocation

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_counterfactual_replay_creation(db_session):
    alloc = OutpostAllocation(
        life_support=20,
        power_generation=20,
        water_recycling=20,
        food_production=15,
        radiation_protection=15,
        emergency_reserves=10
    )
    orig = Mission(
        destination="mars",
        duration_days=20,
        difficulty="intermediate",
        seed=777,
        status="active",
        current_day=5,
        score=250,
        initial_allocation=json.dumps(alloc.model_dump())
    )
    db_session.add(orig)
    db_session.commit()

    replay = ReplayService.create_replay_mission(db_session, orig)

    assert replay.is_replay is True
    assert replay.parent_id == orig.id
    assert replay.seed == 777
    assert replay.destination == "mars"
    assert replay.duration_days == 20
    assert replay.current_day == 1 # Replay resets to day 1

def test_counterfactual_comparison(db_session):
    orig = Mission(
        id="orig-123",
        destination="moon",
        duration_days=10,
        difficulty="beginner",
        seed=999,
        status="completed",
        current_day=10,
        score=850,
        initial_allocation="{}"
    )
    alt = Mission(
        id="alt-456",
        parent_id="orig-123",
        is_replay=True,
        destination="moon",
        duration_days=10,
        difficulty="beginner",
        seed=999,
        status="completed",
        current_day=10,
        score=980,
        initial_allocation="{}"
    )
    db_session.add_all([orig, alt])
    db_session.commit()

    # Add sample decision
    d1 = DecisionRecord(mission_id=orig.id, day=3, event_id="evt_water", choice_id="ration_and_bypass", choice_title="Ration Water", impact_summary="Dehydration -10% health")
    d2 = DecisionRecord(mission_id=alt.id, day=3, event_id="evt_water", choice_id="replace_membrane", choice_title="Install Spare Membrane", impact_summary="Restored 95%")
    db_session.add_all([d1, d2])
    db_session.commit()

    comp = ReplayService.compare_runs(db_session, orig.id, alt.id)
    assert comp["is_counterfactual"] is True
    assert comp["deltas"]["score_delta"] == 130
    assert len(comp["deltas"]["decision_divergences"]) == 1
    assert "Original chose 'Ration Water' while Replay chose 'Install Spare Membrane'" in comp["deltas"]["decision_divergences"][0]["divergence_analysis"]
