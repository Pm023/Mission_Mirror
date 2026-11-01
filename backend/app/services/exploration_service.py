from typing import Dict, List, Any, Optional
from app.schemas.exploration import ExplorationObjective, ObjectiveOption, ExplorationActionResult
from app.schemas.mission import MissionStateResponse, ResourceState, SystemState, CrewState, ObjectiveSchema
from app.services.scoring_engine import ScoringEngine
import json

OBJECTIVES_DATABASE: Dict[str, List[Dict[str, Any]]] = {
    "moon": [
        {
            "id": "moon_solar_array",
            "environment": "moon",
            "title": "Inspect Photovoltaic Solar Array",
            "target_name": "Solar Array Alpha",
            "category": "Power & Regolith Mitigation",
            "description": "Fine, abrasive lunar regolith dust has settled on the solar panel glass after airlock cycling, reducing photovoltaic conversion efficiency.",
            "scientific_concept": "Photoelectric Effect & Regolith Adhesion: Electrostatic solar wind charges abrasive lunar dust, causing it to cling tenaciously to dielectric glass surfaces.",
            "nasa_fact": "NASA's Apollo missions reported lunar dust was one of the greatest operational hazards, clogging mechanical joints and degrading radiator thermal properties.",
            "coordinates": {"x": 24.0, "y": 0.0, "z": -22.0},
            "options": [
                {
                    "id": "piezo_pulse",
                    "title": "Activate Ultrasonic Piezoelectric Pulse",
                    "description": "Send high-frequency standing waves across the cover-glass to loosen adhering charged dust particles without mechanical scratching.",
                    "resource_impact_preview": "-8% Energy, Power Grid restored +18%, +45 Score",
                    "tradeoff_summary": "Uses electrical energy to clean panels cleanly without physical EVA abrasion."
                },
                {
                    "id": "manual_brush",
                    "title": "Perform Astronaut Manual Brush Pass",
                    "description": "Use astronaut carbon-fiber brushes to sweep arrays physically. Heavy physical suit work.",
                    "resource_impact_preview": "-10% Crew Health (fatigue), Power Grid restored +22%, +50 Score",
                    "tradeoff_summary": "Saves energy but exerts physical astronaut stamina and risks suit abrasive wear."
                },
                {
                    "id": "passive_bias",
                    "title": "Apply Passive Electrostatic Repulsion Bias",
                    "description": "Charge the outer conductive grid to a positive potential, slowly repelling daytime solar dust.",
                    "resource_impact_preview": "-2% Energy, Power Grid restored +8%, +25 Score",
                    "tradeoff_summary": "Low power expenditure, but slow and partial dust clearance."
                }
            ]
        },
        {
            "id": "moon_power_fault",
            "environment": "moon",
            "title": "Diagnose Habitat Power Conduit Junction",
            "target_name": "Power Conduit Junction Hub",
            "category": "Electrical Infrastructure",
            "description": "Thermal cycling in the lunar vacuum (-130°C to +120°C) has caused thermal expansion strain on the primary DC power bus connection.",
            "scientific_concept": "Vacuum Thermal Expansion & Soldering Fatigue: Spacecraft electronics experience extreme temperature swings with no convective air cooling, leading to junction micro-fractures.",
            "nasa_fact": "On Artemis basecamps, power management systems must operate across 14-day lunar night cryogenic freezes and blistering equatorial sun.",
            "coordinates": {"x": -16.0, "y": 0.0, "z": -12.0},
            "options": [
                {
                    "id": "aux_bus_divert",
                    "title": "Reroute Through Auxiliary Cryo-Bus",
                    "description": "Switch load to secondary isolated conduit line and apply thermal insulation wrap.",
                    "resource_impact_preview": "-6% Energy, Life Support +14%, +40 Score",
                    "tradeoff_summary": "Channels reserve power to permanently stabilize the habitat life-support circuit."
                },
                {
                    "id": "spare_junction_swap",
                    "title": "Install Factory Spare Connector Module",
                    "description": "Expend a factory-sealed solid-state connector from outpost emergency reserves.",
                    "resource_impact_preview": "-1 Emergency Spare, Power Grid +25%, +60 Score",
                    "tradeoff_summary": "Consumes valuable spare hardware for an immediate 100% factory repair."
                },
                {
                    "id": "load_throttling",
                    "title": "Throttle Subsystem Voltage & Derate Bus",
                    "description": "Operate conduit at 75% rated load to limit heating. Greenhouse grow lights dimmed.",
                    "resource_impact_preview": "Greenhouse -8%, Power Grid stable, +20 Score",
                    "tradeoff_summary": "Zero resource cost, but reduces hydroponic crop growth rate."
                }
            ]
        },
        {
            "id": "moon_soil_sample",
            "environment": "moon",
            "title": "Collect Lunar Regolith Ice-Core Sample",
            "target_name": "Cold Trap Sampling Site",
            "category": "In-Situ Resource Utilization (ISRU)",
            "description": "Deploy scientific core drill into permanently shadowed crater rim regolith to extract volatile water-ice crystals.",
            "scientific_concept": "Lunar Cold Traps & ISRU: Deep crater floors at the lunar poles remain in permanent shadow at 40 Kelvin, trapping water ice deposits delivered by billions of years of cometary impacts.",
            "nasa_fact": "NASA's LCROSS mission confirmed significant water-ice concentrations in Cabeus crater, a cornerstone for future Artemis propellant manufacturing.",
            "coordinates": {"x": 12.0, "y": 0.0, "z": 28.0},
            "options": [
                {
                    "id": "cryo_drill",
                    "title": "Execute Deep Cryogenic Core Drilling",
                    "description": "Drill 2 meters below the regolith surface to access pure subsurface water-ice strata.",
                    "resource_impact_preview": "-7% Energy, +25L Water Buffer (+12%), +70 Score",
                    "tradeoff_summary": "High energy drill consumption delivers substantial fresh potable water to the outpost."
                },
                {
                    "id": "surface_scoop",
                    "title": "Collect Surface Regolith Geological Scoop",
                    "description": "Collect surface breccia and volatile-poor dust for mineralogical analysis.",
                    "resource_impact_preview": "-3% Energy, +5L Water Buffer, +35 Score",
                    "tradeoff_summary": "Quick, low-risk collection yielding modest water and basic geological insight."
                },
                {
                    "id": "thermal_sublimator",
                    "title": "Deploy Solar Thermal Concentrator Sublimator",
                    "description": "Focus sunlight via mirror onto heated regolith to bake out trapped moisture directly into collection bladder.",
                    "resource_impact_preview": "-4% Energy, +16L Water Buffer (+8%), +50 Score",
                    "tradeoff_summary": "Balanced solar extraction technique yielding good water recovery."
                }
            ]
        }
    ],

    "mars": [
        {
            "id": "mars_rover_inspection",
            "environment": "mars",
            "title": "Inspect Ares Exploration Rover",
            "target_name": "Ares Surface Rover",
            "category": "Surface Mobility & Robotics",
            "description": "The 6-wheel robotic chassis has completed a 12-kilometer geological traverse across Jezero Crater. Telemetry indicates dust intrusion in the right steering bogie.",
            "scientific_concept": "Martian Regolith Suspension & Rocker-Bogie Mechanics: Fine Martian atmospheric dust particles (~2-3 microns) penetrate unsealed bearings, accelerating mechanical wear in low gravity.",
            "nasa_fact": "NASA rovers Curiosity and Perseverance use specialized titanium rocker-bogie suspensions designed to climb over rocks larger than their wheel diameter.",
            "coordinates": {"x": -22.0, "y": 0.0, "z": 18.0},
            "options": [
                {
                    "id": "purge_bogie",
                    "title": "High-Pressure Gas Purge & Lubrication",
                    "description": "Purge sealed wheel hub with compressed nitrogen and re-grease actuator gears.",
                    "resource_impact_preview": "-6% Energy, Rover Restored, Systems +10%, +45 Score",
                    "tradeoff_summary": "Uses power to restore full mobility and sample delivery capacity."
                },
                {
                    "id": "replace_bogie_spare",
                    "title": "Install Factory Spare Actuator Assembly",
                    "description": "Swap out the degraded motor with a replacement actuator from outpost spares.",
                    "resource_impact_preview": "-1 Emergency Spare, Rover 100%, Systems +18%, +60 Score",
                    "tradeoff_summary": "Spends limited emergency spare parts for guaranteed rover perfection."
                },
                {
                    "id": "derate_rover",
                    "title": "Derate Speed & Software Motor Balancing",
                    "description": "Adjust motor drive firmware to reduce torque on the affected wheel.",
                    "resource_impact_preview": "No cost, Systems +4%, +20 Score",
                    "tradeoff_summary": "Zero resource expenditure, but limits maximum surface exploration radius."
                }
            ]
        },
        {
            "id": "mars_soil_sample",
            "environment": "mars",
            "title": "Collect Jezero Delta Sediment Core",
            "target_name": "Ancient River Delta Trench",
            "category": "Astrobiology & Geochemistry",
            "description": "Excavate sediment layers in the dried lakebed of Jezero Crater to analyze clay minerals and toxic perchlorates.",
            "scientific_concept": "Aqueous Sediments & Perchlorates: Mars regolith contains 0.5-1% toxic calcium and magnesium perchlorates (ClO4-), requiring chemical scrubbing before regolith can be used for food cultivation.",
            "nasa_fact": "NASA's Perseverance rover collects hermetically sealed rock cores in Jezero Crater for the international Mars Sample Return campaign.",
            "coordinates": {"x": 28.0, "y": 0.0, "z": -16.0},
            "options": [
                {
                    "id": "wet_chemical_assay",
                    "title": "Deploy Wet Chemical Perchlorate Leach Assay",
                    "description": "Dissolve soil sample in solvent solution to extract bio-toxic salts and isolate nutrients.",
                    "resource_impact_preview": "-6L Water, -5% Energy, Greenhouse Health +15%, +65 Score",
                    "tradeoff_summary": "Consumes water buffer but unlocks safe Martian soil for greenhouse crop cultivation."
                },
                {
                    "id": "raman_spectrometry",
                    "title": "Optical Raman & Luminescence Laser Scan",
                    "description": "Shoot pulsed ultraviolet laser at minerals to detect organic chemical bonds without physical processing.",
                    "resource_impact_preview": "-4% Energy, +45 Score",
                    "tradeoff_summary": "Clean, contactless scientific analysis that preserves water supplies."
                },
                {
                    "id": "magnetic_separation",
                    "title": "Magnetic Regolith Magnetite Sifting",
                    "description": "Use rare-earth magnets to pull ferromagnetic hematite minerals for habitat structural cement.",
                    "resource_impact_preview": "-2% Energy, Hull Integrity +8%, +35 Score",
                    "tradeoff_summary": "Extracts iron oxide building materials to reinforce habitat hull seals."
                }
            ]
        },
        {
            "id": "mars_dust_storm_warning",
            "environment": "mars",
            "title": "Respond to Approaching Dust Storm Warning",
            "target_name": "Meteorological Mast Tower",
            "category": "Atmospheric Dynamics & Hazard Triage",
            "description": "The automated anemometer detects wind gusts of 38 m/s carrying electrostatic dust clouds. Solar array irradiance will drop by 70% within hours.",
            "scientific_concept": "Martian Dust Storm Physics: Due to low atmospheric density (6 mbar), high wind speeds generate low dynamic pressure but lift microscopic dust that blocks sunlight for weeks.",
            "nasa_fact": "The 2018 global Martian dust storm ended NASA's Opportunity rover mission after 15 years by cutting solar power generation completely.",
            "coordinates": {"x": 6.0, "y": 0.0, "z": -34.0},
            "options": [
                {
                    "id": "stow_arrays",
                    "title": "Angle Solar Arrays & Overclock Fuel Cells",
                    "description": "Tilt panels vertically to prevent dust settling and fire auxiliary fuel cells.",
                    "resource_impact_preview": "-10% Energy Buffer, Power Grid Protected, +55 Score",
                    "tradeoff_summary": "Uses stored battery buffer to preserve solar panel optics from permanent coating."
                },
                {
                    "id": "electrostatic_shield",
                    "title": "Activate Electrodynamic Dust Shield (EDS)",
                    "description": "Energize high-voltage standing wave electrodes embedded in the array cover-glass.",
                    "resource_impact_preview": "-14% Energy, Array Cleared, +70 Score",
                    "tradeoff_summary": "Heavy electrical draw that completely repels airborne dust particles."
                },
                {
                    "id": "minimal_shelter",
                    "title": "Seal Habitats & Accept Passive Dust Settling",
                    "description": "Power down all science and non-critical systems; let dust settle naturally.",
                    "resource_impact_preview": "Power Grid -15%, Food Production paused, +25 Score",
                    "tradeoff_summary": "Conserves all energy, but accepts significant solar power degradation."
                }
            ]
        }
    ],

    "station": [
        {
            "id": "station_life_support",
            "environment": "station",
            "title": "Inspect ECLSS Carbon Dioxide Scrubbing Rack",
            "target_name": "CDRA & Sabatier Assembly",
            "category": "Atmospheric Regeneration",
            "description": "The Carbon Dioxide Removal Assembly (CDRA) desiccant bed pressure drop indicates zeolite pellet degradation.",
            "scientific_concept": "Zeolite Molecular Sieves & Sabatier Reaction: Thermal-swing adsorption uses synthetic porous zeolites to capture CO2, which is reacted with hydrogen to produce water (CO2 + 4H2 -> CH4 + 2H2O).",
            "nasa_fact": "On the International Space Station, the ECLSS system recycles over 98% of all water and regenerates breathable oxygen via electrolysis.",
            "coordinates": {"x": -12.0, "y": 0.0, "z": 8.0},
            "options": [
                {
                    "id": "thermal_bake",
                    "title": "Initiate High-Heat Desiccant Bake-Out",
                    "description": "Channel auxiliary power to 250°C thermal regeneration heaters to purge zeolite pores.",
                    "resource_impact_preview": "-8% Energy, Life Support +18%, Oxygen Buffer +10%, +50 Score",
                    "tradeoff_summary": "Consumes electrical power to regenerate scrubbing capacity and generate fresh O2."
                },
                {
                    "id": "swap_zeolite_spares",
                    "title": "Replace Desiccant Bed from Emergency Reserves",
                    "description": "Install sealed factory zeolite cartridge from emergency spares locker.",
                    "resource_impact_preview": "-1 Emergency Spare, Life Support +28%, +65 Score",
                    "tradeoff_summary": "Uses valuable emergency spare inventory to guarantee 100% ECLSS performance."
                },
                {
                    "id": "bleed_co2",
                    "title": "Vent Excess CO2 to Space & Run Backup Canisters",
                    "description": "Directly vent scrubber exhaust overboard and crack open lithium hydroxide canisters.",
                    "resource_impact_preview": "-5% Oxygen Buffer, Life Support +6%, +20 Score",
                    "tradeoff_summary": "Saves energy and spares, but consumes finite non-regenerable consumable oxygen."
                }
            ]
        },
        {
            "id": "station_equipment_maint",
            "environment": "station",
            "title": "Calibrate Nitrogen High-Pressure Regulator",
            "target_name": "High-Pressure Gas Manifold",
            "category": "Pneumatic Infrastructure",
            "description": "A minor pressure differential across the secondary nitrogen manifold requires transducer recalibration and valve seal inspection.",
            "scientific_concept": "Two-Gas Atmospheric Balance: Humans cannot breathe pure oxygen long-term without pulmonary toxicity and fire hazard; spacecraft atmospheres require 78% nitrogen buffer at 101.3 kPa.",
            "nasa_fact": "NASA spacesuits operate at 4.3 psi pure oxygen, but space station cabins operate at standard Earth sea-level pressure (14.7 psi / 101.3 kPa) using a nitrogen-oxygen mix.",
            "coordinates": {"x": 14.0, "y": 0.0, "z": -10.0},
            "options": [
                {
                    "id": "ultrasonic_leak_test",
                    "title": "Conduct Ultrasonic Acoustic Leak Diagnostic",
                    "description": "Use micro-frequency acoustic wand to locate micro-fissures in valve seating.",
                    "resource_impact_preview": "-5% Energy, Hull Integrity +14%, +45 Score",
                    "tradeoff_summary": "Identifies pressure anomalies early, protecting the orbital pressure vessel."
                },
                {
                    "id": "replace_elastomer_seal",
                    "title": "Install Factory Fluorocarbon O-Ring Seal",
                    "description": "Depressurize manifold line and replace the elastomer gasket with a flight spare.",
                    "resource_impact_preview": "-1 Emergency Spare, Hull Integrity +22%, +60 Score",
                    "tradeoff_summary": "Permanent factory repair that completely prevents nitrogen gas loss."
                },
                {
                    "id": "grease_actuator",
                    "title": "Apply Fluorosilicone Vacuum Grease & Torque",
                    "description": "Manually lubricate actuator stem and tighten locking collars.",
                    "resource_impact_preview": "-8% Crew Health (exhaustion), Hull Integrity +8%, +25 Score",
                    "tradeoff_summary": "Saves hardware but requires hours of fatiguing physical maintenance."
                }
            ]
        },
        {
            "id": "station_system_alert",
            "environment": "station",
            "title": "Respond to Simulated Micro-Meteoroid Impact Alert",
            "target_name": "Cupola Optical Sensor Array",
            "category": "Orbital Defense & Pressure Triage",
            "description": "Piezoelectric hull sensors register a high-velocity orbital debris impact on outer Whipple shield standoff bumper #4 near the Cupola window.",
            "scientific_concept": "Whipple Shield Hypervelocity Impact Physics: Space debris traveling at 7 to 10 km/s is vaporized upon striking thin outer aluminum bumpers, dispersing impact energy before reaching the inner pressure hull.",
            "nasa_fact": "The ISS Cupola has multi-pane fused silica and borosilicate glass windows protected by motorized external shutters when not in observation use.",
            "coordinates": {"x": 0.0, "y": 0.0, "z": 22.0},
            "options": [
                {
                    "id": "close_shutters_lockdown",
                    "title": "Close Motorized Cupola Shutters & Inspect Telemetry",
                    "description": "Engage heavy external micrometeoroid shutters and verify pressure decay rate.",
                    "resource_impact_preview": "-4% Energy, Hull Safe, Crew Morale Protected, +45 Score",
                    "tradeoff_summary": "Standard, safe aerospace procedure that contains pressure breach risks."
                },
                {
                    "id": "robotic_arm_scan",
                    "title": "Dispatch Canadarm Robotic Inspection Pass",
                    "description": "Maneuver external robotic arm with high-definition optical camera to inspect bumper cratering.",
                    "resource_impact_preview": "-8% Energy, Systems Condition +15%, +65 Score",
                    "tradeoff_summary": "Full visual verification confirms structural integrity and provides orbital debris science."
                },
                {
                    "id": "internal_bulkhead_seal",
                    "title": "Seal Hatch to Cupola Module & Restrict Access",
                    "description": "Close pressure hatch separating Cupola from node, isolating the observation deck.",
                    "resource_impact_preview": "No energy cost, Crew Morale -10%, +20 Score",
                    "tradeoff_summary": "Zero resource expenditure, but restricts station habitable volume and crew morale."
                }
            ]
        }
    ]
}

class ExplorationService:
    @staticmethod
    def get_objectives_for_environment(environment: str, completed_ids: Optional[List[str]] = None) -> List[ExplorationObjective]:
        env_key = environment.lower()
        if env_key not in OBJECTIVES_DATABASE:
            env_key = "moon"
        
        raw_list = OBJECTIVES_DATABASE[env_key]
        completed_set = set(completed_ids or [])

        objectives = []
        for item in raw_list:
            opts = [
                ObjectiveOption(
                    id=o["id"],
                    title=o["title"],
                    description=o["description"],
                    resource_impact_preview=o["resource_impact_preview"],
                    tradeoff_summary=o["tradeoff_summary"]
                )
                for o in item["options"]
            ]
            is_comp = item["id"] in completed_set
            objectives.append(ExplorationObjective(
                id=item["id"],
                environment=item["environment"],
                title=item["title"],
                target_name=item["target_name"],
                category=item["category"],
                description=item["description"],
                scientific_concept=item["scientific_concept"],
                nasa_fact=item["nasa_fact"],
                coordinates=item["coordinates"],
                options=opts,
                completed=is_comp
            ))
        return objectives

    @staticmethod
    def resolve_action(
        objective_id: str,
        option_id: str,
        state_dict: Dict[str, Any],
        duration_days: int,
        difficulty: str,
        current_day: int
    ) -> ExplorationActionResult:
        # Find objective in database
        target_obj = None
        target_opt = None
        for env_list in OBJECTIVES_DATABASE.values():
            for obj in env_list:
                if obj["id"] == objective_id:
                    target_obj = obj
                    for opt in obj["options"]:
                        if opt["id"] == option_id:
                            target_opt = opt
                            break
                    break
            if target_obj:
                break

        if not target_obj or not target_opt:
            raise ValueError(f"Objective '{objective_id}' or option '{option_id}' not found.")

        resources = ResourceState(**state_dict["resources"])
        systems = SystemState(**state_dict["systems"])
        crew = CrewState(**state_dict["crew"])
        emergency_spares = state_dict.get("emergency_spares", 2)
        score = state_dict.get("score", 100)

        # Baseline EVA oxygen & stamina cost
        resources.oxygen = max(0.0, resources.oxygen - 2.5)
        crew.morale = min(100.0, max(0.0, crew.morale + 1.0))

        score_boost = 35
        deltas = {"oxygen": -2.5}

        # Apply specific effects based on chosen option
        if option_id in ["piezo_pulse", "aux_bus_divert", "purge_bogie", "thermal_bake", "ultrasonic_leak_test", "close_shutters_lockdown"]:
            energy_cost = 6.0
            resources.energy = max(0.0, resources.energy - energy_cost)
            deltas["energy"] = -energy_cost
            if "piezo_pulse" in option_id:
                systems.power_grid = min(100.0, systems.power_grid + 18.0)
                deltas["power_grid"] = +18.0
                score_boost = 45
            elif "aux_bus_divert" in option_id:
                systems.life_support = min(100.0, systems.life_support + 14.0)
                deltas["life_support"] = +14.0
                score_boost = 40
            elif "purge_bogie" in option_id:
                systems.hull_integrity = min(100.0, systems.hull_integrity + 10.0)
                score_boost = 45
            elif "thermal_bake" in option_id:
                systems.life_support = min(100.0, systems.life_support + 18.0)
                resources.oxygen = min(100.0, resources.oxygen + 8.0)
                deltas["oxygen"] = +5.5
                score_boost = 50
            elif "ultrasonic_leak_test" in option_id:
                systems.hull_integrity = min(100.0, systems.hull_integrity + 14.0)
                deltas["hull_integrity"] = +14.0
                score_boost = 45

        elif option_id in ["spare_junction_swap", "replace_bogie_spare", "swap_zeolite_spares", "replace_elastomer_seal"]:
            if emergency_spares > 0:
                emergency_spares -= 1
                deltas["emergency_spares"] = -1
                systems.power_grid = min(100.0, systems.power_grid + 20.0)
                systems.life_support = min(100.0, systems.life_support + 20.0)
                systems.hull_integrity = min(100.0, systems.hull_integrity + 15.0)
                score_boost = 65
            else:
                resources.energy = max(0.0, resources.energy - 10.0)
                deltas["energy"] = -10.0
                score_boost = 20

        elif option_id in ["cryo_drill", "wet_chemical_assay", "electrostatic_shield", "robotic_arm_scan"]:
            resources.energy = max(0.0, resources.energy - 10.0)
            deltas["energy"] = -10.0
            if "cryo_drill" in option_id:
                resources.water = min(100.0, resources.water + 18.0)
                deltas["water"] = +18.0
                score_boost = 70
            elif "wet_chemical_assay" in option_id:
                resources.water = max(0.0, resources.water - 6.0)
                systems.greenhouse = min(100.0, systems.greenhouse + 15.0)
                deltas["greenhouse"] = +15.0
                score_boost = 65
            elif "electrostatic_shield" in option_id:
                systems.power_grid = min(100.0, systems.power_grid + 25.0)
                deltas["power_grid"] = +25.0
                score_boost = 70
            elif "robotic_arm_scan" in option_id:
                resources.system_condition = min(100.0, resources.system_condition + 15.0)
                score_boost = 65

        elif option_id in ["manual_brush", "grease_actuator"]:
            crew_cost = 8.0
            resources.crew_health = max(0.0, resources.crew_health - crew_cost)
            deltas["crew_health"] = -crew_cost
            systems.power_grid = min(100.0, systems.power_grid + 15.0)
            score_boost = 40

        else: # Passive or derating
            score_boost = 25

        # Re-average system condition
        resources.system_condition = round(
            (systems.power_grid + systems.life_support + systems.water_recovery +
             systems.greenhouse + systems.radiation_shield + systems.hull_integrity) / 6.0, 1
        )

        score += score_boost

        # Mark completed in state
        completed_objs = state_dict.get("completed_exploration_objectives", [])
        if objective_id not in completed_objs:
            completed_objs.append(objective_id)

        # Update objectives progress
        objectives = [ObjectiveSchema(**o) for o in state_dict.get("objectives", [])]
        for obj in objectives:
            if obj.id == "obj_eclss":
                obj.progress = round((systems.life_support + systems.water_recovery) / 2.0, 1)
                obj.completed = (obj.progress >= 65.0)
            elif obj.id == "obj_power":
                obj.progress = round(resources.energy, 1)
                obj.completed = (resources.energy >= 30.0)
            elif obj.id == "obj_hull":
                obj.progress = round(systems.hull_integrity, 1)
                obj.completed = (systems.hull_integrity >= 70.0)

        logs = state_dict.get("recent_logs", [])
        logs.append(f"EVA 3D ACTION: Completed '{target_obj['title']}' via '{target_opt['title']}'.")

        # Save back to state_dict
        state_dict["resources"] = resources.model_dump()
        state_dict["systems"] = systems.model_dump()
        state_dict["crew"] = crew.model_dump()
        state_dict["emergency_spares"] = emergency_spares
        state_dict["score"] = score
        state_dict["completed_exploration_objectives"] = completed_objs
        state_dict["objectives"] = [o.model_dump() for o in objectives]
        state_dict["recent_logs"] = logs[-6:]

        updated_resp = MissionStateResponse(
            mission_id=state_dict.get("mission_id", "sim-preview"),
            status=state_dict.get("status", "active"),
            current_day=current_day,
            total_days=duration_days,
            destination=target_obj["environment"],
            difficulty=difficulty,
            commander_name=state_dict.get("commander_name", "Cadet Explorer"),
            score=score,
            resources=resources,
            systems=systems,
            crew=crew,
            objectives=objectives,
            recent_logs=logs[-6:],
            completed_exploration_objectives=completed_objs,
            can_advance=True
        )

        return ExplorationActionResult(
            success=True,
            objective_id=objective_id,
            environment=target_obj["environment"],
            option_title=target_opt["title"],
            outcome_title=f"EVA Objective Completed: {target_obj['title']}",
            outcome_description=target_opt["description"],
            scientific_concept=target_obj["scientific_concept"],
            nasa_reference=target_obj["nasa_fact"],
            resource_deltas=deltas,
            score_delta=score_boost,
            updated_state=updated_resp
        )
