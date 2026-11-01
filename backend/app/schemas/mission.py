from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any

class ObjectiveSchema(BaseModel):
    id: str
    title: str
    description: str
    completed: bool = False
    progress: float = 0.0 # 0.0 to 100.0

class ResourceState(BaseModel):
    oxygen: float = Field(..., description="Oxygen storage / atmospheric buffer (0-100%)")
    water: float = Field(..., description="Available potable & reserve water (Liters, 0-500L, indexed 0-100%)")
    food: float = Field(..., description="Nutritional rations buffer (kg, 0-300kg, indexed 0-100%)")
    energy: float = Field(..., description="Power generation / battery storage state (0-100%)")
    crew_health: float = Field(..., description="Overall crew physiological health (0-100%)")
    system_condition: float = Field(..., description="Composite spacecraft integrity score (0-100%)")

class SystemState(BaseModel):
    power_grid: float = Field(..., description="Solar/Nuclear array efficiency (0-100%)")
    life_support: float = Field(..., description="CO2 scrubbers & O2 generation status (0-100%)")
    water_recovery: float = Field(..., description="Urine and condensate recovery efficiency (0-100%)")
    greenhouse: float = Field(..., description="Hydroponic growth chamber condition (0-100%)")
    radiation_shield: float = Field(..., description="Regolith & active magnetic deflection condition (0-100%)")
    hull_integrity: float = Field(..., description="Outpost seal and structural health (0-100%)")

class CrewState(BaseModel):
    crew_count: int = 4
    morale: float = 100.0
    radiation_dose_msv: float = 0.0
    status: str = "nominal" # nominal, fatigued, injured, critical

class EventChoiceSchema(BaseModel):
    id: str
    title: str
    description: str
    resource_impact_preview: str
    tradeoff_summary: str

class MissionEventSchema(BaseModel):
    id: str
    event_type: str # solar_storm, water_malfunction, power_failure, food_shortage, crew_medical, maintenance_failure
    title: str
    description: str
    severity: str # low, medium, high, critical
    choices: List[EventChoiceSchema]
    resolved: bool = False
    chosen_choice_id: Optional[str] = None
    day_triggered: int
    resolution_summary: Optional[str] = None

class MissionCreate(BaseModel):
    destination: str = Field(..., description="'moon' or 'mars'")
    duration_days: int = Field(..., description="10, 20, or 30 days")
    difficulty: str = Field(..., description="'beginner', 'intermediate', or 'expert'")
    commander_name: str = Field(default="Cadet Explorer")
    seed: Optional[int] = Field(default=None, description="Deterministic seed for simulation events")

    @field_validator('destination')
    def validate_destination(cls, v):
        if v.lower() not in ['moon', 'mars', 'station']:
            raise ValueError("Destination must be 'moon', 'mars', or 'station'")
        return v.lower()

    @field_validator('duration_days')
    def validate_duration(cls, v):
        if v not in [10, 20, 30]:
            raise ValueError("Duration must be 10, 20, or 30 days")
        return v

    @field_validator('difficulty')
    def validate_difficulty(cls, v):
        if v.lower() not in ['beginner', 'intermediate', 'expert']:
            raise ValueError("Difficulty must be 'beginner', 'intermediate', or 'expert'")
        return v.lower()

class OutpostAllocation(BaseModel):
    life_support: int = Field(..., ge=0, le=100)
    power_generation: int = Field(..., ge=0, le=100)
    water_recycling: int = Field(..., ge=0, le=100)
    food_production: int = Field(..., ge=0, le=100)
    radiation_protection: int = Field(..., ge=0, le=100)
    emergency_reserves: int = Field(..., ge=0, le=100)

    @field_validator('emergency_reserves')
    def validate_total_budget(cls, v, info):
        values = info.data
        total = (
            values.get('life_support', 0) +
            values.get('power_generation', 0) +
            values.get('water_recycling', 0) +
            values.get('food_production', 0) +
            values.get('radiation_protection', 0) +
            v
        )
        if total > 100:
            raise ValueError(f"Total budget allocation cannot exceed 100 simulation credits. Current total: {total}")
        if total < 50:
            raise ValueError(f"Outpost requires at least 50 credits allocated for viable deployment. Current total: {total}")
        return v

class DecisionSubmit(BaseModel):
    choice_id: str

class MentorAdvice(BaseModel):
    what_changed: str
    why_it_changed: str
    affected_systems: List[str]
    what_to_monitor: str
    scientific_concept: str
    source: str = "rule_based" # "rule_based" or "ai_model"

class MissionStateResponse(BaseModel):
    mission_id: str
    parent_mission_id: Optional[str] = None
    is_replay: bool = False
    status: str # briefing, planning, active, completed, failed, evacuated
    failure_reason: Optional[str] = None
    current_day: int
    total_days: int
    destination: str
    difficulty: str
    commander_name: str
    score: int
    resources: ResourceState
    systems: SystemState
    crew: CrewState
    active_event: Optional[MissionEventSchema] = None
    warnings: List[str] = []
    objectives: List[ObjectiveSchema] = []
    recent_logs: List[str] = []
    completed_exploration_objectives: List[str] = []
    mentor_advice: Optional[MentorAdvice] = None
    can_advance: bool = True

class MissionSummary(BaseModel):
    id: str
    parent_id: Optional[str] = None
    destination: str
    duration_days: int
    difficulty: str
    commander_name: str
    status: str
    score: int
    current_day: int
    created_at: str
    is_replay: bool = False

class DependencyNode(BaseModel):
    id: str
    name: str
    category: str
    status: str # healthy, warning, critical
    value: float
    unit: str
    impacts: List[str]
    depended_by: List[str]
    description: str

class DependencyGraphResponse(BaseModel):
    nodes: List[DependencyNode]
    edges: List[Dict[str, str]] # {"source": "power_grid", "target": "water_recovery", "relationship": "Provides pump energy"}

class DayTelemetry(BaseModel):
    day: int
    oxygen: float
    water: float
    food: float
    energy: float
    crew_health: float
    system_condition: float
    events_occurred: List[str] = []
    decisions_made: List[str] = []

class MissionDebriefReport(BaseModel):
    mission_id: str
    parent_mission_id: Optional[str] = None
    is_replay: bool
    commander_name: str
    destination: str
    difficulty: str
    outcome: str # "Mission Success", "Mission Failure", "Emergency Evacuation"
    failure_reason: Optional[str] = None
    final_score: int
    grade: str # A+, A, B, C, Needs Retraining
    days_survived: int
    total_days: int
    objectives_completed: int
    total_objectives: int
    telemetry_history: List[DayTelemetry]
    key_decisions: List[Dict[str, Any]]
    lessons_learned: List[str]
    recommended_challenge: str
    counterfactual_comparison: Optional[Dict[str, Any]] = None
