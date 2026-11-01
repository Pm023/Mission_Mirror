import json
import random
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.mission import Mission, DayLog, EventLog, DecisionRecord
from app.schemas.mission import (
    MissionCreate, OutpostAllocation, DecisionSubmit,
    MissionStateResponse, MissionSummary, MissionDebriefReport,
    DependencyGraphResponse, DependencyNode, DayTelemetry,
    ResourceState, SystemState, CrewState, ObjectiveSchema,
    MissionEventSchema, EventChoiceSchema
)
from app.services.simulation_engine import SimulationEngine
from app.services.event_engine import EventEngine
from app.services.scoring_engine import ScoringEngine
from app.services.mentor_service import MentorService
from app.services.replay_service import ReplayService
from app.services.science_service import ScienceService

router = APIRouter(prefix="/api/missions", tags=["Missions"])

@router.post("", response_model=MissionStateResponse)
def create_mission(req: MissionCreate, db: Session = Depends(get_db)):
    """Initializes a new space mission briefing."""
    seed = req.seed if req.seed is not None else random.randint(10000, 99999)
    
    new_mission = Mission(
        destination=req.destination,
        duration_days=req.duration_days,
        difficulty=req.difficulty,
        commander_name=req.commander_name,
        seed=seed,
        status="planning",
        current_day=0,
        score=100
    )
    db.add(new_mission)
    db.commit()
    db.refresh(new_mission)

    # Empty initial resource placeholder before allocation
    resources = ResourceState(oxygen=100.0, water=100.0, food=100.0, energy=100.0, crew_health=100.0, system_condition=100.0)
    systems = SystemState(power_grid=100.0, life_support=100.0, water_recovery=100.0, greenhouse=100.0, radiation_shield=100.0, hull_integrity=100.0)
    crew = CrewState()

    return MissionStateResponse(
        mission_id=new_mission.id,
        is_replay=False,
        status=new_mission.status,
        current_day=0,
        total_days=new_mission.duration_days,
        destination=new_mission.destination,
        difficulty=new_mission.difficulty,
        commander_name=new_mission.commander_name,
        score=100,
        resources=resources,
        systems=systems,
        crew=crew,
        recent_logs=["Mission briefing established. Awaiting outpost budget allocation."]
    )

@router.get("", response_model=List[MissionSummary])
def list_missions(limit: int = 20, db: Session = Depends(get_db)):
    """Lists recent mission runs."""
    missions = db.query(Mission).order_by(Mission.created_at.desc()).limit(limit).all()
    return [
        MissionSummary(
            id=m.id,
            parent_id=m.parent_id,
            destination=m.destination,
            duration_days=m.duration_days,
            difficulty=m.difficulty,
            commander_name=m.commander_name,
            status=m.status,
            score=m.score,
            current_day=m.current_day,
            created_at=m.created_at.strftime("%Y-%m-%d %H:%M"),
            is_replay=m.is_replay
        )
        for m in missions
    ]

@router.get("/{mission_id}", response_model=MissionSummary)
def get_mission(mission_id: str, db: Session = Depends(get_db)):
    """Gets summary for a specific mission."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return MissionSummary(
        id=mission.id,
        parent_id=mission.parent_id,
        destination=mission.destination,
        duration_days=mission.duration_days,
        difficulty=mission.difficulty,
        commander_name=mission.commander_name,
        status=mission.status,
        score=mission.score,
        current_day=mission.current_day,
        created_at=mission.created_at.strftime("%Y-%m-%d %H:%M"),
        is_replay=mission.is_replay
    )

@router.post("/{mission_id}/deploy", response_model=MissionStateResponse)
def deploy_outpost(mission_id: str, allocation: OutpostAllocation, db: Session = Depends(get_db)):
    """Allocates 100-credit budget and deploys the surface outpost systems."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.status != "planning":
        raise HTTPException(status_code=400, detail=f"Cannot deploy outpost; status is {mission.status}")

    engine = SimulationEngine(seed=mission.seed)
    initial_state = engine.calculate_initial_state(
        destination=mission.destination,
        difficulty=mission.difficulty,
        duration_days=mission.duration_days,
        allocation=allocation
    )

    mission.initial_allocation = json.dumps(allocation.model_dump())
    mission.status = "active"
    mission.current_day = 1
    mission.score = initial_state["score"]
    mission.state_json = json.dumps({
        "resources": initial_state["resources"].model_dump(),
        "systems": initial_state["systems"].model_dump(),
        "crew": initial_state["crew"].model_dump(),
        "emergency_spares": initial_state["emergency_spares"],
        "objectives": [obj.model_dump() for obj in initial_state["objectives"]],
        "warnings": initial_state["warnings"],
        "recent_logs": initial_state["recent_logs"]
    })
    db.commit()

    # Log Day 1
    day_log = DayLog(
        mission_id=mission.id,
        day=1,
        oxygen=initial_state["resources"].oxygen,
        water=initial_state["resources"].water,
        food=initial_state["resources"].food,
        energy=initial_state["resources"].energy,
        crew_health=initial_state["resources"].crew_health,
        system_condition=initial_state["resources"].system_condition,
        events_summary="Outpost Initialized",
        decisions_summary="Initial budget allocation confirmed",
        log_messages=json.dumps(initial_state["recent_logs"])
    )
    db.add(day_log)
    db.commit()

    return MissionStateResponse(
        mission_id=mission.id,
        parent_mission_id=mission.parent_id,
        is_replay=mission.is_replay,
        status=mission.status,
        current_day=mission.current_day,
        total_days=mission.duration_days,
        destination=mission.destination,
        difficulty=mission.difficulty,
        commander_name=mission.commander_name,
        score=mission.score,
        resources=initial_state["resources"],
        systems=initial_state["systems"],
        crew=initial_state["crew"],
        objectives=initial_state["objectives"],
        warnings=initial_state["warnings"],
        recent_logs=initial_state["recent_logs"],
        can_advance=True
    )

@router.get("/{mission_id}/state", response_model=MissionStateResponse)
def get_mission_state(mission_id: str, db: Session = Depends(get_db)):
    """Retrieves full current state of the simulation."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    if not mission.state_json:
        # Pre-deployment briefing state
        res = ResourceState(oxygen=100.0, water=100.0, food=100.0, energy=100.0, crew_health=100.0, system_condition=100.0)
        sys = SystemState(power_grid=100.0, life_support=100.0, water_recovery=100.0, greenhouse=100.0, radiation_shield=100.0, hull_integrity=100.0)
        return MissionStateResponse(
            mission_id=mission.id,
            parent_mission_id=mission.parent_id,
            is_replay=mission.is_replay,
            status=mission.status,
            current_day=0,
            total_days=mission.duration_days,
            destination=mission.destination,
            difficulty=mission.difficulty,
            commander_name=mission.commander_name,
            score=mission.score,
            resources=res,
            systems=sys,
            crew=CrewState(),
            can_advance=False
        )

    state_dict = json.loads(mission.state_json)
    active_event = None
    if "active_event" in state_dict and state_dict["active_event"]:
        active_event = MissionEventSchema(**state_dict["active_event"])

    return MissionStateResponse(
        mission_id=mission.id,
        parent_mission_id=mission.parent_id,
        is_replay=mission.is_replay,
        status=mission.status,
        failure_reason=mission.failure_reason,
        current_day=mission.current_day,
        total_days=mission.duration_days,
        destination=mission.destination,
        difficulty=mission.difficulty,
        commander_name=mission.commander_name,
        score=mission.score,
        resources=ResourceState(**state_dict["resources"]),
        systems=SystemState(**state_dict["systems"]),
        crew=CrewState(**state_dict["crew"]),
        active_event=active_event,
        warnings=state_dict.get("warnings", []),
        objectives=[ObjectiveSchema(**o) for o in state_dict.get("objectives", [])],
        recent_logs=state_dict.get("recent_logs", []),
        completed_exploration_objectives=state_dict.get("completed_exploration_objectives", []),
        can_advance=(active_event is None and mission.status == "active")
    )

@router.post("/{mission_id}/advance", response_model=MissionStateResponse)
def advance_day(mission_id: str, db: Session = Depends(get_db)):
    """Advances the simulation by 1 day tick (24 hours)."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.status != "active":
        raise HTTPException(status_code=400, detail=f"Cannot advance: Mission status is '{mission.status}'")

    state_dict = json.loads(mission.state_json)
    if state_dict.get("active_event") and not state_dict["active_event"].get("resolved", False):
        raise HTTPException(status_code=400, detail="Cannot advance while an unresolved dynamic event requires commander action.")

    current_day = mission.current_day + 1
    engine = SimulationEngine(seed=mission.seed + current_day)
    event_engine = EventEngine(seed=mission.seed + current_day)

    resources = ResourceState(**state_dict["resources"])
    systems = SystemState(**state_dict["systems"])
    crew = CrewState(**state_dict["crew"])
    objectives = [ObjectiveSchema(**o) for o in state_dict["objectives"]]
    emergency_spares = state_dict.get("emergency_spares", 2)

    # Execute simulation tick
    resources, systems, crew, objectives, warnings, logs, failure = engine.advance_day_tick(
        current_day=current_day,
        total_days=mission.duration_days,
        destination=mission.destination,
        difficulty=mission.difficulty,
        resources=resources,
        systems=systems,
        crew=crew,
        objectives=objectives,
        emergency_spares=emergency_spares
    )

    mission.current_day = current_day
    new_active_event = None

    if failure:
        mission.status = "failed"
        mission.failure_reason = failure
        logs.append(failure)
    elif current_day >= mission.duration_days:
        mission.status = "completed"
        logs.append(f"Mission complete! Outpost survived full {mission.duration_days}-day surface operation.")
    else:
        # Check dynamic event trigger
        existing_event_days = [e.day for e in mission.event_logs]
        used_event_types = [e.event_type for e in mission.event_logs]

        if event_engine.should_trigger_event(current_day, mission.duration_days, mission.difficulty, existing_event_days):
            new_active_event = event_engine.select_event(used_event_types, mission.destination)
            new_active_event.day_triggered = current_day
            
            # Persist event log
            event_log = EventLog(
                id=new_active_event.id,
                mission_id=mission.id,
                day=current_day,
                event_type=new_active_event.event_type,
                title=new_active_event.title,
                description=new_active_event.description,
                severity=new_active_event.severity,
                choices_json=json.dumps([c.model_dump() for c in new_active_event.choices]),
                resolved=False
            )
            db.add(event_log)
            logs.append(f"CRITICAL ANOMALY: {new_active_event.title}")

    # Re-evaluate live score
    obj_completed_count = sum(1 for o in objectives if o.completed)
    score_data = ScoringEngine.calculate_score(
        status=mission.status,
        current_day=mission.current_day,
        total_days=mission.duration_days,
        difficulty=mission.difficulty,
        resources=resources,
        systems=systems,
        crew=crew,
        objectives_completed=obj_completed_count,
        total_objectives=len(objectives)
    )
    mission.score = score_data["final_score"]

    # Save state
    updated_state = {
        "resources": resources.model_dump(),
        "systems": systems.model_dump(),
        "crew": crew.model_dump(),
        "emergency_spares": emergency_spares,
        "objectives": [obj.model_dump() for obj in objectives],
        "warnings": warnings,
        "recent_logs": logs[-6:],
        "active_event": new_active_event.model_dump() if new_active_event else None
    }
    mission.state_json = json.dumps(updated_state)

    # Persist daily log
    day_log = DayLog(
        mission_id=mission.id,
        day=current_day,
        oxygen=resources.oxygen,
        water=resources.water,
        food=resources.food,
        energy=resources.energy,
        crew_health=resources.crew_health,
        system_condition=resources.system_condition,
        events_summary=new_active_event.title if new_active_event else "Nominal Operations",
        decisions_summary="",
        log_messages=json.dumps(logs)
    )
    db.add(day_log)
    db.commit()

    return MissionStateResponse(
        mission_id=mission.id,
        parent_mission_id=mission.parent_id,
        is_replay=mission.is_replay,
        status=mission.status,
        failure_reason=mission.failure_reason,
        current_day=mission.current_day,
        total_days=mission.duration_days,
        destination=mission.destination,
        difficulty=mission.difficulty,
        commander_name=mission.commander_name,
        score=mission.score,
        resources=resources,
        systems=systems,
        crew=crew,
        active_event=new_active_event,
        warnings=warnings,
        objectives=objectives,
        recent_logs=logs[-6:],
        completed_exploration_objectives=state_dict.get("completed_exploration_objectives", []),
        can_advance=(new_active_event is None and mission.status == "active")
    )

@router.post("/{mission_id}/decisions", response_model=MissionStateResponse)
async def submit_decision(mission_id: str, dec: DecisionSubmit, db: Session = Depends(get_db)):
    """Resolves an active event choice and updates simulation state with mentor feedback."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.status != "active":
        raise HTTPException(status_code=400, detail="Cannot submit decision: Mission is not active")

    state_dict = json.loads(mission.state_json)
    active_event_dict = state_dict.get("active_event")
    if not active_event_dict:
        raise HTTPException(status_code=400, detail="No active event pending a decision")

    event = MissionEventSchema(**active_event_dict)
    choice = next((c for c in event.choices if c.id == dec.choice_id), None)
    if not choice:
        raise HTTPException(status_code=400, detail=f"Invalid choice '{dec.choice_id}' for event '{event.id}'")

    engine = SimulationEngine(seed=mission.seed + mission.current_day)
    resources = ResourceState(**state_dict["resources"])
    systems = SystemState(**state_dict["systems"])
    crew = CrewState(**state_dict["crew"])
    emergency_spares = state_dict.get("emergency_spares", 2)

    # Apply consequences
    resources, systems, crew, emergency_spares, resolution_text, mentor_data = engine.apply_event_decision(
        event=event,
        choice_id=dec.choice_id,
        resources=resources,
        systems=systems,
        crew=crew,
        emergency_spares=emergency_spares
    )

    # Generate explainable mentor feedback
    mentor_advice = await MentorService.generate_explanation(
        simulation_mentor_data=mentor_data,
        decision_title=choice.title,
        event_title=event.title,
        current_day=mission.current_day,
        destination=mission.destination
    )

    # Update event log
    event_db = db.query(EventLog).filter(EventLog.id == event.id).first()
    if event_db:
        event_db.resolved = True
        event_db.chosen_choice_id = dec.choice_id
        event_db.outcome_notes = resolution_text

    # Record decision
    decision_rec = DecisionRecord(
        mission_id=mission.id,
        day=mission.current_day,
        event_id=event.id,
        choice_id=dec.choice_id,
        choice_title=choice.title,
        impact_summary=resolution_text,
        mentor_notes=mentor_advice.scientific_concept
    )
    db.add(decision_rec)

    # Check if this caused failure (e.g. oxygen dropped to 0)
    failure_reason = None
    if resources.oxygen <= 0:
        failure_reason = "Mission Failed: Oxygen depleted following emergency action."
    elif resources.crew_health <= 0:
        failure_reason = "Mission Failed: Crew incapacitation."
    
    if failure_reason:
        mission.status = "failed"
        mission.failure_reason = failure_reason

    # Recalculate score
    objectives = [ObjectiveSchema(**o) for o in state_dict["objectives"]]
    obj_completed_count = sum(1 for o in objectives if o.completed)
    score_data = ScoringEngine.calculate_score(
        status=mission.status,
        current_day=mission.current_day,
        total_days=mission.duration_days,
        difficulty=mission.difficulty,
        resources=resources,
        systems=systems,
        crew=crew,
        objectives_completed=obj_completed_count,
        total_objectives=len(objectives)
    )
    mission.score = score_data["final_score"]

    logs = state_dict.get("recent_logs", [])
    logs.append(f"DECISION: {choice.title} -> {resolution_text}")

    # Clear active event since it's resolved
    updated_state = {
        "resources": resources.model_dump(),
        "systems": systems.model_dump(),
        "crew": crew.model_dump(),
        "emergency_spares": emergency_spares,
        "objectives": [obj.model_dump() for obj in objectives],
        "warnings": state_dict.get("warnings", []),
        "recent_logs": logs[-6:],
        "active_event": None
    }
    mission.state_json = json.dumps(updated_state)
    db.commit()

    return MissionStateResponse(
        mission_id=mission.id,
        parent_mission_id=mission.parent_id,
        is_replay=mission.is_replay,
        status=mission.status,
        failure_reason=mission.failure_reason,
        current_day=mission.current_day,
        total_days=mission.duration_days,
        destination=mission.destination,
        difficulty=mission.difficulty,
        commander_name=mission.commander_name,
        score=mission.score,
        resources=resources,
        systems=systems,
        crew=crew,
        active_event=None,
        warnings=state_dict.get("warnings", []),
        objectives=objectives,
        recent_logs=logs[-6:],
        completed_exploration_objectives=state_dict.get("completed_exploration_objectives", []),
        mentor_advice=mentor_advice,
        can_advance=(mission.status == "active")
    )

@router.get("/{mission_id}/systems", response_model=DependencyGraphResponse)
def get_system_dependencies(mission_id: str, db: Session = Depends(get_db)):
    """Returns interactive dependency graph nodes and edges with real-time status."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission or not mission.state_json:
        # Default nominal topology
        nodes = [
            DependencyNode(id="power_grid", name="Power Generation", category="Energy", status="healthy", value=100.0, unit="%", impacts=["Water Recovery", "Life Support", "Greenhouse"], depended_by=[], description="Solar and reactor energy grid"),
            DependencyNode(id="life_support", name="Life Support (ECLSS)", category="Atmosphere", status="healthy", value=100.0, unit="%", impacts=["Crew Health", "Oxygen"], depended_by=["Power Generation"], description="CO2 scrubbing and O2 generation"),
            DependencyNode(id="water_recovery", name="Water Recycling", category="Hydrology", status="healthy", value=100.0, unit="%", impacts=["Water Buffer", "Greenhouse"], depended_by=["Power Generation"], description="Urine processor & graywater filtration"),
            DependencyNode(id="greenhouse", name="Hydroponic Food", category="Biomass", status="healthy", value=100.0, unit="%", impacts=["Food Buffer"], depended_by=["Power Generation", "Water Recycling"], description="Aeroponic crops & calorie production"),
            DependencyNode(id="radiation_shield", name="Radiation Shield", category="Defense", status="healthy", value=100.0, unit="%", impacts=["Crew Health"], depended_by=[], description="Regolith mass & active magnetic deflector"),
            DependencyNode(id="crew_health", name="Crew Vitals", category="Human", status="healthy", value=100.0, unit="%", impacts=["Mission Success"], depended_by=["Life Support", "Water Buffer", "Radiation Shield"], description="Astronaut physiological condition")
        ]
        edges = [
            {"source": "power_grid", "target": "life_support", "relationship": "Provides 28V/120V bus power"},
            {"source": "power_grid", "target": "water_recovery", "relationship": "Drives distillation vacuum pump"},
            {"source": "power_grid", "target": "greenhouse", "relationship": "Powers photosynthetic LED grow lamps"},
            {"source": "water_recovery", "target": "greenhouse", "relationship": "Delivers mineralized irrigation water"},
            {"source": "life_support", "target": "crew_health", "relationship": "Maintains breathable pO2 and pCO2"},
            {"source": "radiation_shield", "target": "crew_health", "relationship": "Attenuates ionizing GCR/SPE flux"}
        ]
        return DependencyGraphResponse(nodes=nodes, edges=edges)

    state = json.loads(mission.state_json)
    sys = state["systems"]
    res = state["resources"]

    def status_label(val: float) -> str:
        if val >= 70.0:
            return "healthy"
        if val >= 40.0:
            return "warning"
        return "critical"

    nodes = [
        DependencyNode(
            id="power_grid",
            name="Power Generation",
            category="Energy",
            status=status_label(sys["power_grid"]),
            value=sys["power_grid"],
            unit="%",
            impacts=["Water Recovery", "Life Support", "Greenhouse"],
            depended_by=[],
            description="Supplies electrical energy for pumps, heaters, scrubbers, and lighting."
        ),
        DependencyNode(
            id="life_support",
            name="Life Support (ECLSS)",
            category="Atmosphere",
            status=status_label(sys["life_support"]),
            value=sys["life_support"],
            unit="%",
            impacts=["Oxygen Buffer", "Crew Health"],
            depended_by=["Power Generation"],
            description="Regenerates breathable O2 and scrubs toxic CO2 from habitat air."
        ),
        DependencyNode(
            id="water_recovery",
            name="Water Recycling",
            category="Hydrology",
            status=status_label(sys["water_recovery"]),
            value=sys["water_recovery"],
            unit="%",
            impacts=["Water Buffer", "Greenhouse"],
            depended_by=["Power Generation"],
            description="Recovers potable water from crew urine, sweat, and humidity condensate."
        ),
        DependencyNode(
            id="greenhouse",
            name="Hydroponic Food",
            category="Biomass",
            status=status_label(sys["greenhouse"]),
            value=sys["greenhouse"],
            unit="%",
            impacts=["Food Buffer"],
            depended_by=["Power Generation", "Water Recycling"],
            description="Cultivates fresh crops and microgreens, augmenting packaged rations."
        ),
        DependencyNode(
            id="radiation_shield",
            name="Radiation Shield",
            category="Defense",
            status=status_label(sys["radiation_shield"]),
            value=sys["radiation_shield"],
            unit="%",
            impacts=["Crew Health"],
            depended_by=[],
            description="In-situ regolith overburden and active magnetic deflection coils."
        ),
        DependencyNode(
            id="hull_integrity",
            name="Habitat Hull & Seals",
            category="Structure",
            status=status_label(sys["hull_integrity"]),
            value=sys["hull_integrity"],
            unit="%",
            impacts=["Atmospheric Seal"],
            depended_by=[],
            description="Pressurized bulkhead barrier resisting vacuum and micrometeorite impacts."
        ),
        DependencyNode(
            id="crew_health",
            name="Crew Physiological Health",
            category="Human",
            status=status_label(res["crew_health"]),
            value=res["crew_health"],
            unit="%",
            impacts=["Mission Survivability"],
            depended_by=["Life Support", "Water Buffer", "Radiation Shield"],
            description="Vital health index reflecting oxygenation, hydration, and radiation dose."
        )
    ]

    edges = [
        {"source": "power_grid", "target": "life_support", "relationship": "Provides high-voltage scrubber power"},
        {"source": "power_grid", "target": "water_recovery", "relationship": "Powers vacuum distillation compressor"},
        {"source": "power_grid", "target": "greenhouse", "relationship": "Powers photosynthetic LED grow lamps"},
        {"source": "water_recovery", "target": "greenhouse", "relationship": "Supplies irrigation water"},
        {"source": "life_support", "target": "crew_health", "relationship": "Maintains breathable pO2 and pCO2"},
        {"source": "radiation_shield", "target": "crew_health", "relationship": "Attenuates ionizing radiation flux"},
        {"source": "hull_integrity", "target": "life_support", "relationship": "Maintains 101.3 kPa pressure vessel"}
    ]

    return DependencyGraphResponse(nodes=nodes, edges=edges)

@router.post("/{mission_id}/replay", response_model=MissionStateResponse)
def trigger_replay(mission_id: str, db: Session = Depends(get_db)):
    """
    Forks a mission run into a counterfactual replay:
    Starts from the exact original scenario, destination, duration, difficulty,
    initial budget allocation, and event triggers, allowing the cadet to test alternative choices.
    """
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if not mission.initial_allocation:
        raise HTTPException(status_code=400, detail="Cannot replay a mission that was never deployed.")

    replay_mission = ReplayService.create_replay_mission(db, mission)

    state_dict = json.loads(replay_mission.state_json)
    return MissionStateResponse(
        mission_id=replay_mission.id,
        parent_mission_id=mission.id,
        is_replay=True,
        status=replay_mission.status,
        current_day=replay_mission.current_day,
        total_days=replay_mission.duration_days,
        destination=replay_mission.destination,
        difficulty=replay_mission.difficulty,
        commander_name=replay_mission.commander_name,
        score=replay_mission.score,
        resources=ResourceState(**state_dict["resources"]),
        systems=SystemState(**state_dict["systems"]),
        crew=CrewState(**state_dict["crew"]),
        objectives=[ObjectiveSchema(**o) for o in state_dict["objectives"]],
        warnings=state_dict["warnings"],
        recent_logs=state_dict["recent_logs"],
        can_advance=True
    )

@router.get("/{mission_id}/compare/{other_mission_id}")
def compare_counterfactual(mission_id: str, other_mission_id: str, db: Session = Depends(get_db)):
    """Returns side-by-side counterfactual analysis between two mission runs."""
    try:
        comparison = ReplayService.compare_runs(db, mission_id, other_mission_id)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{mission_id}/report", response_model=MissionDebriefReport)
def get_mission_report(mission_id: str, db: Session = Depends(get_db)):
    """Generates the comprehensive Mission Debrief and Learning Report."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    state_dict = json.loads(mission.state_json) if mission.state_json else {}
    resources = ResourceState(**state_dict["resources"]) if "resources" in state_dict else ResourceState(oxygen=0, water=0, food=0, energy=0, crew_health=0, system_condition=0)
    systems = SystemState(**state_dict["systems"]) if "systems" in state_dict else SystemState(power_grid=0, life_support=0, water_recovery=0, greenhouse=0, radiation_shield=0, hull_integrity=0)
    crew = CrewState(**state_dict["crew"]) if "crew" in state_dict else CrewState()
    objectives = [ObjectiveSchema(**o) for o in state_dict.get("objectives", [])]

    obj_completed_count = sum(1 for o in objectives if o.completed)
    score_eval = ScoringEngine.calculate_score(
        status=mission.status,
        current_day=mission.current_day,
        total_days=mission.duration_days,
        difficulty=mission.difficulty,
        resources=resources,
        systems=systems,
        crew=crew,
        objectives_completed=obj_completed_count,
        total_objectives=len(objectives)
    )

    day_logs = db.query(DayLog).filter(DayLog.mission_id == mission.id).order_by(DayLog.day).all()
    decisions = db.query(DecisionRecord).filter(DecisionRecord.mission_id == mission.id).order_by(DecisionRecord.day).all()

    telemetry = [
        DayTelemetry(
            day=dl.day,
            oxygen=dl.oxygen,
            water=dl.water,
            food=dl.food,
            energy=dl.energy,
            crew_health=dl.crew_health,
            system_condition=dl.system_condition,
            events_occurred=[dl.events_summary] if dl.events_summary else [],
            decisions_made=[dl.decisions_summary] if dl.decisions_summary else []
        )
        for dl in day_logs
    ]

    key_decisions = [
        {
            "day": d.day,
            "choice": d.choice_title,
            "impact": d.impact_summary,
            "scientific_concept": d.mentor_notes
        }
        for d in decisions
    ]

    counterfactual_data = None
    if mission.parent_id:
        try:
            counterfactual_data = ReplayService.compare_runs(db, mission.parent_id, mission.id)
        except Exception:
            pass

    outcome_str = "Mission Success" if mission.status == "completed" else ("Mission Terminated: Failure" if mission.status == "failed" else "Mission In Progress")

    return MissionDebriefReport(
        mission_id=mission.id,
        parent_mission_id=mission.parent_id,
        is_replay=mission.is_replay,
        commander_name=mission.commander_name,
        destination=mission.destination,
        difficulty=mission.difficulty,
        outcome=outcome_str,
        failure_reason=mission.failure_reason,
        final_score=score_eval["final_score"],
        grade=score_eval["grade"],
        days_survived=mission.current_day,
        total_days=mission.duration_days,
        objectives_completed=obj_completed_count,
        total_objectives=len(objectives),
        telemetry_history=telemetry,
        key_decisions=key_decisions,
        lessons_learned=score_eval["lessons_learned"],
        recommended_challenge=score_eval["recommended_challenge"],
        counterfactual_comparison=counterfactual_data
    )

@router.get("/{mission_id}/events")
def get_mission_events(mission_id: str, db: Session = Depends(get_db)):
    """Returns event history for this mission."""
    events = db.query(EventLog).filter(EventLog.mission_id == mission_id).order_by(EventLog.day).all()
    return [
        {
            "id": e.id,
            "day": e.day,
            "event_type": e.event_type,
            "title": e.title,
            "description": e.description,
            "severity": e.severity,
            "chosen_choice_id": e.chosen_choice_id,
            "outcome_notes": e.outcome_notes,
            "resolved": e.resolved
        }
        for e in events
    ]
