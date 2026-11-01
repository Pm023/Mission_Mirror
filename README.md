# MISSION MIRROR — Junior Astronaut Mission Trainer
> **Junior Astronaut Mission Trainer & 3D Interactive Exploration Platform**  
> An explainable space habitat simulator featuring deterministic life support physics, crisis triage, and counterfactual mission replay.

---

## 1. Product Vision & Educational Purpose

**Mission Mirror** is an interactive, explainable astronaut training simulator designed for middle-school and high-school students. Rather than relying on gamified guesswork, Mission Mirror teaches students how real space habitats work:

- **Resource Budgeting & Trade-offs:** Allocate a strict 100 simulation credit budget across life support, power generation, water loop recovery, food production, radiation shielding, and emergency reserves.
- **Interconnected Systems (ECLSS):** Experience real engineering cascades—e.g., how solar dust storms lower battery power, which throttles vacuum distillation water pumps, in turn reducing hydroponic greenhouse yield and depleting food reserves.
- **Dynamic Emergency Response:** Make critical triage decisions during 6 realistic anomalies (Solar Radiation Storms, Urine Processor Failures, Array Blackouts, Crop Blight, Decompression Trauma, and Airlock Seal Leaks).
- **Explainable Counterfactual Replay:** The core pedagogical breakthrough of Mission Mirror. Students can save their completed or failed missions, fork the exact same scenario from Day 1 with identical starting conditions, and make alternative choices. The simulator then compares both runs side-by-side using dual telemetry curves and causal attribution to explain *why* the outcome changed.
- **AI Mission Mentor:** Every decision is immediately explained across 5 structured dimensions: *What Changed*, *Why It Changed*, *Affected Systems*, *What to Monitor Next*, and the *Scientific Principle*. The simulation engine serves as the absolute ground truth, with a deterministic rule-based mentor that operates 100% offline without any paid API keys (with optional LLM enrichment).

---

## 2. Architecture & Data Flow

```
                      +---------------------------------------+
                      |       Cadet Web Interface (SPA)       |
                      |   HTML5 / CSS3 / Vanilla JS / Chart   |
                      +-------------------+-------------------+
                                          | REST API / JSON
                                          v
                      +---------------------------------------+
                      |         FastAPI REST Backend          |
                      |           (Python 3.11+)              |
                      +-------------------+-------------------+
                                          |
         +--------------------------------+--------------------------------+
         |                                |                                |
         v                                v                                v
+--------------------+          +--------------------+          +--------------------+
| Simulation Engine  |          |   Event Engine     |          |  AI Mission Mentor |
| - ECLSS Chemistry  |          | - 6 Space Events   |          | - Rule-Based Core  |
| - Power Cascades   |          | - 3 Choices Each   |          | - Optional LLM     |
| - Crew Vitals Math |          | - Trade-off Matrix |          | - NASA Citations   |
+---------+----------+          +---------+----------+          +---------+----------+
          |                               |                               |
          +-------------------------------+-------------------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |         SQLite / SQLAlchemy           |
                      |  - Missions & Day Telemetry Logs      |
                      |  - Decision Records & Replay Forks    |
                      +---------------------------------------+
```

### System Interdependency Topology
```
[Power Generation Grid]
     │
     ├───► [Life Support / O2 Scrubbers] ───► [Oxygen Buffer] ──┐
     │                                                          │
     ├───► [Water Recycling Bioreactor] ───► [Potable Water]  ──┼──► [Crew Physiological Health]
     │              │                                           │
     │              ▼                                           │
     ├───► [Hydroponic Greenhouse] ────────► [Food Rations]   ──┤
     │                                                          │
[Radiation Shielding] ──────────────────────────────────────────┘
```

---

## 3. Technology Stack

- **Backend:**
  - Python 3.11+
  - **FastAPI** for high-performance async REST APIs
  - **Pydantic v2** for robust state validation and data models
  - **SQLAlchemy 2.0** with **SQLite** for zero-configuration persistent storage
  - **Uvicorn** ASGI web server
  - **Pytest** and **HTTPX** for automated test coverage
- **Frontend:**
  - Modern HTML5 & CSS3 with custom Aerospace Mission Control dark theme
  - **Three.js (WebGL)** for interactive 3D Solar System & first/third-person astronaut exploration
  - **Bootstrap 5.3** & **Bootstrap Icons** for responsive, accessible UI
  - **Chart.js** for real-time telemetry curves and counterfactual comparative charts
  - Vanilla ES6 JavaScript (modular architecture: `api.js`, `planner.js`, `systems_graph.js`, `dashboard.js`, `replay.js`, `science.js`, `state.js`, `app.js`)
- **Verified Science & References:**
  - Open-access NASA Technical Reports Server (NTRS), NASA Marshall ECLSS fact sheets, and NASA Human Research Program literature.

---

---

## 3.5. 3D Virtual Space Exploration Platform

Mission Mirror includes a fully integrated, interactive 3D WebGL virtual space experience connected to the FastAPI simulation backend:

### A. The 3D Virtual Universe (Solar System)
- **Celestial Bodies:** Explore the Sun, Mercury, Venus, Earth with orbiting Moon and Space Station (ISS), Mars, Jupiter, and Saturn (with rings).
- **Interactive Navigation:** Smooth mouse drag orbit, wheel zoom, and click raycasting to inspect planetary telemetry, surface gravity, temperatures, and NASA exploration facts.
- **Visual Scale Disclaimer:** Planet radii and orbital distances are scaled for intuitive student interaction.
- **Flight Transitions:** One-click launch into 3D surface EVA exploration or mission flight briefings.

### B. Three Interactive 3D Explorable Environments
1. **The Moon (Shackleton Rim):**
   - Gray lunar regolith with craters and boulders.
   - High-contrast sunlight with crisp shadows and Earth suspended in the lunar sky.
   - Inflatable habitat dome, rover, dual solar arrays, power junction hub, and cold trap core drill.
   - **Low gravity:** $1/6g$ with soaring hops!
   - **3 Objectives:** Inspect Photovoltaic Solar Array, Diagnose Habitat Power Conduit Junction, Collect Regolith Ice-Core Sample.
2. **Mars (Jezero Crater):**
   - Oxidized red-ochre terrain, sand dunes, and basalt rocks.
   - Diffuse sunlight with pale salmon-pink atmospheric haze.
   - Ares Basecamp habitat, 6-wheel rover with rocker-bogie mechanics, sample cache drill, and dust storm weather mast.
   - **Mars gravity:** $3/8g$.
   - **3 Objectives:** Inspect Ares Rover Bogie, Drill Subsurface Perchlorate Core, Weather Station Dust Storm Alert.
3. **Space Station (ISS Low Earth Orbit):**
   - Pressurized orbital laboratory module with high-tech equipment racks and handrails.
   - **Panoramic Cupola Viewing Bay:** Look straight down through the observation port at a gigantic, rotating blue marble Earth!
   - ECLSS CO2 scrubber racks and high-pressure nitrogen gas regulator manifolds.
   - **Microgravity:** Zero-g floating movement.
   - **3 Objectives:** Inspect ECLSS CO2 Scrubbing Rack, Calibrate Nitrogen High-Pressure Regulator, Micrometeoroid Hull Impact Alert.

### C. Third-Person Astronaut Controller & Controls
- **Procedural 3D Suit:** Authentic Extravehicular Mobility Unit (EMU) with helmet, gold-coated visor, Display & Control Module (DCM), Life Support Backpack (PLSS), and articulated limb walking cycle.
- **Controls:**
  - `W`, `A`, `S`, `D` or Arrow Keys: Walk in direction of camera heading.
  - `Space`: Low-gravity jump or microgravity hop.
  - `Mouse Drag`: Smoothly orbit camera 360° around astronaut; `Mouse Wheel`: Zoom camera in/out.
  - `E`: Interact with objective when within proximity (< 3.5m).
  - `Esc` or `P`: Toggle Tactical Pause & Navigation Menu.
  - **Mobile Touch Overlay:** Virtual analog thumbstick D-pad + on-screen [HOP] and [INTERACT] buttons.

### D. FastAPI Integration
All 9 objectives are validated by the backend (`/api/exploration/missions/{id}/action` or `/api/exploration/sandbox/action`). Completed actions deduct EVA consumables, update system integrity, award mission points, generate an audit trail in the mission database, and reflect in real-time in the flight HUD.

## 4. Setup & Running Instructions

### Prerequisites
- Python 3.11, 3.12, or 3.13 installed
- Git (optional, for cloning)

### Quick Direct Run (Single Command)
You can launch the entire application with one simple command:

**Windows (Command Prompt or PowerShell):**
```cmd
.\runbackend.bat
```
*(or run `python run.py` / `.\runbackend.ps1`)*

**macOS / Linux:**
```bash
./runbackend.sh
```
*(or run `python3 run.py`)*

This script automatically sets up the environment, seeds the database if fresh, starts the Uvicorn server on port 8000, and mounts the cadet frontend!

---

### Step-by-Step Manual Setup

#### Windows (PowerShell)
```powershell
# 1. Navigate to the project directory
cd E:\NSAC_Project\mission-mirror

# 2. (Optional) Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r backend\requirements.txt

# 4. (Optional) Seed sample mission for instant demonstration
$env:PYTHONPATH = "backend"
python backend\seed_data.py

# 5. Start the FastAPI server
python run.py
```

### macOS / Linux (Bash)
```bash
# 1. Navigate to the project directory
cd mission-mirror

# 2. (Optional) Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. (Optional) Seed sample mission for instant demonstration
export PYTHONPATH=backend
python3 backend/seed_data.py

# 5. Start the FastAPI server
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

### Accessing the Web Application
- **Main Mission Control Dashboard:** Open your web browser to [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger REST API Documentation:** Open [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc API Documentation:** Open [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 5. Optional AI Mentor Configuration

Mission Mirror is designed to be **100% functional without any external AI API or paid subscription**. Its built-in deterministic rule-based mentor provides accurate, scientifically verified explanations based directly on backend simulation outputs.

If you wish to enable optional LLM enrichment, copy `.env.example` to `.env` and configure your API key:

```ini
# .env
DATABASE_URL=sqlite:///./mission_mirror.db

# Optional: Google Gemini
LLM_PROVIDER=gemini
LLM_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-1.5-flash

# OR Optional: OpenAI
# LLM_PROVIDER=openai
# LLM_API_KEY=your_openai_api_key_here
# LLM_MODEL=gpt-3.5-turbo
```

> **Security Note:** Secrets are never hardcoded or exposed to the client. If the AI API fails, times out, or has no quota, the simulator instantly falls back to the deterministic rule-based mentor with zero disruption.

---

## 6. The 6 Dynamic Mission Anomalies

Every dynamic event includes 3 distinct actionable choices with realistic engineering trade-offs:

| Anomaly | Description | Choice A (Resource Focus) | Choice B (Crew Triage) | Choice C (Sacrifice Buffer) |
|---|---|---|---|---|
| **1. Solar Radiation Storm** | High-energy proton flux from Coronal Mass Ejection | **Magnetic Deflector Boost:** -18% Energy, preserves crew | **Regolith Bunker:** Minor confinement stress (-5% health), saves power | **Passive Shielding:** Saves power, inflicts severe radiation (-22% health, +48 mSv) |
| **2. Water Recycling Malfunction** | Mineral scaling fouls vacuum distillation unit | **Replace Membrane:** Consumes 1 Emergency Spare; restores to 95% | **Chemical Backwash:** Spends 15L water and 10% energy; restores to 75% | **Ration & Bypass:** Loop stays at 40%; dehydration stress (-10% health) |
| **3. Power Grid Critical Anomaly** | Regolith dust blankets photovoltaic arrays | **Pulse Cleaning:** -12% Energy, -6% O2 (fuel cell burn); restores array | **Emergency Spacewalk:** 6h EVA sweeps panels; crew exhaustion (-14% health) | **Rolling Load Shedding:** Greenhouse lights cut; food growth halts |
| **4. Food Hydroponic Blight** | Airborne mold infects aeroponic lettuce trays | **UV-C Sterilization:** -14% Energy, -8L Water; cleans crops to 80% | **Caloric Rationing:** Crew on half-rations (-10% health); greenhouse wiped | **Deploy Seed Spares:** Consumes 1 Emergency Spare; fast-cycle harvest |
| **5. Crew Medical Emergency** | Acute decompression sickness / CO2 hypercapnia | **Hyperbaric O2 Therapy:** -15% O2, -8% Energy; full recovery | **Medical Spares Kit:** Consumes 1 Emergency Spare; stabilizes health | **Conservative Bedrest:** No resource cost; crew overworked (-16% health) |
| **6. Airlock Pressure Seal Leak** | Micrometeoroid pitting scores silicone gasket | **Spare Gasket Swap:** Consumes 1 Emergency Spare; hull sealed to 98% | **Epoxy Patch:** -8% Energy; seals hull to 88% with residual vulnerability | **Condemn Vestibule:** No resource cost; loses airlock volume (-10% morale) |

---

## 7. Running the Automated Test Suite

Mission Mirror includes a comprehensive automated test suite testing simulation equations, dynamic events, counterfactual replay determinism, and FastAPI REST endpoints.

Run tests using Pytest:
```powershell
# Windows
$env:PYTHONPATH = "backend"
pytest tests -v
```

```bash
# macOS / Linux
export PYTHONPATH=backend
pytest tests -v
```

### Verified Test Cases
1. `tests/test_simulation.py`:
   - `test_initial_outpost_calculation`: Credit allocation to resource conversions.
   - `test_budget_overspend_validation`: Strict validation rejecting allocations > 100 credits.
   - `test_daily_tick_nominal_consumption`: Daily 24h consumption, closed loop recycling, and wear.
   - `test_cascading_power_failure`: Verifies that low battery reserves throttle ECLSS scrubbers.
   - `test_fatal_oxygen_depletion`: Verifies catastrophic failure when oxygen depletes to 0%.
2. `tests/test_events.py`:
   - `test_all_six_events_exist`: Asserts presence and integrity of all 6 events with 3 choices each.
   - `test_event_selection`: Deterministic scenario selection.
   - `test_solar_radiation_storm_tradeoffs`: Validates contrasting energy vs health consequences.
   - `test_water_recycling_malfunction_spares_usage`: Verifies inventory tracking of spare parts.
3. `tests/test_replay.py`:
   - `test_counterfactual_replay_creation`: Ensures replay forks from identical seed and starting budget.
   - `test_counterfactual_comparison`: Validates delta calculation, divergence tracking, and causal attribution.
4. `tests/test_api.py`:
   - `test_health_check`: REST `/api/health` response.
   - `test_science_resources`: REST `/api/science/resources` verified citations.
   - `test_mission_lifecycle_api`: End-to-end API lifecycle: create, deploy, advance, report, replay.
   - `test_mentor_explain_api`: Pedagogical mentor advice endpoint.
5. `tests/test_e2e_full_flow.py`:
   - `test_static_files_served`: Verifies FastAPI serves frontend HTML, CSS, and JS.
   - `test_full_mission_counterfactual_lifecycle`: Multi-day simulation with event choices and replay comparison.

---

## 8. 3–5 Minute Hackathon Presentation Script

Use this structured script when presenting Mission Mirror to judges or teachers:

- **0:00 - 0:45 | The Hook & Challenge:**  
  *"Judges, preparing the next generation of space explorers requires more than textbooks—it requires understanding that in space, every system is connected to your life. Welcome to Mission Mirror, an explainable space habitat trainer for junior astronauts that demonstrates the power of counterfactual learning."*
- **0:45 - 1:30 | Planning & Interconnected Systems (Live Demo):**  
  *(Show Outpost Planner)* *"We start with 100 simulation credits. Every credit allocated involves real aerospace trade-offs. Notice our Engineering Consequence Explorer: our power grid drives our water recovery pumps, which in turn feed our hydroponic greenhouse. If power dips below 25%, life support is automatically throttled."*
- **1:30 - 2:45 | Crisis Triage & Explainable AI Mentor (Live Demo):**  
  *(Advance Day -> Trigger Solar Radiation Storm)* *"On Day 4, deep space sensors detect a massive solar radiation storm. We have three actionable protocols. Let's shelter in the regolith bunker. Notice our AI Mission Mentor: it doesn't give generic text—it breaks down what changed, why it changed, what to monitor next, and explains the physics of In-Situ Radiation Shielding."*
- **2:45 - 3:45 | The Core Innovation: Counterfactual Replay:**  
  *(Show Mission Debrief -> Click Launch Counterfactual Replay)* *"Here is the breakthrough: in traditional games, when you fail, you just start over blindly. In Mission Mirror, cadets launch a Counterfactual Replay. The simulator forks the exact same scenario. This time, we spend power on the Active Magnetic Deflector. Our comparative debrief places both runs side-by-side: our score increased by +140 points, our crew health stayed at 95%, and the causal attribution explains exactly how our alternative choice prevented the cascade."*
- **3:45 - 4:15 | Authentic Space Science & Wrap-Up:**  
  *(Show Science Explorer)* *"Every fact in our Science Explorer is cited from verified open-access NASA technical reports. Mission Mirror works 100% offline without any paid API keys, is fully covered by automated tests, and gives junior astronauts the confidence to solve real space problems."*

---

## 9. Feature Checklist, Honest Limitations & Future Roadmap

### Fully Implemented & Verified
- [x] Responsive Aerospace Mission Control UI (HTML5, Bootstrap 5, Chart.js, Vanilla JS).
- [x] FastAPI REST API with Pydantic v2 schemas and SQLite persistent storage.
- [x] 100-credit Outpost Budget Planner with interactive trade-offs and overspend enforcement.
- [x] Deterministic ECLSS simulation engine with documented units (O2, Water, Food, Energy, Health).
- [x] Cascading failure modeling (e.g., power grid brownout throttles water & oxygen regeneration).
- [x] 6 distinct dynamic space anomalies with 3 actionable choices each.
- [x] Interactive Engineering Consequence Explorer (SVG dependency graph with node inspector).
- [x] Explainable AI Mission Mentor with 5-part pedagogical breakdown.
- [x] Deterministic rule-based mentor fallback (operates without any API key or paid service).
- [x] Optional LLM integration (Gemini / OpenAI) via environment variables.
- [x] Counterfactual Replay engine that clones initial seed and starting conditions.
- [x] Side-by-side Replay Comparison with dual telemetry curves and causal attribution.
- [x] Science Explorer with verified open-access NASA citations.
- [x] 3D Virtual Universe ("Explore Universe") with Sun, Earth, Moon, ISS, Mars, Jupiter, Saturn, and orbital paths.
- [x] 3 explorable 3D environments: Moon (Shackleton Rim), Mars (Jezero Crater), and Space Station (LEO Cupola with rotating Earth below).
- [x] 3rd-person procedural EMU Astronaut controller with walking animations, environment-specific gravity, and collision handling.
- [x] 9 interactive field objectives (3 per environment) integrated into FastAPI simulation state and score calculations.
- [x] Desktop (WASD/Mouse/Space/E) & Mobile Touch (Virtual Joystick, Hop, Interact) controls.
- [x] 21 automated tests passing with zero failures.

### Limitations & Honest Disclaimers
- **Educational Approximation:** The ECLSS calculations and physiological models are educational simplifications designed for students, not flight-certified engineering simulations.
- **Diurnal Cycles:** The Moon's 14-day night cycle is represented as daily wear and power drain rather than an hour-by-hour thermal radiation model.
- **Crew Uniformity:** The 4-person crew is treated as an aggregated physiological unit rather than individual avatar health sheets.

### Future Roadmap
- **Multiplayer Crew Stations:** Allow a team of 4 students to operate as Flight Commander, ECLSS Officer, Power Systems Officer, and Medical Officer across separate network terminals.
- **Custom Scenario Builder:** Allow science educators to design custom planetary anomalies and budget challenges for curriculum-aligned classroom modules.
- **Real-Time NASA Telemetry Feed:** Integrate live ISS ECLSS telemetry data via NASA Open APIs to let students compare simulated habitat rates against the actual space station.

---

## 10. License & Acknowledgements
- Designed as an interactive, explainable astronaut mission simulator.
- Educational spaceflight concepts and citations courtesy of the **National Aeronautics and Space Administration (NASA)** and the **NASA Technical Reports Server (NTRS)**.
- Released under the open-source **MIT License**.
