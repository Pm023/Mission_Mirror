from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.mentor_service import MentorService
from app.schemas.mission import MentorAdvice

router = APIRouter(prefix="/api/mentor", tags=["Mentor"])

class MentorExplainRequest(BaseModel):
    event_title: str
    decision_title: str
    destination: str = "moon"
    current_day: int = 1
    what_changed: str
    why_it_changed: str
    scientific_concept: str
    affected_systems: List[str] = ["life_support"]
    what_to_monitor: str = "Oxygen levels"

@router.post("/explain", response_model=MentorAdvice)
async def explain_decision(req: MentorExplainRequest):
    """Explains consequences of an astronaut decision with pedagogical principles."""
    sim_data = {
        "what_changed": req.what_changed,
        "why_it_changed": req.why_it_changed,
        "affected_systems": req.affected_systems,
        "what_to_monitor": req.what_to_monitor,
        "scientific_concept": req.scientific_concept
    }
    advice = await MentorService.generate_explanation(
        simulation_mentor_data=sim_data,
        decision_title=req.decision_title,
        event_title=req.event_title,
        current_day=req.current_day,
        destination=req.destination
    )
    return advice
