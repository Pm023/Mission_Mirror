import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Mission(Base):
    __tablename__ = "missions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String(36), ForeignKey("missions.id"), nullable=True)
    is_replay = Column(Boolean, default=False)
    commander_name = Column(String(100), default="Cadet Explorer")
    destination = Column(String(20), nullable=False)
    duration_days = Column(Integer, nullable=False)
    difficulty = Column(String(20), nullable=False)
    seed = Column(Integer, nullable=False)
    status = Column(String(20), default="planning") # planning, active, completed, failed, evacuated
    failure_reason = Column(String(255), nullable=True)
    current_day = Column(Integer, default=0)
    score = Column(Integer, default=100)
    
    # Serialized JSON representations
    initial_allocation = Column(Text, nullable=True) # JSON
    state_json = Column(Text, nullable=True) # Full current state JSON
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    day_logs = relationship("DayLog", back_populates="mission", cascade="all, delete-orphan", order_by="DayLog.day")
    event_logs = relationship("EventLog", back_populates="mission", cascade="all, delete-orphan", order_by="EventLog.day")
    decisions = relationship("DecisionRecord", back_populates="mission", cascade="all, delete-orphan", order_by="DecisionRecord.day")
    replays = relationship("Mission", backref="parent_mission", remote_side=[id])

class DayLog(Base):
    __tablename__ = "day_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mission_id = Column(String(36), ForeignKey("missions.id"), nullable=False)
    day = Column(Integer, nullable=False)
    oxygen = Column(Float, nullable=False)
    water = Column(Float, nullable=False)
    food = Column(Float, nullable=False)
    energy = Column(Float, nullable=False)
    crew_health = Column(Float, nullable=False)
    system_condition = Column(Float, nullable=False)
    events_summary = Column(Text, default="")
    decisions_summary = Column(Text, default="")
    log_messages = Column(Text, default="[]") # JSON list of strings

    mission = relationship("Mission", back_populates="day_logs")

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String(36), ForeignKey("missions.id"), nullable=False)
    day = Column(Integer, nullable=False)
    event_type = Column(String(50), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    choices_json = Column(Text, nullable=False) # JSON list
    chosen_choice_id = Column(String(50), nullable=True)
    outcome_notes = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)

    mission = relationship("Mission", back_populates="event_logs")

class DecisionRecord(Base):
    __tablename__ = "decision_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String(36), ForeignKey("missions.id"), nullable=False)
    day = Column(Integer, nullable=False)
    event_id = Column(String(36), nullable=False)
    choice_id = Column(String(50), nullable=False)
    choice_title = Column(String(150), nullable=False)
    impact_summary = Column(Text, nullable=False)
    mentor_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    mission = relationship("Mission", back_populates="decisions")
