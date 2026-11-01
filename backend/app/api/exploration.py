import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.mission import Mission, DecisionRecord
from app.schemas.exploration import (
    ExplorationObjective,
    ExplorationActionRequest,
    ExplorationActionResult
)
from app.services.exploration_service import ExplorationService, OBJECTIVES_DATABASE

router = APIRouter(prefix="/api/exploration", tags=["Exploration"])

@router.get("/objectives/{environment}", response_model=List[ExplorationObjective])
def get_objectives(
    environment: str,
    mission_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Returns the list of 3D interactive field objectives for the specified environment
    ('moon', 'mars', or 'station'). If mission_id is provided, marks already completed objectives.
    """
    completed_ids = []
    if mission_id:
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        if mission and mission.state_json:
            try:
                state_dict = json.loads(mission.state_json)
                completed_ids = state_dict.get("completed_exploration_objectives", [])
            except Exception:
                pass

    return ExplorationService.get_objectives_for_environment(environment, completed_ids)


@router.post("/sandbox/action", response_model=ExplorationActionResult)
def execute_sandbox_action(req: ExplorationActionRequest):
    """
    Executes an interactive EVA action in free-roam cadet sandbox mode (without an active mission).
    Returns real resource trade-offs and verified NASA scientific concepts.
    """
    # Create baseline initial training outpost state
    mock_state: Dict[str, Any] = {
        "mission_id": "sandbox-cadet",
        "status": "training",
        "commander_name": "Cadet Explorer",
        "score": 100,
        "emergency_spares": 2,
        "resources": {
            "oxygen": 85.0,
            "water": 80.0,
            "food": 85.0,
            "energy": 90.0,
            "crew_health": 95.0,
            "system_condition": 90.0
        },
        "systems": {
            "power_grid": 88.0,
            "life_support": 90.0,
            "water_recovery": 88.0,
            "greenhouse": 85.0,
            "radiation_shield": 92.0,
            "hull_integrity": 95.0
        },
        "crew": {
            "crew_count": 4,
            "morale": 95.0,
            "radiation_dose_msv": 2.5,
            "status": "nominal"
        },
        "objectives": [
            {
                "id": "obj_survive",
                "title": "Sustain Crew Health",
                "description": "Keep crew physiological health above 60%.",
                "completed": True,
                "progress": 95.0
            },
            {
                "id": "obj_eclss",
                "title": "Closed-Loop ECLSS Stability",
                "description": "Maintain Life Support and Water Recycling subsystems in healthy condition.",
                "completed": True,
                "progress": 89.0
            },
            {
                "id": "obj_power",
                "title": "Energy Grid Continuity",
                "description": "Maintain power generation buffer above critical reserve levels.",
                "completed": True,
                "progress": 90.0
            }
        ],
        "completed_exploration_objectives": [],
        "recent_logs": ["Sandbox cadet EVA simulation active."]
    }

    try:
        result = ExplorationService.resolve_action(
            objective_id=req.objective_id,
            option_id=req.option_id,
            state_dict=mock_state,
            duration_days=10,
            difficulty="beginner",
            current_day=1
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.post("/missions/{mission_id}/action", response_model=ExplorationActionResult)
def execute_mission_exploration_action(
    mission_id: str,
    req: ExplorationActionRequest,
    db: Session = Depends(get_db)
):
    """
    Executes an interactive 3D EVA action linked to an active persistent mission.
    Validates choice, deducts EVA resources, updates systems, boosts score, and persists state.
    """
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    if not mission.state_json:
        raise HTTPException(status_code=400, detail="Mission has no initialized state; deploy outpost first.")

    try:
        state_dict = json.loads(mission.state_json)
    except Exception:
        raise HTTPException(status_code=500, detail="Corrupted mission state JSON")

    # Check if objective is already completed in this mission
    completed_objs = state_dict.get("completed_exploration_objectives", [])
    if req.objective_id in completed_objs:
        raise HTTPException(
            status_code=400,
            detail=f"Objective '{req.objective_id}' has already been completed during this mission."
        )

    try:
        result = ExplorationService.resolve_action(
            objective_id=req.objective_id,
            option_id=req.option_id,
            state_dict=state_dict,
            duration_days=mission.duration_days,
            difficulty=mission.difficulty,
            current_day=mission.current_day
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

    # Update database record
    mission.score = result.updated_state.score
    mission.state_json = json.dumps(state_dict)

    # Record decision audit trail
    record = DecisionRecord(
        mission_id=mission.id,
        day=mission.current_day,
        event_id=f"eva_{req.objective_id}",
        choice_id=req.option_id,
        choice_title=result.option_title,
        impact_summary=f"{result.outcome_title}: {result.scientific_concept}",
        mentor_notes=f"NASA Reference: {result.nasa_reference}"
    )
    db.add(record)
    db.commit()

    return result

