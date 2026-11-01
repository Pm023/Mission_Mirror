import logging
from typing import Dict, Any, List, Optional
import httpx
from app.config import settings
from app.schemas.mission import MentorAdvice

logger = logging.getLogger("mentor_service")

class MentorService:
    @staticmethod
    async def generate_explanation(
        simulation_mentor_data: Dict[str, Any],
        decision_title: str,
        event_title: str,
        current_day: int,
        destination: str
    ) -> MentorAdvice:
        """
        Generates explainable mission mentor feedback.
        Uses deterministic simulation data as ground truth.
        Attempts optional LLM enrichment if configured, with instant fallback to rule-based analysis.
        """
        # Base deterministic ground-truth values
        what_changed = simulation_mentor_data.get("what_changed", "Mission resources updated.")
        why_it_changed = simulation_mentor_data.get("why_it_changed", "Actions consumed buffer reserves.")
        affected_systems = simulation_mentor_data.get("affected_systems", ["outpost"])
        what_to_monitor = simulation_mentor_data.get("what_to_monitor", "Review life support telemetry.")
        scientific_concept = simulation_mentor_data.get("scientific_concept", "Spacecraft resource triage.")

        # If LLM is not configured, return immediately with deterministic rule-based mentor
        if not settings.LLM_PROVIDER or not settings.LLM_API_KEY:
            return MentorAdvice(
                what_changed=what_changed,
                why_it_changed=why_it_changed,
                affected_systems=affected_systems,
                what_to_monitor=what_to_monitor,
                scientific_concept=scientific_concept,
                source="rule_based"
            )

        # Attempt optional LLM call with strict timeout and fallback
        try:
            if settings.LLM_PROVIDER.lower() == "gemini":
                # Google Gemini API
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent?key={settings.LLM_API_KEY}"
                prompt = (
                    f"You are the Mission Mentor for Junior Astronauts on {destination.capitalize()}.\n"
                    f"Event: {event_title}\n"
                    f"Decision taken: {decision_title}\n"
                    f"Simulated factual effects:\n"
                    f"- What changed: {what_changed}\n"
                    f"- Why it changed: {why_it_changed}\n"
                    f"- Scientific concept: {scientific_concept}\n"
                    f"Task: Provide an encouraging, pedagogical 2-sentence cadet debrief explaining the scientific principle. "
                    f"Do not invent new numbers or contradict the facts."
                )
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 200}
                }
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        ai_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        return MentorAdvice(
                            what_changed=what_changed,
                            why_it_changed=f"{why_it_changed} ({ai_text})",
                            affected_systems=affected_systems,
                            what_to_monitor=what_to_monitor,
                            scientific_concept=scientific_concept,
                            source="ai_model"
                        )
            elif settings.LLM_PROVIDER.lower() == "openai":
                # OpenAI Compatible API
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {settings.LLM_API_KEY}"}
                payload = {
                    "model": settings.LLM_MODEL if "gpt" in settings.LLM_MODEL else "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are an encouraging NASA mission mentor explaining spacecraft engineering to junior astronauts."},
                        {"role": "user", "content": f"Event: {event_title}. Decision: {decision_title}. Factual outcome: {what_changed}. Scientific principle: {scientific_concept}. Give a concise 2-sentence educational insight."}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 150
                }
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        ai_text = data["choices"][0]["message"]["content"].strip()
                        return MentorAdvice(
                            what_changed=what_changed,
                            why_it_changed=f"{why_it_changed} ({ai_text})",
                            affected_systems=affected_systems,
                            what_to_monitor=what_to_monitor,
                            scientific_concept=scientific_concept,
                            source="ai_model"
                        )
        except Exception as e:
            logger.warning(f"Optional LLM provider failed, falling back to rule-based mentor: {e}")

        # Fallback to rule-based
        return MentorAdvice(
            what_changed=what_changed,
            why_it_changed=why_it_changed,
            affected_systems=affected_systems,
            what_to_monitor=what_to_monitor,
            scientific_concept=scientific_concept,
            source="rule_based"
        )
