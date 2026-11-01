import math
import random
from typing import Dict, Any, Tuple, List, Optional
from app.schemas.mission import (
    ResourceState, SystemState, CrewState, ObjectiveSchema,
    OutpostAllocation, MissionStateResponse, MissionEventSchema
)

"""
SIMULATION ENGINE SPECIFICATION & ASSUMPTIONS:
- Crew Size: 4 astronauts.
- Simulation Units:
  * Oxygen: Expressed as normalized atmospheric buffer (0-100%). Nominal safe range: 75-100%. 
    Critical hypoxia threshold: < 30%. Lethal: 0%.
  * Water: Potable buffer in Liters (nominal max 500L, normalized 0-100%). 
    Crew baseline consumption: 4L/person/day = 16 L/day total. Closed-loop recovery recycles 70-98%.
  * Food: Caloric rations in kg (nominal max 300kg, normalized 0-100%). 
    Crew baseline consumption: ~1.8 kg/person/day = 7.2 kg/day total. Greenhouse offsets up to 75%.
  * Energy: Battery / Generation reserve (0-100%). Outpost baseline draw: 25 kWh/day.
  * Crew Health: Physiological fitness index (0-100%). Under 40% triggers medical emergency.
  * System Integrity: Health of each critical spacecraft subsystem (0-100%).
- Educational Scope:
  * Demonstrates real ECLSS (Environmental Control and Life Support System) trade-offs, 
    energy cascading, and water-loop closure concepts utilized on the ISS and planned Artemis Basecamp.
  * Clearly identified as a simplified educational simulator, not flight-certified software.
"""

class SimulationEngine:
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)

    @staticmethod
    def calculate_initial_state(
        destination: str,
        difficulty: str,
        duration_days: int,
        allocation: OutpostAllocation
    ) -> Dict[str, Any]:
        """Calculates initial outpost resources and system conditions from player credit allocation."""
        # Baseline conversion factors from credits (0-100 total budget)
        # Allocation fields: life_support, power_generation, water_recycling, food_production, radiation_protection, emergency_reserves

        # Difficulty scaling factors
        diff_mult = {
            "beginner": 1.15,
            "intermediate": 1.0,
            "expert": 0.88
        }.get(difficulty.lower(), 1.0)

        # Destination environmental offsets
        # Moon: harsher thermal swings and night cycle, zero atmosphere
        # Mars: dust storms, lower sunlight (43% solar flux of Earth), thin CO2 atmosphere
        env_power_penalty = 5.0 if destination.lower() == "mars" else 2.0
        env_radiation_penalty = 8.0 if destination.lower() == "moon" else 4.0

        # Systems health calculation (0 - 100%)
        power_grid = min(100.0, max(20.0, (allocation.power_generation * 4.2 * diff_mult) - env_power_penalty))
        life_support = min(100.0, max(20.0, allocation.life_support * 4.2 * diff_mult))
        water_recovery = min(100.0, max(20.0, allocation.water_recycling * 4.2 * diff_mult))
        greenhouse = min(100.0, max(15.0, allocation.food_production * 4.0 * diff_mult))
        radiation_shield = min(100.0, max(20.0, (allocation.radiation_protection * 4.2 * diff_mult) - env_radiation_penalty))
        hull_integrity = 95.0

        # Resources initial buffers (0 - 100%)
        oxygen = min(100.0, max(30.0, 50.0 + (allocation.life_support * 2.2 * diff_mult)))
        water = min(100.0, max(30.0, 50.0 + (allocation.water_recycling * 2.2 * diff_mult)))
        food = min(100.0, max(30.0, 50.0 + (allocation.food_production * 2.2 * diff_mult)))
        energy = min(100.0, max(30.0, 50.0 + (allocation.power_generation * 2.2 * diff_mult)))
        crew_health = 100.0

        emergency_spares_count = max(1, int(allocation.emergency_reserves / 8))

        system_condition = round((power_grid + life_support + water_recovery + greenhouse + radiation_shield + hull_integrity) / 6.0, 1)

        objectives = [
            ObjectiveSchema(
                id="obj_survive",
                title="Sustain Crew Health",
                description="Keep crew physiological health above 60% for the entire mission duration.",
                completed=False,
                progress=0.0
            ),
            ObjectiveSchema(
                id="obj_eclss",
                title="Closed-Loop ECLSS Stability",
                description="Maintain Life Support and Water Recycling subsystems in healthy operating condition (>65%).",
                completed=False,
                progress=0.0
            ),
            ObjectiveSchema(
                id="obj_power",
                title="Energy Grid Autonomy",
                description="Prevent catastrophic brownouts; maintain active power reserves above 30%.",
                completed=False,
                progress=0.0
            ),
            ObjectiveSchema(
                id="obj_hull",
                title="Structural Habitat Integrity",
                description="Protect outpost hull and airlock seals against micro-meteorites and wear (>70%).",
                completed=False,
                progress=0.0
            )
        ]

        return {
            "resources": ResourceState(
                oxygen=round(oxygen, 1),
                water=round(water, 1),
                food=round(food, 1),
                energy=round(energy, 1),
                crew_health=round(crew_health, 1),
                system_condition=system_condition
            ),
            "systems": SystemState(
                power_grid=round(power_grid, 1),
                life_support=round(life_support, 1),
                water_recovery=round(water_recovery, 1),
                greenhouse=round(greenhouse, 1),
                radiation_shield=round(radiation_shield, 1),
                hull_integrity=round(hull_integrity, 1)
            ),
            "crew": CrewState(
                crew_count=4,
                morale=100.0,
                radiation_dose_msv=0.0,
                status="nominal"
            ),
            "emergency_spares": emergency_spares_count,
            "objectives": objectives,
            "score": 100,
            "warnings": [],
            "recent_logs": [
                f"Outpost initialized on {destination.capitalize()} at {difficulty.capitalize()} level.",
                f"Allocation confirmed: {emergency_spares_count} emergency reserve spares provisioned.",
                "ECLSS closed-loop habitat pressurization nominal."
            ]
        }

    def advance_day_tick(
        self,
        current_day: int,
        total_days: int,
        destination: str,
        difficulty: str,
        resources: ResourceState,
        systems: SystemState,
        crew: CrewState,
        objectives: List[ObjectiveSchema],
        emergency_spares: int
    ) -> Tuple[ResourceState, SystemState, CrewState, List[ObjectiveSchema], List[str], List[str], Optional[str]]:
        """
        Executes a single 24-hour simulation tick.
        Order of application:
        1. Natural wear & tear
        2. Power generation / battery balance
        3. Cascading power impacts on ECLSS, Water, and Greenhouse
        4. Oxygen consumption & generation
        5. Water consumption & closed-loop filtration
        6. Food consumption & hydroponic replenishment
        7. Ambient radiation & crew physiological check
        8. Objective evaluation
        9. Clamping & failure condition detection
        """
        logs = []
        warnings = []
        failure_reason = None

        # Difficulty burn multipliers
        burn_rate = {
            "beginner": 0.85,
            "intermediate": 1.0,
            "expert": 1.22
        }.get(difficulty.lower(), 1.0)

        # 1. System wear & tear (0.6% - 1.8% daily degradation)
        base_wear = 1.0 * burn_rate
        if destination.lower() == "moon":
            # Regolith abrasion on seals and radiators
            hull_wear = base_wear * 1.2
            power_wear = base_wear * 1.1
        else:
            # Mars fine dust settling on solar optics
            power_wear = base_wear * 1.4
            hull_wear = base_wear * 0.9

        systems.power_grid = max(0.0, systems.power_grid - power_wear)
        systems.life_support = max(0.0, systems.life_support - base_wear)
        systems.water_recovery = max(0.0, systems.water_recovery - (base_wear * 1.1))
        systems.greenhouse = max(0.0, systems.greenhouse - (base_wear * 0.9))
        systems.radiation_shield = max(0.0, systems.radiation_shield - (base_wear * 0.7))
        systems.hull_integrity = max(0.0, systems.hull_integrity - hull_wear)

        # 2. Power Balance: Generation efficiency depends on power_grid condition
        # Outpost consumes ~12% base energy per day.
        # Solar / reactor generation recovers up to 14% if power_grid is 100%.
        daily_power_inflow = (systems.power_grid / 100.0) * 14.0
        daily_power_outflow = 12.0 * burn_rate
        net_energy = daily_power_inflow - daily_power_outflow
        resources.energy = max(0.0, min(100.0, resources.energy + net_energy))

        # 3. Cascading Dependency: Power Grid directly throttles ECLSS & Water pumps
        life_support_eff = (systems.life_support / 100.0)
        water_recovery_eff = (systems.water_recovery / 100.0)

        if resources.energy < 25.0:
            warnings.append("CRITICAL POWER BROWNOUT: ECLSS scrubbers and water pumps operating under emergency low-voltage mode!")
            life_support_eff *= 0.55
            water_recovery_eff *= 0.50
        elif resources.energy < 50.0:
            warnings.append("Power grid strained: Non-essential auxiliary life support throttled.")
            life_support_eff *= 0.80
            water_recovery_eff *= 0.85

        # 4. Oxygen Dynamics
        # Nominal crew consumption: 4% buffer/day. Life support generates based on efficiency.
        o2_consumption = 3.8 * burn_rate
        o2_production = 3.5 * life_support_eff
        net_o2 = o2_production - o2_consumption
        resources.oxygen = max(0.0, min(100.0, resources.oxygen + net_o2))

        # 5. Water Dynamics
        # Nominal crew consumption: 5% buffer/day (16L). Water recovery captures 70-95% of graywater.
        water_consumed = 5.0 * burn_rate
        water_recycled = water_consumed * (0.60 + (0.35 * water_recovery_eff))
        net_water = water_recycled - water_consumed
        resources.water = max(0.0, min(100.0, resources.water + net_water))

        # 6. Food & Greenhouse Dynamics
        # Nominal crew consumption: 4% buffer/day. Greenhouse yields fresh calories if power & water healthy.
        food_consumed = 4.0 * burn_rate
        if resources.water > 30.0 and resources.energy > 30.0:
            greenhouse_yield = 3.5 * (systems.greenhouse / 100.0)
        else:
            greenhouse_yield = 1.0 * (systems.greenhouse / 100.0)
            warnings.append("Greenhouse growth restricted due to water/power rationing.")

        net_food = greenhouse_yield - food_consumed
        resources.food = max(0.0, min(100.0, resources.food + net_food))

        # 7. Radiation & Crew Physiological Impact
        # Base cosmic radiation dose: ~1.5 mSv/day modified by shielding
        shield_factor = max(0.1, systems.radiation_shield / 100.0)
        daily_rad_dose = (1.8 * (1.0 - (shield_factor * 0.85)))
        crew.radiation_dose_msv = round(crew.radiation_dose_msv + daily_rad_dose, 2)

        health_delta = 0.0

        # Hypoxia penalty
        if resources.oxygen < 30.0:
            health_delta -= 12.0
            warnings.append("HYPOXIA ALERT: Crew suffering from acute oxygen deprivation!")
        elif resources.oxygen < 60.0:
            health_delta -= 3.0

        # Dehydration penalty
        if resources.water < 20.0:
            health_delta -= 10.0
            warnings.append("DEHYDRATION ALERT: Crew water rations dangerously depleted!")
        elif resources.water < 40.0:
            health_delta -= 2.5

        # Malnutrition penalty
        if resources.food < 20.0:
            health_delta -= 5.0
            warnings.append("NUTRITIONAL DEFICIT: Crew caloric intake below baseline.")

        # Radiation sickness penalty
        if crew.radiation_dose_msv > 100.0:
            health_delta -= 4.0
            warnings.append("RADIATION HAZARD: Cumulative astronaut radiation exposure exceeds safety threshold.")

        # Natural rest recovery if all needs are met
        if resources.oxygen >= 70.0 and resources.water >= 60.0 and resources.food >= 60.0 and health_delta >= 0:
            health_delta += 1.5 # Slow recuperation

        resources.crew_health = max(0.0, min(100.0, resources.crew_health + health_delta))

        # Update crew status string
        if resources.crew_health > 80.0:
            crew.status = "nominal"
        elif resources.crew_health > 50.0:
            crew.status = "fatigued"
        elif resources.crew_health > 25.0:
            crew.status = "strained"
        else:
            crew.status = "critical"

        # Overall composite system condition
        resources.system_condition = round(
            (systems.power_grid + systems.life_support + systems.water_recovery +
             systems.greenhouse + systems.radiation_shield + systems.hull_integrity) / 6.0, 1
        )

        # 8. Check Objectives
        for obj in objectives:
            if obj.id == "obj_survive":
                obj.progress = min(100.0, round((current_day / total_days) * 100.0, 1))
                obj.completed = (current_day >= total_days and resources.crew_health >= 60.0)
            elif obj.id == "obj_eclss":
                avg_eclss = (systems.life_support + systems.water_recovery) / 2.0
                obj.progress = round(avg_eclss, 1)
                obj.completed = (avg_eclss >= 65.0)
            elif obj.id == "obj_power":
                obj.progress = round(resources.energy, 1)
                obj.completed = (resources.energy >= 30.0)
            elif obj.id == "obj_hull":
                obj.progress = round(systems.hull_integrity, 1)
                obj.completed = (systems.hull_integrity >= 70.0)

        # 9. Failure State Checks
        if resources.oxygen <= 0.0:
            failure_reason = "Mission Failed: Atmospheric oxygen depleted. Catastrophic ECLSS asphyxiation failure."
        elif resources.water <= 0.0:
            failure_reason = "Mission Failed: Potable water exhausted. Terminal dehydration crisis."
        elif resources.crew_health <= 0.0:
            failure_reason = "Mission Failed: Crew completely incapacitated due to medical trauma or severe radiation sickness."
        elif systems.hull_integrity <= 0.0:
            failure_reason = "Mission Failed: Outpost structural hull breach. Catastrophic habitat depressurization."

        # Logging
        logs.append(f"Day {current_day} completed. ECLSS balance: O2 {resources.oxygen:.1f}%, H2O {resources.water:.1f}%, Pwr {resources.energy:.1f}%.")
        if warnings:
            logs.append(f"Warning: {warnings[0]}")

        return resources, systems, crew, objectives, warnings, logs, failure_reason

    def apply_event_decision(
        self,
        event: MissionEventSchema,
        choice_id: str,
        resources: ResourceState,
        systems: SystemState,
        crew: CrewState,
        emergency_spares: int
    ) -> Tuple[ResourceState, SystemState, CrewState, int, str, Dict[str, Any]]:
        """
        Applies consequences of the chosen action for an active event.
        Returns:
            (updated_resources, updated_systems, updated_crew, updated_spares, resolution_text, mentor_data)
        """
        resolution_text = ""
        mentor_data = {}

        # 1. SOLAR RADIATION STORM
        if event.event_type == "solar_radiation_storm":
            if choice_id == "deflector_boost":
                resources.energy = max(0.0, resources.energy - 18.0)
                systems.power_grid = max(0.0, systems.power_grid - 4.0)
                resolution_text = "Magnetic deflector coils powered to peak flux. Solar storm proton spray successfully repelled; crew safe."
                mentor_data = {
                    "what_changed": "Energy reserves reduced by 18%; power grid experienced slight thermal strain (-4%).",
                    "why_it_changed": "Generating an electromagnetic Lorentz deflection field requires significant sustained kilowatt wattage.",
                    "affected_systems": ["power_grid", "energy", "radiation_shield"],
                    "what_to_monitor": "Battery charge levels before entering the next planetary night cycle.",
                    "scientific_concept": "Lorentz Force & Magnetic Deflection: Charged ions (solar protons) are curved away from habitats by artificial magnetic fields, mimicking Earth's magnetosphere."
                }
            elif choice_id == "regolith_bunker":
                resources.crew_health = max(0.0, resources.crew_health - 5.0)
                resources.energy = max(0.0, resources.energy - 5.0)
                crew.morale = max(0.0, crew.morale - 12.0)
                systems.greenhouse = max(0.0, systems.greenhouse - 8.0)
                resolution_text = "Astronauts sheltered in subterranean regolith bunker. Minor psychological confinement strain, zero radiation sickness."
                mentor_data = {
                    "what_changed": "Crew health dipped by 5% from high-stress emergency confinement; greenhouse growth was paused.",
                    "why_it_changed": "Lunar/Martian regolith (at least 2-3 meters depth) provides excellent passive bulk mass shielding against gamma rays.",
                    "affected_systems": ["crew_health", "greenhouse", "morale"],
                    "what_to_monitor": "Astronaut fatigue and greenhouse lighting status.",
                    "scientific_concept": "In-Situ Passive Radiation Attenuation: Planetary regolith is rich in silicates and aluminum oxides, absorbing ionizing radiation without requiring payload launch mass."
                }
            else: # passive_shielding
                resources.crew_health = max(0.0, resources.crew_health - 22.0)
                crew.radiation_dose_msv += 48.0
                systems.power_grid = max(0.0, systems.power_grid - 10.0)
                resolution_text = "Standard outpost hull failed to attenuate full CME flux. Crew suffered ionizing radiation exposure (-22% health, +48 mSv)."
                mentor_data = {
                    "what_changed": "Severe crew physiological degradation (-22% health) and micro-electronics interference.",
                    "why_it_changed": "Standard lightweight spacecraft composite walls alone cannot stop secondary neutron showers from high-energy coronal mass ejections.",
                    "affected_systems": ["crew_health", "power_grid"],
                    "what_to_monitor": "Acute radiation symptoms and medical locker supplies.",
                    "scientific_concept": "Secondary Neutron Showers & Radiation Sickness: Heavy atomic nuclei colliding with aluminum spacecraft hulls create ionizing secondary cascades that damage biological DNA."
                }

        # 2. WATER RECYCLING MALFUNCTION
        elif event.event_type == "water_recycling_malfunction":
            if choice_id == "replace_membrane":
                if emergency_spares > 0:
                    emergency_spares -= 1
                    systems.water_recovery = min(100.0, systems.water_recovery + 35.0)
                    resolution_text = "Installed factory catalytic filter module from emergency reserves. Closed-loop recovery restored to 95%."
                    mentor_data = {
                        "what_changed": "Used 1 emergency spare kit; water recovery loop jumped back to 95%.",
                        "why_it_changed": "Replacing the fouled distillation membrane completely eliminates mineral scale and biofilm clogging.",
                        "affected_systems": ["water_recovery", "emergency_spares"],
                        "what_to_monitor": "Remaining count of emergency spares for future emergencies.",
                        "scientific_concept": "Vapor Compression Distillation: Spacecraft water systems evaporate moisture from urine and sweat, passing vapor through porous hydrophobic membranes to recycle up to 98% of all water."
                    }
                else:
                    # Fallback if no spares
                    resources.water = max(0.0, resources.water - 20.0)
                    systems.water_recovery = max(30.0, systems.water_recovery + 15.0)
                    resolution_text = "No emergency spares available! Performed emergency bypass instead (-20L water)."
                    mentor_data = {
                        "what_changed": "Lost 20L water buffer attempting field repairs without factory parts.",
                        "why_it_changed": "Running out of reserve spares forces reliance on destructive mechanical workarounds.",
                        "affected_systems": ["water", "water_recovery"],
                        "what_to_monitor": "Daily water reserves and crew hydration levels.",
                        "scientific_concept": "Logistics and Spares Mass: Human exploration architecture requires balancing initial launch mass against spare parts wear probability."
                    }
            elif choice_id == "chemical_backwash":
                resources.water = max(0.0, resources.water - 15.0)
                resources.energy = max(0.0, resources.energy - 10.0)
                systems.water_recovery = min(85.0, systems.water_recovery + 25.0)
                resolution_text = "Acid reagents flushed the bioreactor. Filter recovered to 75%, spending 15L flush water and 10% energy."
                mentor_data = {
                    "what_changed": "Water buffer dropped by 15L and energy by 10%; water recycling efficiency improved to 75%.",
                    "why_it_changed": "Chemical dissolution removes precipitate buildup but consumes consumable flush fluids and heating power.",
                    "affected_systems": ["water", "energy", "water_recovery"],
                    "what_to_monitor": "Water recycling efficiency over consecutive days.",
                    "scientific_concept": "Chemical Scale Remediation: High concentrations of calcium sulfate and uric acid in graywater require acidic solutions like phosphoric acid to clear filtration pores."
                }
            else: # ration_and_bypass
                resources.crew_health = max(0.0, resources.crew_health - 10.0)
                crew.morale = max(0.0, crew.morale - 15.0)
                resolution_text = "Filtration membrane bypassed. Crew placed on strict water rationing. Dehydration fatigue observed (-10% health)."
                mentor_data = {
                    "what_changed": "Crew health fell by 10% and morale dropped; water recovery efficiency remains degraded at low capacity.",
                    "why_it_changed": "Humans require at least 2.5L to 3.0L of water daily to maintain renal function and cognitive performance.",
                    "affected_systems": ["crew_health", "morale", "water_recovery"],
                    "what_to_monitor": "Critical dehydration thresholds and crew reaction times.",
                    "scientific_concept": "Human Osmoregulation in Space: Microgravity blunts normal thirst perception, making strict fluid intake vital to prevent kidney stone formation and cardiovascular deconditioning."
                }

        # 3. POWER GENERATION FAILURE
        elif event.event_type == "power_generation_failure":
            if choice_id == "pulse_cleaning":
                resources.energy = max(0.0, resources.energy - 12.0)
                resources.oxygen = max(0.0, resources.oxygen - 6.0)
                systems.power_grid = min(100.0, systems.power_grid + 30.0)
                resolution_text = "Electrodynamic dust pulse cleared solar arrays; fuel cells provided steady backup. Power output restored."
                mentor_data = {
                    "what_changed": "Energy lowered by 12% and Oxygen by 6% (consumed in fuel cell reaction); power grid restored to nominal.",
                    "why_it_changed": "Fuel cells react hydrogen and oxygen to produce instantaneous electricity and pure water when arrays are obscured.",
                    "affected_systems": ["energy", "oxygen", "power_grid"],
                    "what_to_monitor": "Oxygen buffer reserves following fuel cell usage.",
                    "scientific_concept": "Electrodynamic Dust Shield (EDS) & Fuel Cells: High-voltage standing waves displace fine lunar dust without mechanical wipers, while H2/O2 fuel cells provide mission-critical power bridging."
                }
            elif choice_id == "emergency_eva":
                resources.crew_health = max(0.0, resources.crew_health - 14.0)
                systems.power_grid = min(100.0, systems.power_grid + 35.0)
                resolution_text = "Astronauts conducted a 6-hour surface EVA to manually sweep arrays. Power restored, but crew exhausted (-14% health)."
                mentor_data = {
                    "what_changed": "Power grid recovered to 95%, but crew health declined by 14% due to intense EVA physical exertion.",
                    "why_it_changed": "Extravehicular activity in pressurized spacesuits causes severe metabolic strain, hand fatigue, and micro-puncture risks.",
                    "affected_systems": ["power_grid", "crew_health"],
                    "what_to_monitor": "Crew rest cycles and suit seal integrity.",
                    "scientific_concept": "Extravehicular Metabolic Workload: Moving inside a 4.3 psi spacesuit requires constant force against pressurized joints, burning over 400 kcal/hour."
                }
            else: # load_shedding
                systems.greenhouse = max(10.0, systems.greenhouse - 25.0)
                resources.food = max(0.0, resources.food - 10.0)
                resolution_text = "Rolling brownouts initiated. Greenhouse LED grow lights powered down; crop growth halted, preserving core life support."
                mentor_data = {
                    "what_changed": "Greenhouse condition fell by 25% and food supply declined; power grid stabilized without extra energy expenditure.",
                    "why_it_changed": "Photosynthetic LED grow lights consume massive amounts of electric power; shedding them preserves human breathing systems.",
                    "affected_systems": ["greenhouse", "food", "power_grid"],
                    "what_to_monitor": "Food buffer depletion rate over the next several days.",
                    "scientific_concept": "Load Shedding & Hierarchy of Needs: In space life support, breathable atmosphere always takes precedence over food production and science payloads."
                }

        # 4. FOOD SUPPLY SHORTAGE
        elif event.event_type == "food_supply_shortage":
            if choice_id == "uv_sterilization":
                resources.energy = max(0.0, resources.energy - 14.0)
                resources.water = max(0.0, resources.water - 8.0)
                systems.greenhouse = min(90.0, systems.greenhouse + 20.0)
                resolution_text = "UV-C chamber sterilization eradicated fungal mold spores. Hydroponic crop trays stabilized."
                mentor_data = {
                    "what_changed": "Spent 14% energy and 8L water to sanitize hydroponic loops; greenhouse condition rebounded to 80%.",
                    "why_it_changed": "Deep germicidal ultraviolet light destroys fungal pathogen DNA without leaving chemical residues in astronaut food.",
                    "affected_systems": ["energy", "water", "greenhouse"],
                    "what_to_monitor": "Energy storage levels.",
                    "scientific_concept": "Germicidal UV-C Sterilization: Electromagnetic radiation at 254 nm breaks molecular bonds in microbial DNA, preventing crop contagion in closed biological habitats."
                }
            elif choice_id == "strict_rationing":
                resources.crew_health = max(0.0, resources.crew_health - 10.0)
                crew.morale = max(0.0, crew.morale - 15.0)
                systems.greenhouse = max(15.0, systems.greenhouse - 30.0)
                resolution_text = "Infected crop trays jettisoned. Crew placed on strict caloric rationing (-10% health)."
                mentor_data = {
                    "what_changed": "Crew health dropped by 10% and greenhouse condition plummeted to 20%; food rations conserved.",
                    "why_it_changed": "Severely restricting caloric intake causes astronaut muscle wasting and reduced cognitive focus.",
                    "affected_systems": ["crew_health", "greenhouse", "morale"],
                    "what_to_monitor": "Astronaut alertness and physical stamina.",
                    "scientific_concept": "Nutritional Energy Expenditure in Confinement: Astronauts require ~2800 kcal/day; persistent deficits trigger protein catabolism and impaired immune response."
                }
            else: # deploy_seed_spares
                if emergency_spares > 0:
                    emergency_spares -= 1
                    systems.greenhouse = min(85.0, systems.greenhouse + 25.0)
                    resolution_text = "Deployed fast-cycle microgreen seed vaults from emergency reserves. Fresh biomass growth resumed."
                    mentor_data = {
                        "what_changed": "Spent 1 emergency reserve spare; greenhouse stabilized at healthy yield.",
                        "why_it_changed": "Hermetically sealed seed packets provide genetic diversity and rapid replanting capability after biological failures.",
                        "affected_systems": ["greenhouse", "emergency_spares"],
                        "what_to_monitor": "Remaining emergency reserve inventory.",
                        "scientific_concept": "Fast-Cycle Biomass in ECLSS: Dwarf cultivars of radishes and microgreens germinate in days, providing essential fresh vitamins (like vitamin C and folate) prone to radiation decay."
                    }
                else:
                    resources.food = max(0.0, resources.food - 15.0)
                    resolution_text = "No emergency reserves remained! Crops discarded without replenishment (-15% food)."
                    mentor_data = {
                        "what_changed": "Food buffer dropped 15% due to lack of replacement seeds.",
                        "why_it_changed": "Without spare biological stock, lost crops cannot be regenerated.",
                        "affected_systems": ["food"],
                        "what_to_monitor": "Remaining food reserves.",
                        "scientific_concept": "Bioregenerative Redundancy: Space architectures require multi-tiered food strategies combining freeze-dried shelf-stable meals with fresh crop additions."
                    }

        # 5. CREW MEDICAL EMERGENCY
        elif event.event_type == "crew_medical_emergency":
            if choice_id == "hyperbaric_treatment":
                resources.oxygen = max(0.0, resources.oxygen - 15.0)
                resources.energy = max(0.0, resources.energy - 8.0)
                resources.crew_health = min(100.0, resources.crew_health + 15.0)
                resolution_text = "Hyperbaric chamber pressurized with pure oxygen. Nitrogen bubbles dissolved, astronaut fully recovered."
                mentor_data = {
                    "what_changed": "Oxygen buffer reduced by 15% and energy by 8%; crew health jumped back to 95%.",
                    "why_it_changed": "High-pressure hyperbaric oxygen therapy dissolves micro-emboli and hyper-oxygenates hypoxic tissues immediately.",
                    "affected_systems": ["oxygen", "energy", "crew_health"],
                    "what_to_monitor": "Oxygen buffer consumption over the next 48 hours.",
                    "scientific_concept": "Boyle's Law & Decompression Sickness (The Bends): Rapid pressure drops cause dissolved inert nitrogen gas in blood to form obstructive bubbles; hyperbaric repressurization forces bubbles back into solution."
                }
            elif choice_id == "medical_spares":
                if emergency_spares > 0:
                    emergency_spares -= 1
                    resources.crew_health = min(90.0, resources.crew_health + 8.0)
                    resolution_text = "Administered targeted anti-inflammatory drugs and neuro-protectants from emergency medical locker."
                    mentor_data = {
                        "what_changed": "Expended 1 emergency reserve kit; crew health stabilized at 85%.",
                        "why_it_changed": "Pharmaceutical countermeasures mitigate barotrauma symptoms and stabilize vascular tone.",
                        "affected_systems": ["crew_health", "emergency_spares"],
                        "what_to_monitor": "Spares locker quantity and astronaut vitals.",
                        "scientific_concept": "Space Pharmacokinetics: Drug shelf-life and metabolic breakdown are altered by space radiation and altered hepatic blood flow in altered gravity."
                    }
                else:
                    resources.crew_health = max(0.0, resources.crew_health - 12.0)
                    resolution_text = "No medical spares in inventory! Astronaut condition degraded (-12% health)."
                    mentor_data = {
                        "what_changed": "Crew health dropped 12% due to lack of medical supplies.",
                        "why_it_changed": "In deep space, there is no emergency room; untreated barotrauma leads to neurological damage.",
                        "affected_systems": ["crew_health"],
                        "what_to_monitor": "Astronaut vitals.",
                        "scientific_concept": "Autonomous Medical Care in Deep Space: Crew must possess diagnostic tools and therapeutics since evacuation to Earth takes days or months."
                    }
            else: # duty_standdown
                resources.crew_health = max(0.0, resources.crew_health - 16.0)
                systems.power_grid = max(0.0, systems.power_grid - 5.0)
                systems.life_support = max(0.0, systems.life_support - 5.0)
                resolution_text = "Astronaut placed on bedrest without active treatment. Remaining crew overworked; habitat maintenance suffered."
                mentor_data = {
                    "what_changed": "Crew health dropped by 16%; power grid and life support systems degraded by 5% from missed maintenance rotations.",
                    "why_it_changed": "A 4-person crew has zero excess capacity; losing one astronaut doubles the physical maintenance workload on the rest.",
                    "affected_systems": ["crew_health", "power_grid", "life_support"],
                    "what_to_monitor": "Cumulative crew fatigue and missed maintenance tasks.",
                    "scientific_concept": "Crew Resource Management (CRM) & Workload Saturation: Astronaut performance degrades exponentially when sleep-deprived and burdened with compensatory emergency shifts."
                }

        # 6. EQUIPMENT MAINTENANCE FAILURE
        elif event.event_type == "equipment_maintenance_failure":
            if choice_id == "spare_seal_replacement":
                if emergency_spares > 0:
                    emergency_spares -= 1
                    systems.hull_integrity = 98.0
                    resolution_text = "Damaged outer airlock seal replaced with new cryo-polymer gasket. Outpost atmosphere hermetically sealed."
                    mentor_data = {
                        "what_changed": "Expended 1 emergency reserve kit; hull integrity restored to 98%.",
                        "why_it_changed": "Replacing the pitted elastomeric gasket prevents atmospheric gas molecules from venting into deep space vacuum.",
                        "affected_systems": ["hull_integrity", "emergency_spares"],
                        "what_to_monitor": "Spares inventory and airlock pressure telemetry.",
                        "scientific_concept": "Vacuum Outgassing & Seal Degradation: Spacecraft hatch elastomers must resist extreme thermal cycling (-150°C to +120°C) and solar UV embrittlement."
                    }
                else:
                    systems.hull_integrity = 70.0
                    resources.oxygen = max(0.0, resources.oxygen - 10.0)
                    resolution_text = "No spare gasket! Airlock patched with temporary tape; minor oxygen leak persists."
                    mentor_data = {
                        "what_changed": "Hull integrity stands at 70% and oxygen dropped by 10%.",
                        "why_it_changed": "Makeshift adhesives degrade quickly under vacuum pressure differentials.",
                        "affected_systems": ["hull_integrity", "oxygen"],
                        "what_to_monitor": "Daily oxygen consumption rate.",
                        "scientific_concept": "Atmospheric Leak Rates: Small pinhole leaks (0.1 mm) can drain hundreds of kilograms of pressurized gas over a week."
                    }
            elif choice_id == "epoxy_composite_patch":
                resources.energy = max(0.0, resources.energy - 8.0)
                systems.hull_integrity = min(88.0, systems.hull_integrity + 18.0)
                resolution_text = "Injected rapid-cure epoxy resin across the gasket seam and heat-cured. Leak stopped; hull at 88%."
                mentor_data = {
                    "what_changed": "Used 8% energy to heat-cure the patch; hull integrity recovered to 88%.",
                    "why_it_changed": "Thermal curing activates cross-linking polymers to plug fissures under pressure.",
                    "affected_systems": ["energy", "hull_integrity"],
                    "what_to_monitor": "Hatch structural integrity during subsequent airlock repressurization cycles.",
                    "scientific_concept": "Composite In-Situ Repair: Epoxy composites provide rapid temporary pressure vessel repair without full mechanical teardown."
                }
            else: # seal_vestibule
                systems.hull_integrity = 80.0
                crew.morale = max(0.0, crew.morale - 12.0)
                systems.system_condition = max(0.0, systems.system_condition - 6.0)
                resolution_text = "Airlock vestibule locked down and vented. Habitat safe, but surface egress disabled."
                mentor_data = {
                    "what_changed": "Hull integrity secured at 80%, but crew morale fell and outpost operational capacity shrank.",
                    "why_it_changed": "Isolating compromised modules contains catastrophic decompression but sacrifices mission habitable volume and surface access.",
                    "affected_systems": ["hull_integrity", "morale", "system_condition"],
                    "what_to_monitor": "Mission objective progress without surface EVAs.",
                    "scientific_concept": "Compartmentalization & Bulkhead Isolation: Space habitats are divided into hermetic cells so hull breaches can be quarantined without evacuating the entire station."
                }

        # Clamping
        resources.oxygen = max(0.0, min(100.0, resources.oxygen))
        resources.water = max(0.0, min(100.0, resources.water))
        resources.food = max(0.0, min(100.0, resources.food))
        resources.energy = max(0.0, min(100.0, resources.energy))
        resources.crew_health = max(0.0, min(100.0, resources.crew_health))
        resources.system_condition = round(
            (systems.power_grid + systems.life_support + systems.water_recovery +
             systems.greenhouse + systems.radiation_shield + systems.hull_integrity) / 6.0, 1
        )

        return resources, systems, crew, emergency_spares, resolution_text, mentor_data
