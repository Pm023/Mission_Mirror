from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.science_service import ScienceService

router = APIRouter(prefix="/api/science", tags=["Science"])

@router.get("/resources", response_model=List[Dict[str, Any]])
def get_science_resources():
    """Returns curated educational science modules with verified open-access NASA citations."""
    return ScienceService.get_all_science_topics()

@router.get("/resources/{topic_id}")
def get_science_topic(topic_id: str):
    """Returns details for a specific science module."""
    return ScienceService.get_topic_by_id(topic_id)
