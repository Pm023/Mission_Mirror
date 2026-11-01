"""
Database Seeder for Mission Mirror
Creates a completed sample mission and counterfactual replay run
for instant hackathon presentation and demonstration.
"""
import json
from app.database import SessionLocal, init_db
from app.models.mission import Mission, DayLog, EventLog, DecisionRecord
from app.services.simulation_engine import SimulationEngine
from app.schemas.mission import OutpostAllocation

def seed():
    init_db()
    db = SessionLocal()

    # Check if already seeded
    existing = db.query(Mission).filter(Mission.commander_name == "Commander Watkins (Sample)").first()
    if existing:
        print("Sample mission already seeded.")
        db.close()
        return

    print("Seeding sample completed mission and counterfactual replay...")

    # 1. Original Run (Conservative choices, experienced power brownouts)
    alloc = OutpostAllocation(
        life_support=20,
        power_generation=20,
        water_recycling=20,
        food_production=15,
        radiation_protection=15,
        emergency_reserves=10
    )

    orig = Mission(
        id="sample-mission-orig",
        is_replay=False,
        commander_name="Commander Watkins (Sample)",
        destination="moon",
        duration_days=10,
        difficulty="intermediate",
        seed=1042,
        status="completed",
        current_day=10,
        score=780,
        initial_allocation=json.dumps(alloc.model_dump()),
        state_json=json.dumps({
            "resources": {"oxygen": 72.0, "water": 68.0, "food": 74.0, "energy": 55.0, "crew_health": 82.0, "system_condition": 76.5},
            "systems": {"power_grid": 70.0, "life_support": 78.0, "water_recovery": 75.0, "greenhouse": 72.0, "radiation_shield": 80.0, "hull_integrity": 84.0},
            "crew": {"crew_count": 4, "morale": 80.0, "radiation_dose_msv": 24.5, "status": "nominal"},
            "emergency_spares": 1,
            "objectives": [
                {"id": "obj_survive", "title": "Sustain Crew Health", "description": "Keep crew > 60%", "completed": True, "progress": 100.0},
                {"id": "obj_eclss", "title": "Closed-Loop ECLSS Stability", "description": "Maintain life support > 65%", "completed": True, "progress": 76.5},
                {"id": "obj_power", "title": "Energy Grid Autonomy", "description": "Prevent brownouts > 30%", "completed": True, "progress": 55.0},
                {"id": "obj_hull", "title": "Structural Habitat Integrity", "description": "Protect outpost hull > 70%", "completed": True, "progress": 84.0}
            ],
            "warnings": [],
            "recent_logs": ["Mission completed! Outpost survived 10-day surface operation."]
        })
    )
    db.add(orig)
    db.commit()

    # Add DayLogs for Original
    o2_curve = [92, 88, 85, 82, 79, 77, 75, 74, 73, 72]
    h2o_curve = [94, 90, 86, 82, 79, 76, 73, 71, 69, 68]
    pwr_curve = [90, 85, 78, 62, 58, 65, 62, 60, 58, 55]
    hlt_curve = [100, 100, 95, 88, 85, 84, 83, 83, 82, 82]

    for d in range(1, 11):
        dl = DayLog(
            mission_id=orig.id,
            day=d,
            oxygen=o2_curve[d-1],
            water=h2o_curve[d-1],
            food=80 - (d * 0.6),
            energy=pwr_curve[d-1],
            crew_health=hlt_curve[d-1],
            system_condition=85 - (d * 0.9),
            events_summary="Solar storm shelter protocol" if d == 4 else "Nominal",
            decisions_summary="Sheltered in regolith bunker" if d == 4 else "",
            log_messages=json.dumps([f"Day {d} completed successfully."])
        )
        db.add(dl)

    # Decision on Day 4
    dec_orig = DecisionRecord(
        mission_id=orig.id,
        day=4,
        event_id="evt_solar_storm",
        choice_id="regolith_bunker",
        choice_title="Shelter Crew in Regolith Storm Bunker",
        impact_summary="Crew health dipped by 5% from emergency confinement; greenhouse paused.",
        mentor_notes="In-Situ Passive Radiation Attenuation"
    )
    db.add(dec_orig)
    db.commit()

    # 2. Counterfactual Replay Run (Chose Deflector Boost on Day 4)
    alt = Mission(
        id="sample-mission-replay",
        parent_id=orig.id,
        is_replay=True,
        commander_name="Commander Watkins (Counterfactual Replay)",
        destination="moon",
        duration_days=10,
        difficulty="intermediate",
        seed=1042,
        status="completed",
        current_day=10,
        score=920,
        initial_allocation=json.dumps(alloc.model_dump()),
        state_json=json.dumps({
            "resources": {"oxygen": 80.0, "water": 74.0, "food": 79.0, "energy": 68.0, "crew_health": 94.0, "system_condition": 82.0},
            "systems": {"power_grid": 82.0, "life_support": 84.0, "water_recovery": 80.0, "greenhouse": 81.0, "radiation_shield": 85.0, "hull_integrity": 88.0},
            "crew": {"crew_count": 4, "morale": 92.0, "radiation_dose_msv": 12.0, "status": "nominal"},
            "emergency_spares": 1,
            "objectives": [
                {"id": "obj_survive", "title": "Sustain Crew Health", "description": "Keep crew > 60%", "completed": True, "progress": 100.0},
                {"id": "obj_eclss", "title": "Closed-Loop ECLSS Stability", "description": "Maintain life support > 65%", "completed": True, "progress": 82.0},
                {"id": "obj_power", "title": "Energy Grid Autonomy", "description": "Prevent brownouts > 30%", "completed": True, "progress": 68.0},
                {"id": "obj_hull", "title": "Structural Habitat Integrity", "description": "Protect outpost hull > 70%", "completed": True, "progress": 88.0}
            ],
            "warnings": [],
            "recent_logs": ["Replay finished! Alternative deflector protocol achieved +140 score increase."]
        })
    )
    db.add(alt)
    db.commit()

    # Telemetry for Replay
    hlt_alt_curve = [100, 100, 98, 97, 96, 96, 95, 95, 94, 94]
    for d in range(1, 11):
        dl_alt = DayLog(
            mission_id=alt.id,
            day=d,
            oxygen=o2_curve[d-1] + 4,
            water=h2o_curve[d-1] + 3,
            food=82 - (d * 0.4),
            energy=pwr_curve[d-1] + 5,
            crew_health=hlt_alt_curve[d-1],
            system_condition=88 - (d * 0.6),
            events_summary="Deflector boost protocol" if d == 4 else "Nominal",
            decisions_summary="Overdrive Active Magnetic Deflector" if d == 4 else "",
            log_messages=json.dumps([f"Replay Day {d} completed."])
        )
        db.add(dl_alt)

    # Decision on Day 4 for Replay
    dec_alt = DecisionRecord(
        mission_id=alt.id,
        day=4,
        event_id="evt_solar_storm",
        choice_id="deflector_boost",
        choice_title="Overdrive Active Magnetic Deflector",
        impact_summary="Magnetic deflector coils powered to peak flux. Solar storm proton spray successfully repelled; crew safe at 97% health.",
        mentor_notes="Lorentz Force & Magnetic Deflection"
    )
    db.add(dec_alt)
    db.commit()
    db.close()
    print("Database seeded with sample mission and counterfactual replay successfully!")

if __name__ == "__main__":
    seed()

