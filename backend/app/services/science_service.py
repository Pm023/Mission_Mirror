from typing import List, Dict, Any

SCIENCE_MODULES: List[Dict[str, Any]] = [
    {
        "id": "eclss_systems",
        "title": "Environmental Control & Life Support Systems (ECLSS)",
        "category": "Life Support",
        "summary": "How spacecraft recycle air and water to create a habitable Earth-like bubble in the vacuum of space.",
        "real_science_facts": [
            "On the International Space Station (ISS), the ECLSS water recovery system achieves up to 98% water recovery from astronaut sweat, urine, and atmospheric moisture condensate.",
            "Oxygen generation primarily occurs via water electrolysis (2H2O -> 2H2 + O2). The byproduct hydrogen is reacted with carbon dioxide in a Sabatier reactor to produce water and methane (CO2 + 4H2 -> CH4 + 2H2O).",
            "Nominal human oxygen consumption in space is approximately 0.84 kg of O2 per astronaut per day, while daily potable water consumption is roughly 2.5 to 3.5 liters for drinking and rehydrating food."
        ],
        "game_model_simplification": "In Mission Mirror, oxygen, water, and food are tracked as unified capacity buffers and percentage levels (0-100%). Subsystem degradation lowers the recycling efficiency coefficient below the nominal 95% baseline.",
        "citations": [
            {
                "title": "NASA ECLSS: Environmental Control and Life Support System",
                "source": "NASA Marshall Space Flight Center Fact Sheet",
                "url": "https://www.nasa.gov/international-space-station/space-station-environmental-control-and-life-support-system/",
                "retrieved_date": "2024-10-15"
            },
            {
                "title": "Closing the Loop: ISS ECLSS Water and Air Technology Demonstration",
                "source": "NASA Technical Reports Server (NTRS)",
                "url": "https://ntrs.nasa.gov/",
                "retrieved_date": "2024-10-15"
            }
        ]
    },
    {
        "id": "space_radiation",
        "title": "Space Radiation Hazards & Planetary Shielding",
        "category": "Crew Protection",
        "summary": "Ionizing galactic cosmic rays and solar particle events, and how regolith and magnetic fields mitigate them.",
        "real_science_facts": [
            "Space radiation consists of Galactic Cosmic Rays (GCRs) from outside the solar system and Solar Particle Events (SPEs) during Coronal Mass Ejections.",
            "Without Earth's protective magnetosphere and thick atmosphere, astronauts on the Moon or Mars receive 200 to 500 times the radiation dose of a person on Earth (typically 0.3 to 1.8 mSv per day vs ~2-3 mSv per year on Earth).",
            "Lunar and Martian regolith (soil) is rich in silicates, basalt, and iron oxides. Piling 2 to 3 meters of compacted regolith over an inflatable habitat provides effective passive mass attenuation against both ionizing particles and micrometeorites."
        ],
        "game_model_simplification": "Mission Mirror tracks cumulative radiation dose in millisieverts (mSv). The Radiation Protection allocation and emergency bunker decisions simulate in-situ regolith mass and active magnetic deflection.",
        "citations": [
            {
                "title": "NASA Space Radiation Analysis Group: Human Spaceflight Radiation Hazards",
                "source": "NASA Johnson Space Center Space Radiation Program",
                "url": "https://www.nasa.gov/space-radiation-analysis-group/",
                "retrieved_date": "2024-10-15"
            },
            {
                "title": "In Situ Resource Utilization (ISRU) for Lunar Radiation Protection",
                "source": "NASA Technical Publication 20210018593",
                "url": "https://ntrs.nasa.gov/",
                "retrieved_date": "2024-10-15"
            }
        ]
    },
    {
        "id": "space_power",
        "title": "Extraterrestrial Power Architectures: Solar vs Nuclear",
        "category": "Power Systems",
        "summary": "Surviving the 14-day lunar night and Martian dust storms using fission surface power and advanced photovoltaics.",
        "real_science_facts": [
            "The Moon experiences a 28-day diurnal cycle: roughly 14 Earth days of continuous sunlight followed by 14 Earth days of freezing darkness (-130°C to -170°C). Solar-only outposts require massive regenerative fuel cell or battery mass.",
            "Mars receives only about 43% of the solar irradiance of Earth, and planetary-scale dust storms can obscure sunlight for weeks, severely reducing photovoltaic generation (as experienced by NASA rovers Opportunity and InSight).",
            "NASA and the Department of Energy have tested the Kilopower reactor concept (10-40 kWe Stirling fission reactor) to supply continuous, weather-independent surface electricity."
        ],
        "game_model_simplification": "Power Grid health and Energy reserves represent generation and battery buffers. Low power triggers cascading throttling to life support scrubbers and hydroponic grow lamps.",
        "citations": [
            {
                "title": "NASA Fission Surface Power Project Overview",
                "source": "NASA Glenn Research Center",
                "url": "https://www.nasa.gov/directorates/stmd/technology-demonstration-missions-program/fission-surface-power-project/",
                "retrieved_date": "2024-10-15"
            },
            {
                "title": "Mars Dust Storms and Solar Power Limitations",
                "source": "NASA Jet Propulsion Laboratory (JPL)",
                "url": "https://mars.nasa.gov/",
                "retrieved_date": "2024-10-15"
            }
        ]
    },
    {
        "id": "bioregenerative_food",
        "title": "Hydroponic & Aeroponic Food Systems in Space",
        "category": "Nutrition & Botany",
        "summary": "Growing fresh crops in microgravity and partial gravity to supplement packaged astronaut rations.",
        "real_science_facts": [
            "NASA's Veggie and Advanced Plant Habitat (APH) experiments on the ISS have successfully cultivated red romaine lettuce, dwarf tomatoes, and chili peppers using LED spectrum lighting and porous rooting pillows.",
            "Packaged freeze-dried rations slowly lose critical micronutrients (specifically Vitamins C, B1, and B12) over multi-year deep space missions due to radiation and ambient temperature decay.",
            "Hydroponic plants transpire clean water vapor into the air, acting as living biological filters that assist mechanical humidity recovery systems."
        ],
        "game_model_simplification": "Food is modeled as combined packaged rations and fresh harvest yield. Maintaining power and water enables the greenhouse to replenish daily caloric draw.",
        "citations": [
            {
                "title": "Growing Plants in Space: NASA Veggie and Advanced Plant Habitat",
                "source": "NASA Kennedy Space Center",
                "url": "https://www.nasa.gov/missions/station/iss-research/growing-plants-in-space/",
                "retrieved_date": "2024-10-15"
            }
        ]
    },
    {
        "id": "human_adaptation",
        "title": "Human Physiological Adaptation & Decompression Triage",
        "category": "Human Biology",
        "summary": "Cardiovascular deconditioning, muscle atrophy, hypercapnia, and barotrauma during EVA operations.",
        "real_science_facts": [
            "In reduced gravity (1/6th g on Moon, 3/8th g on Mars), the human body undergoes fluid shifts toward the head, vestibular disorientation, and bone mineral loss of up to 1-1.5% per month in weight-bearing bones.",
            "Extravehicular suits operate at lower internal pressures (e.g. 4.3 psi / 29.6 kPa) to allow glove and joint flexibility. Astronauts must 'pre-breathe' 100% oxygen before spacewalks to wash out nitrogen and prevent decompression sickness.",
            "Elevated carbon dioxide levels (hypercapnia) above 0.5% (5 mm Hg) cause astronaut headaches, cognitive impairment, and irritability, making reliable CO2 scrubbers mission-critical."
        ],
        "game_model_simplification": "Crew Health reflects overall physiological integrity. Oxygen depletion or high radiation degrades health; rested conditions and balanced life support allow steady recovery.",
        "citations": [
            {
                "title": "NASA Human Research Program: The Five Hazards of Human Spaceflight",
                "source": "NASA Human Research Program",
                "url": "https://www.nasa.gov/hrp/hazards/",
                "retrieved_date": "2024-10-15"
            }
        ]
    }
]

class ScienceService:
    @staticmethod
    def get_all_science_topics() -> List[Dict[str, Any]]:
        return SCIENCE_MODULES

    @staticmethod
    def get_topic_by_id(topic_id: str) -> Dict[str, Any]:
        for topic in SCIENCE_MODULES:
            if topic["id"] == topic_id:
                return topic
        return SCIENCE_MODULES[0]
