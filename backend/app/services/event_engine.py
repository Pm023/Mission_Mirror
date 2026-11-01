import uuid
import random
from typing import Dict, List, Optional
from app.schemas.mission import MissionEventSchema, EventChoiceSchema

# Definitions of all 6 mission events with realistic astronaut engineering trade-offs

EVENT_TEMPLATES = {
    "solar_radiation_storm": {
        "event_type": "solar_radiation_storm",
        "title": "Coronal Mass Ejection: Solar Radiation Storm",
        "description": "Deep space sensors detect a high-energy proton flux heading towards the habitat. Surface radiation levels will spike tenfold within hours.",
        "severity": "high",
        "choices": [
            {
                "id": "deflector_boost",
                "title": "Overdrive Active Magnetic Deflector",
                "description": "Channel auxiliary power into the magnetic deflector coils to repel charged particles.",
                "resource_impact_preview": "-18% Energy, Hull Integrity safe, Crew Health preserved.",
                "tradeoff_summary": "High energy consumption prevents crew radiation dosage."
            },
            {
                "id": "regolith_bunker",
                "title": "Shelter Crew in Regolith Storm Bunker",
                "description": "Sound emergency sirens and order all crew to the deep subterranean bunker. Power down surface experiments.",
                "resource_impact_preview": "-5% Crew Health (confinement stress), -5% Energy, Greenhouse paused.",
                "tradeoff_summary": "Zero equipment damage, minor crew morale/fatigue penalty."
            },
            {
                "id": "passive_shielding",
                "title": "Rely on Passive Outpost Shielding",
                "description": "Keep systems running as normal, trusting the outer habitat wall thickness.",
                "resource_impact_preview": "-22% Crew Health, +45 mSv radiation dose, electronics glitch.",
                "tradeoff_summary": "Saves all resources but inflicts severe radiation damage to crew."
            }
        ]
    },
    "water_recycling_malfunction": {
        "event_type": "water_recycling_malfunction",
        "title": "ECLSS Urine Processor & Graywater Membrane Failure",
        "description": "Mineral scale has clogged the primary vacuum distillation filtration unit. Closed-loop water recovery has dropped to 30%.",
        "severity": "medium",
        "choices": [
            {
                "id": "replace_membrane",
                "title": "Install Spare Filtration Assembly",
                "description": "Expend a high-grade catalytic filter cartridge from emergency reserves to fully restore the loop.",
                "resource_impact_preview": "-1 Emergency Reserve, Water Recovery restored to 95%.",
                "tradeoff_summary": "Consumes valuable spare parts for immediate 100% recovery."
            },
            {
                "id": "chemical_backwash",
                "title": "Initiate Chemical Backwash & Acid Flush",
                "description": "Flush the fouled core with internal acid reagents and flush water to dissolve buildup.",
                "resource_impact_preview": "-25L Water, -10% Energy, Water Recovery restored to 75%.",
                "tradeoff_summary": "Saves emergency parts by spending precious water buffer and power."
            },
            {
                "id": "ration_and_bypass",
                "title": "Ration Potable Water & Bypass Filter",
                "description": "Switch to emergency storage bladders and limit crew drinking rations to 1.5L/day.",
                "resource_impact_preview": "Water loop remains at 40%, Crew Health -8%, Morale drops.",
                "tradeoff_summary": "No resource cost, but crew suffers dehydration stress."
            }
        ]
    },
    "power_generation_failure": {
        "event_type": "power_generation_failure",
        "title": "Surface Power Generation Critical Anomaly",
        "description": "Heavy electrostatically-charged regolith dust has coated primary photovoltaic arrays (or coolant loop cavitation in the reactor). Power output reduced by 50%.",
        "severity": "high",
        "choices": [
            {
                "id": "pulse_cleaning",
                "title": "Electrodynamic Dust Shield Pulse & Fuel Cell Assist",
                "description": "Fire high-voltage dust mitigation pulses across panel surfaces and burn fuel cell reserves.",
                "resource_impact_preview": "-12% Energy buffer, -8% Oxygen (fuel cell burn), Power restored to 90%.",
                "tradeoff_summary": "Consumes buffer reactants to restore solar efficiency without crew risk."
            },
            {
                "id": "emergency_eva",
                "title": "Order Astronauts on Manual Brush EVA",
                "description": "Send two crew members on an emergency extravehicular surface spacewalk to physically sweep the arrays.",
                "resource_impact_preview": "-15% Crew Health (exhaustion/suit wear), Power restored to 95%.",
                "tradeoff_summary": "100% system fix, but strains astronauts and risks suit seal abrasion."
            },
            {
                "id": "load_shedding",
                "title": "Initiate Tier-3 Rolling Load Shedding",
                "description": "Power down greenhouse grow lights, scientific equipment, and non-critical heaters.",
                "resource_impact_preview": "Greenhouse condition -25%, Food production halts, Power grid stabilizes.",
                "tradeoff_summary": "Saves critical life support, but sacrifices food crop yield."
            }
        ]
    },
    "food_supply_shortage": {
        "event_type": "food_supply_shortage",
        "title": "Hydroponic Crop Blight & Microbial Contamination",
        "description": "An airborne fungal mold has infected the aeroponic lettuce and soybean bay, destroying 40% of the active crops.",
        "severity": "medium",
        "choices": [
            {
                "id": "uv_sterilization",
                "title": "UV-C Chamber Sterilization & Re-inoculation",
                "description": "Blast growth chambers with deep ultraviolet sterilization and inject nutrient reserves.",
                "resource_impact_preview": "-15% Energy, -10L Water, Greenhouse recovers to 80%.",
                "tradeoff_summary": "Heavy energy and water expenditure saves remaining crops."
            },
            {
                "id": "strict_rationing",
                "title": "Switch Crew to Emergency Caloric Rations",
                "description": "Purge infected trays completely and enforce half-rationing of sealed pre-packaged meals.",
                "resource_impact_preview": "-10% Crew Health, Food reserves conserved, Greenhouse wiped to 20%.",
                "tradeoff_summary": "Prevents contamination spread, but crew experiences fatigue."
            },
            {
                "id": "deploy_seed_spares",
                "title": "Deploy Fast-Cycle Microgreen Spares",
                "description": "Open sealed freeze-dried seed pods from emergency reserves for rapid 5-day harvest.",
                "resource_impact_preview": "-1 Emergency Reserve, Food supply stabilized, Greenhouse at 70%.",
                "tradeoff_summary": "Consumes emergency reserve to quickly restore fresh food production."
            }
        ]
    },
    "crew_medical_emergency": {
        "event_type": "crew_medical_emergency",
        "title": "Acute Decompression & Confinement Medical Crisis",
        "description": "A crew specialist exhibits symptoms of barotrauma and severe acute hypercapnia (elevated bloodstream CO2) following airlock cycling.",
        "severity": "critical",
        "choices": [
            {
                "id": "hyperbaric_treatment",
                "title": "Hyperbaric Oxygen Chamber Repressurization",
                "description": "Place astronaut in airlock chamber at 1.4 atm with 100% pure oxygen therapy for 12 hours.",
                "resource_impact_preview": "-16% Oxygen reserve, -10% Energy, Crew Health fully restored to 95%.",
                "tradeoff_summary": "High consumable expenditure saves astronaut with zero lasting impairment."
            },
            {
                "id": "medical_spares",
                "title": "Administer Telemedicine Medical Countermeasures",
                "description": "Use prescription drug injectors and automated vitals monitor from emergency medical lockers.",
                "resource_impact_preview": "-1 Emergency Reserve, Crew Health recovers to 80%.",
                "tradeoff_summary": "Conserves oxygen buffer at the expense of limited medical supplies."
            },
            {
                "id": "duty_standdown",
                "title": "Enforce Strict Bedrest & Spread Workload",
                "description": "Isolate the astronaut with standard first aid and require remaining crew to take double shifts.",
                "resource_impact_preview": "-18% Crew Health across team, Morale drops, Systems wear +5%.",
                "tradeoff_summary": "Zero resource cost, but crew exhaustion degrades habitat maintenance."
            }
        ]
    },
    "equipment_maintenance_failure": {
        "event_type": "equipment_maintenance_failure",
        "title": "Airlock Micrometeoroid Pitting & Pressure Seal Leak",
        "description": "A high-velocity micro-debris particle has scored the outer hatch silicone gasket, causing a continuous pressure bleed of 0.3 kPa/hr.",
        "severity": "high",
        "choices": [
            {
                "id": "spare_seal_replacement",
                "title": "Install Cryo-Polymer Hatch Replacement Gasket",
                "description": "Depressurize vestibule and replace the damaged seal assembly with a factory spare.",
                "resource_impact_preview": "-1 Emergency Reserve, Hull Integrity restored to 100%.",
                "tradeoff_summary": "Permanent factory repair using precious emergency hardware."
            },
            {
                "id": "epoxy_composite_patch",
                "title": "Rapid Epoxy Sealant Patch & Thermal Cure",
                "description": "Inject expanding structural adhesive over the rupture and cure with thermal heat lamps.",
                "resource_impact_preview": "-8% Energy, Hull Integrity at 85%, minor leak risk remains.",
                "tradeoff_summary": "Fast, cheap repair that leaves slight structural vulnerability."
            },
            {
                "id": "seal_vestibule",
                "title": "Condemn and Isolate Outer Airlock Vestibule",
                "description": "Lock dog-latches on secondary bulkhead and vent vestibule to space. Restrict EVAs.",
                "resource_impact_preview": "Hull safe, Outpost functional capacity -15%, Morale -10%.",
                "tradeoff_summary": "No resources spent, but permanently restricts surface mission access."
            }
        ]
    }
}

class EventEngine:
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)

    def should_trigger_event(self, day: int, total_days: int, difficulty: str, existing_event_days: List[int]) -> bool:
        """Determines if a dynamic event triggers today based on schedule and difficulty."""
        if day in existing_event_days or day == 1 or day == total_days:
            # Day 1 is initial settling day; final day is debrief
            return False

        # Target number of events based on duration and difficulty
        difficulty_multipliers = {
            "beginner": 0.15,     # ~1-2 events for 10d, 2-3 for 20d
            "intermediate": 0.25, # ~2-3 events for 10d, 4-5 for 20d
            "expert": 0.38        # ~3-4 events for 10d, 7-8 for 20d
        }
        chance = difficulty_multipliers.get(difficulty.lower(), 0.25)
        return self.rng.random() < chance

    def select_event(self, used_event_types: List[str], destination: str) -> MissionEventSchema:
        """Selects an appropriate event template, favoring unused events."""
        all_keys = list(EVENT_TEMPLATES.keys())
        unused = [k for k in all_keys if k not in used_event_types]
        
        selected_key = self.rng.choice(unused) if unused else self.rng.choice(all_keys)
        template = EVENT_TEMPLATES[selected_key]
        
        choices = [
            EventChoiceSchema(
                id=c["id"],
                title=c["title"],
                description=c["description"],
                resource_impact_preview=c["resource_impact_preview"],
                tradeoff_summary=c["tradeoff_summary"]
            )
            for c in template["choices"]
        ]
        
        return MissionEventSchema(
            id=f"evt_{selected_key}_{uuid.uuid4().hex[:12]}",
            event_type=template["event_type"],
            title=f"[{destination.upper()}] {template['title']}",
            description=template["description"],
            severity=template["severity"],
            choices=choices,
            resolved=False,
            chosen_choice_id=None,
            day_triggered=0
        )
