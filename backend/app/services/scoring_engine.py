from typing import Dict, Any, List
from app.schemas.mission import DayTelemetry, ResourceState, SystemState, CrewState

class ScoringEngine:
    @staticmethod
    def calculate_score(
        status: str,
        current_day: int,
        total_days: int,
        difficulty: str,
        resources: ResourceState,
        systems: SystemState,
        crew: CrewState,
        objectives_completed: int,
        total_objectives: int
    ) -> Dict[str, Any]:
        """
        Calculates mission score, letter grade, and pedagogical evaluation.
        Base points: 1000 max.
        - Survival & Duration: up to 350 pts
        - Crew Health & Safety: up to 250 pts
        - Resource Sustainability: up to 200 pts
        - Objectives: up to 200 pts
        - Difficulty multiplier
        """
        diff_multipliers = {
            "beginner": 1.0,
            "intermediate": 1.25,
            "expert": 1.5
        }
        mult = diff_multipliers.get(difficulty.lower(), 1.0)

        if status == "failed":
            survival_pts = int((current_day / total_days) * 150)
            health_pts = int(resources.crew_health * 0.5)
            resource_pts = int((resources.oxygen + resources.water + resources.energy) * 0.2)
            obj_pts = objectives_completed * 20
            total_score = max(50, int((survival_pts + health_pts + resource_pts + obj_pts) * mult))
            grade = "Needs Retraining"
        else:
            # Survived or completed
            survival_pts = int((current_day / total_days) * 350)
            health_pts = int((resources.crew_health / 100.0) * 250)
            
            avg_res = (resources.oxygen + resources.water + resources.food + resources.energy) / 4.0
            resource_pts = int((avg_res / 100.0) * 200)

            obj_pts = int((objectives_completed / max(1, total_objectives)) * 200)

            total_score = int((survival_pts + health_pts + resource_pts + obj_pts) * mult)

            if total_score >= 1200:
                grade = "A+ (Commander Honor Roll)"
            elif total_score >= 1000:
                grade = "A (Distinguished Flight Cadet)"
            elif total_score >= 800:
                grade = "B (Qualified Surface Astronaut)"
            elif total_score >= 600:
                grade = "C (Passable Surface Operator)"
            else:
                grade = "D (Marginal Pass)"

        lessons = ScoringEngine._generate_lessons(resources, systems, crew, status)
        challenge = ScoringEngine._recommend_next_challenge(difficulty, grade, status)

        return {
            "final_score": total_score,
            "grade": grade,
            "breakdown": {
                "survival_points": survival_pts,
                "health_points": health_pts,
                "resource_points": resource_pts,
                "objective_points": obj_pts,
                "difficulty_bonus_multiplier": mult
            },
            "lessons_learned": lessons,
            "recommended_challenge": challenge
        }

    @staticmethod
    def _generate_lessons(resources: ResourceState, systems: SystemState, crew: CrewState, status: str) -> List[str]:
        lessons = []
        if status == "failed":
            lessons.append("Mission ended prematurely. In deep space, resource buffers represent your life expectancy—never allow consumable margins to dip below safety reserve thresholds.")
        else:
            lessons.append("Successful surface mission execution demonstrates the power of proactive systems monitoring and balanced resource triage.")

        if resources.oxygen < 50.0:
            lessons.append("Oxygen reserves reached low levels. Life support scrubbers need higher priority during outpost budget allocation and emergency events.")
        elif resources.oxygen >= 80.0:
            lessons.append("Excellent atmospheric management: closed-loop oxygen scrubbers maintained safe partial pressures throughout.")

        if resources.water < 45.0:
            lessons.append("Potable water margins were narrow. Closed-loop graywater recovery is vital—every drop lost must be hauled from Earth at extreme expense.")

        if systems.power_grid < 60.0:
            lessons.append("Power grid suffered significant strain. Without electrical power, life support scrubbers and hydroponic grow lights fail in cascading sequence.")

        if crew.radiation_dose_msv > 50.0:
            lessons.append(f"Cumulative crew radiation dose reached {crew.radiation_dose_msv:.1f} mSv. Deep regolith shielding and rapid shelter response are essential against solar particle events.")

        if len(lessons) < 3:
            lessons.append("System interdependency is key: energy generation powers environmental control, which in turn preserves human cognitive capability.")

        return lessons

    @staticmethod
    def _recommend_next_challenge(difficulty: str, grade: str, status: str) -> str:
        if status == "failed":
            return "Replay this mission scenario with counterfactual adjustments: allocate more budget into Emergency Reserves and Power Generation, or take shelter earlier during radiation events."
        if difficulty == "beginner":
            return "Promote to Intermediate Mission: 20 days on Mars, managing dust-storm induced solar power degradation and crop cultivation."
        elif difficulty == "intermediate":
            return "Advance to Expert Challenge: 30-day Lunar Outpost with extreme 14-day night thermal cycles, abrasive regolith wear, and unpredictable CME storms."
        else:
            return "Master Class: Replay on Expert difficulty aiming for A+ (score > 1200) by perfecting closed-loop water recovery and zero crew radiation sickness."
