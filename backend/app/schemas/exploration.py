from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.schemas.mission import MissionStateResponse

class ObjectiveOption(BaseModel):
    id: str
    title: str
    description: str
    resource_impact_preview: str
    tradeoff_summary: str

class ExplorationObjective(BaseModel):
    id: str
    environment: str # "moon", "mars", "station"
    title: str
    target_name: str
    category: str
    description: str
    scientific_concept: str
    nasa_fact: str
    coordinates: Dict[str, float] # {"x": 20.0, "y": 0.0, "z": -25.0}
    options: List[ObjectiveOption]
    completed: bool = False
    chosen_option_id: Optional[str] = None
    outcome_summary: Optional[str] = None

class ExplorationActionRequest(BaseModel):
    objective_id: str
    option_id: str

class ExplorationActionResult(BaseModel):
    success: bool
    objective_id: str
    environment: str
    option_title: str
    outcome_title: str
    outcome_description: str
    scientific_concept: str
    nasa_reference: str
    resource_deltas: Dict[str, float]
    score_delta: int
    updated_state: MissionStateResponse
