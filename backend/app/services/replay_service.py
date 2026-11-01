import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.mission import Mission, DayLog, EventLog, DecisionRecord
from app.services.simulation_engine import SimulationEngine
from app.schemas.mission import OutpostAllocation

class ReplayService:
    @staticmethod
    def create_replay_mission(db: Session, parent_mission: Mission) -> Mission:
        """
        Creates a new counterfactual replay mission sharing the exact starting conditions:
        - Same destination
        - Same duration
        - Same difficulty
        - Same initial random seed
        - Same initial outpost budget allocation
        """
        allocation_data = json.loads(parent_mission.initial_allocation)
        allocation = OutpostAllocation(**allocation_data)

        engine = SimulationEngine(seed=parent_mission.seed)
        initial_state = engine.calculate_initial_state(
            destination=parent_mission.destination,
            difficulty=parent_mission.difficulty,
            duration_days=parent_mission.duration_days,
            allocation=allocation
        )

        replay_mission = Mission(
            parent_id=parent_mission.id,
            is_replay=True,
            commander_name=f"{parent_mission.commander_name} (Replay)",
            destination=parent_mission.destination,
            duration_days=parent_mission.duration_days,
            difficulty=parent_mission.difficulty,
            seed=parent_mission.seed,
            status="active",
            current_day=1,
            score=initial_state["score"],
            initial_allocation=parent_mission.initial_allocation,
            state_json=json.dumps({
                "resources": initial_state["resources"].model_dump(),
                "systems": initial_state["systems"].model_dump(),
                "crew": initial_state["crew"].model_dump(),
                "emergency_spares": initial_state["emergency_spares"],
                "objectives": [obj.model_dump() for obj in initial_state["objectives"]],
                "warnings": initial_state["warnings"],
                "recent_logs": initial_state["recent_logs"]
            })
        )
        db.add(replay_mission)
        db.commit()
        db.refresh(replay_mission)

        # Log Day 1 baseline
        day_log = DayLog(
            mission_id=replay_mission.id,
            day=1,
            oxygen=initial_state["resources"].oxygen,
            water=initial_state["resources"].water,
            food=initial_state["resources"].food,
            energy=initial_state["resources"].energy,
            crew_health=initial_state["resources"].crew_health,
            system_condition=initial_state["resources"].system_condition,
            events_summary="Replay Outpost Initialized",
            decisions_summary="Initial state mirrored from parent mission",
            log_messages=json.dumps(initial_state["recent_logs"])
        )
        db.add(day_log)
        db.commit()

        return replay_mission

    @staticmethod
    def compare_runs(db: Session, run_a_id: str, run_b_id: str) -> Dict[str, Any]:
        """
        Generates comprehensive counterfactual comparison between two mission runs.
        """
        run_a = db.query(Mission).filter(Mission.id == run_a_id).first()
        run_b = db.query(Mission).filter(Mission.id == run_b_id).first()

        if not run_a or not run_b:
            raise ValueError("One or both missions not found for comparison.")

        # Ensure run_a is original / parent if applicable
        if run_b.parent_id == run_a.id:
            orig = run_a
            alt = run_b
        elif run_a.parent_id == run_b.id:
            orig = run_b
            alt = run_a
        else:
            orig = run_a
            alt = run_b

        # Day logs for telemetry charts
        orig_logs = db.query(DayLog).filter(DayLog.mission_id == orig.id).order_by(DayLog.day).all()
        alt_logs = db.query(DayLog).filter(DayLog.mission_id == alt.id).order_by(DayLog.day).all()

        # Decision records
        orig_decisions = db.query(DecisionRecord).filter(DecisionRecord.mission_id == orig.id).order_by(DecisionRecord.day).all()
        alt_decisions = db.query(DecisionRecord).filter(DecisionRecord.mission_id == alt.id).order_by(DecisionRecord.day).all()

        # Find decision differences by matching day and event
        decision_divergences = []
        alt_by_day = {d.day: d for d in alt_decisions}
        for d_orig in orig_decisions:
            d_alt = alt_by_day.get(d_orig.day)
            if d_alt and d_alt.choice_id != d_orig.choice_id:
                decision_divergences.append({
                    "day": d_orig.day,
                    "event_id": d_orig.event_id,
                    "original_choice": d_orig.choice_title,
                    "counterfactual_choice": d_alt.choice_title,
                    "divergence_analysis": f"On Day {d_orig.day}, Original chose '{d_orig.choice_title}' while Replay chose '{d_alt.choice_title}'."
                })

        score_diff = alt.score - orig.score
        days_survived_diff = alt.current_day - orig.current_day

        attribution = []
        if score_diff > 50:
            attribution.append(f"Counterfactual replay gained +{score_diff} points due to improved crisis triage and reduced resource depletion.")
        elif score_diff < -50:
            attribution.append(f"Counterfactual replay scored {score_diff} points lower, demonstrating that alternative choices introduced greater operational risk.")
        else:
            attribution.append("Both strategies performed with comparable overall efficiency.")

        if decision_divergences:
            attribution.append(f"Identified {len(decision_divergences)} tactical decision divergence(s) between the two runs.")

        return {
            "is_counterfactual": True,
            "disclaimer": "Simulated Counterfactual Analysis: Outlines alternative outcomes based on simulation engine logic. Not a flight-certified predictive model.",
            "original_run": {
                "mission_id": orig.id,
                "label": "Original Run",
                "status": orig.status,
                "score": orig.score,
                "days_survived": orig.current_day,
                "total_days": orig.duration_days,
                "telemetry": [
                    {
                        "day": l.day,
                        "oxygen": l.oxygen,
                        "water": l.water,
                        "food": l.food,
                        "energy": l.energy,
                        "crew_health": l.crew_health,
                        "system_condition": l.system_condition
                    }
                    for l in orig_logs
                ]
            },
            "counterfactual_run": {
                "mission_id": alt.id,
                "label": "Counterfactual Replay",
                "status": alt.status,
                "score": alt.score,
                "days_survived": alt.current_day,
                "total_days": alt.duration_days,
                "telemetry": [
                    {
                        "day": l.day,
                        "oxygen": l.oxygen,
                        "water": l.water,
                        "food": l.food,
                        "energy": l.energy,
                        "crew_health": l.crew_health,
                        "system_condition": l.system_condition
                    }
                    for l in alt_logs
                ]
            },
            "deltas": {
                "score_delta": score_diff,
                "days_survived_delta": days_survived_diff,
                "decision_divergences": decision_divergences,
                "outcome_attribution": attribution
            }
        }
