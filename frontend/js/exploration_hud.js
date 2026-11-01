/**
 * MISSION MIRROR — 3D Exploration HUD & Mission Coordinator
 * Full-screen aerospace flight overlay, dynamic waypoint tracker, radar compass,
 * interactive objective decision modal, and mobile touch controls.
 */
const ExplorationHUD = {
  container: null,
  canvas: null,
  scene: null,
  camera: null,
  renderer: null,
  clock: null,
  animationId: null,
  isRunning: false,

  currentEnvironment: 'moon',
  astronaut: null,
  objectives: [],
  activeObjective: null,
  terrainHeightFn: (x, z) => 0,

  init() {
    this.container = document.getElementById('exploration-canvas-container');
    if (!this.container) return;

    this.setupUI();
    this.setupMobileControls();
  },

  setupUI() {
    // Proximity banner interact button
    const banner = document.getElementById('exploration-proximity-prompt');
    if (banner) {
      banner.addEventListener('click', () => {
        if (this.astronaut) this.astronaut.triggerInteract();
      });
    }

    // Pause menu buttons
    const btnResume = document.getElementById('btn-pause-resume');
    if (btnResume) {
      btnResume.addEventListener('click', () => this.togglePauseMenu(false));
    }

    const btnUniverse = document.getElementById('btn-pause-universe');
    if (btnUniverse) {
      btnUniverse.addEventListener('click', () => {
        this.togglePauseMenu(false);
        AppState.setView('universe');
      });
    }

    const btnDashboard = document.getElementById('btn-pause-dashboard');
    if (btnDashboard) {
      btnDashboard.addEventListener('click', () => {
        this.togglePauseMenu(false);
        AppState.setView('dashboard');
      });
    }

    const btnPauseToggle = document.getElementById('btn-hud-pause');
    if (btnPauseToggle) {
      btnPauseToggle.addEventListener('click', () => this.togglePauseMenu());
    }

    // Objective modal close
    const btnCloseModal = document.getElementById('btn-close-objective-modal');
    if (btnCloseModal) {
      btnCloseModal.addEventListener('click', () => {
        const modal = document.getElementById('exploration-objective-modal');
        if (modal) modal.classList.add('d-none');
      });
    }

    // Window resize
    window.addEventListener('resize', () => this.onResize());
  },

  setupMobileControls() {
    // Touch D-Pad
    const touchStick = document.getElementById('touch-joystick-knob');
    const touchBase = document.getElementById('touch-joystick-base');
    if (touchStick && touchBase) {
      let isTouching = false;
      let startX = 0, startY = 0;
      const maxRadius = 40;

      const handleTouchStart = (e) => {
        isTouching = true;
        const touch = e.targetTouches ? e.targetTouches[0] : e;
        const rect = touchBase.getBoundingClientRect();
        startX = rect.left + rect.width / 2;
        startY = rect.top + rect.height / 2;
      };

      const handleTouchMove = (e) => {
        if (!isTouching || !this.astronaut) return;
        const touch = e.targetTouches ? e.targetTouches[0] : e;
        const dx = touch.clientX - startX;
        const dy = touch.clientY - startY;
        const dist = Math.hypot(dx, dy);
        const angle = Math.atan2(dy, dx);

        const clampedDist = Math.min(dist, maxRadius);
        const knobX = Math.cos(angle) * clampedDist;
        const knobY = Math.sin(angle) * clampedDist;

        touchStick.style.transform = `translate(${knobX}px, ${knobY}px)`;

        // Update astronaut keys
        const threshold = 12;
        this.astronaut.keys.forward = dy < -threshold;
        this.astronaut.keys.backward = dy > threshold;
        this.astronaut.keys.left = dx < -threshold;
        this.astronaut.keys.right = dx > threshold;
      };

      const handleTouchEnd = () => {
        isTouching = false;
        touchStick.style.transform = 'translate(0px, 0px)';
        if (this.astronaut) {
          this.astronaut.keys.forward = false;
          this.astronaut.keys.backward = false;
          this.astronaut.keys.left = false;
          this.astronaut.keys.right = false;
        }
      };

      touchBase.addEventListener('touchstart', handleTouchStart, { passive: true });
      window.addEventListener('touchmove', handleTouchMove, { passive: true });
      window.addEventListener('touchend', handleTouchEnd, { passive: true });
    }

    // Touch Jump
    const touchJump = document.getElementById('touch-btn-jump');
    if (touchJump) {
      touchJump.addEventListener('touchstart', (e) => {
        e.preventDefault();
        if (this.astronaut) this.astronaut.keys.jump = true;
      });
      touchJump.addEventListener('touchend', (e) => {
        e.preventDefault();
        if (this.astronaut) this.astronaut.keys.jump = false;
      });
    }

    // Touch Interact
    const touchInteract = document.getElementById('touch-btn-interact');
    if (touchInteract) {
      touchInteract.addEventListener('click', (e) => {
        e.preventDefault();
        if (this.astronaut) this.astronaut.triggerInteract();
      });
    }
  },

  async startExploration(environment = 'moon') {
    this.currentEnvironment = environment.toLowerCase();
    AppState.setView('exploration');

    if (!this.container) {
      this.init();
    }

    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || (window.innerHeight - 80);

    // 1. Scene & Renderer setup
    if (!this.scene) {
      this.scene = new THREE.Scene();
      this.clock = new THREE.Clock();
      this.camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);

      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      this.container.innerHTML = '';
      this.container.appendChild(this.renderer.domElement);
    }

    // 2. Build 3D Environment (Moon, Mars, or Station)
    const envData = ExplorationEnvironments.build(this.currentEnvironment, this.scene);
    this.terrainHeightFn = envData.getTerrainHeight;

    // 3. Create or Reset Astronaut Controller
    if (this.astronaut) {
      this.astronaut.dispose();
    }
    this.astronaut = new AstronautController(this.scene, this.camera, this.renderer.domElement);
    this.astronaut.setEnvironment(this.currentEnvironment);
    this.astronaut.getTerrainHeight = this.terrainHeightFn;
    this.astronaut.resetPosition(0, 4);

    // Callbacks
    this.astronaut.onProximity = (obj, dist) => this.showProximityPrompt(obj, dist);
    this.astronaut.onProximityExit = () => this.hideProximityPrompt();
    this.astronaut.onInteract = (obj) => this.openObjectiveDialog(obj);

    // 4. Fetch Objectives from Backend
    await this.loadObjectives();

    // 5. Update HUD state
    this.updateHUDHeader();

    // 6. Start Render Loop
    if (!this.isRunning) {
      this.isRunning = true;
      this.clock.start();
      this.animate();
    }

    this.onResize();
  },

  async loadObjectives() {
    try {
      const missionId = AppState.currentMissionId;
      const objs = await API.getExplorationObjectives(this.currentEnvironment, missionId);
      this.objectives = objs;
      this.astronaut.objectives = objs;

      // Spawn glowing 3D beacon waypoints in the scene
      objs.forEach(obj => {
        ExplorationEnvironments.createWaypointMarker(this.scene, obj, this.terrainHeightFn);
      });

      this.updateWaypointPanel();
    } catch (err) {
      console.error('Failed to load exploration objectives:', err);
    }
  },

  updateHUDHeader() {
    const envBadge = document.getElementById('hud-environment-title');
    const envSub = document.getElementById('hud-environment-sub');
    const missionTag = document.getElementById('hud-mission-link-tag');

    const envNames = {
      moon: { title: 'LUNAR SURFACE — SHACKLETON RIM', sub: '1/6g Gravity • Hard Vacuum • ISRU Cold Traps' },
      mars: { title: 'MARTIAN SURFACE — JEZERO CRATER', sub: '3/8g Gravity • Thin CO2 Atmosphere • Ares Outpost' },
      station: { title: 'ORBITAL SPACE STATION — CUPOLA & ECLSS', sub: 'Microgravity • Low Earth Orbit (420 km) • Life Support' }
    };

    const info = envNames[this.currentEnvironment] || envNames.moon;
    if (envBadge) envBadge.textContent = info.title;
    if (envSub) envSub.textContent = info.sub;

    if (missionTag) {
      if (AppState.currentMission && AppState.currentMission.mission_id) {
        missionTag.innerHTML = `
          <span class="badge bg-primary-subtle text-cyan border border-cyan">
            <i class="bi bi-link-45deg me-1"></i>MISSION: ${AppState.currentMission.mission_id.substring(0, 8)}... (Day ${AppState.currentMission.current_day})
          </span>
        `;
      } else {
        missionTag.innerHTML = `
          <span class="badge bg-dark border border-secondary text-dim">
            <i class="bi bi-mortarboard me-1"></i>CADET FREE-ROAM SANDBOX
          </span>
        `;
      }
    }

    this.updateTelemetryBars();
  },

  updateTelemetryBars() {
    // If mission active, pull from AppState.currentMission.resources, else mock nominal
    const res = AppState.currentMission ? AppState.currentMission.resources : {
      oxygen: 92, energy: 88, crew_health: 95, system_condition: 90
    };
    const score = AppState.currentMission ? AppState.currentMission.score : 100;

    const elO2 = document.getElementById('hud-bar-o2');
    const elEnergy = document.getElementById('hud-bar-energy');
    const elHealth = document.getElementById('hud-bar-health');
    const elScore = document.getElementById('hud-val-score');

    if (elO2) {
      elO2.style.width = `${res.oxygen}%`;
      elO2.className = `progress-bar ${res.oxygen < 35 ? 'bg-danger' : (res.oxygen < 65 ? 'bg-warning' : 'bg-info')}`;
    }
    if (elEnergy) {
      elEnergy.style.width = `${res.energy}%`;
      elEnergy.className = `progress-bar ${res.energy < 35 ? 'bg-danger' : (res.energy < 60 ? 'bg-warning' : 'bg-primary')}`;
    }
    if (elHealth) {
      elHealth.style.width = `${res.crew_health}%`;
      elHealth.className = `progress-bar ${res.crew_health < 40 ? 'bg-danger' : 'bg-success')}`;
    }
    if (elScore) {
      elScore.textContent = score;
    }
  },

  updateWaypointPanel() {
    const listEl = document.getElementById('hud-waypoint-list');
    if (!listEl) return;

    listEl.innerHTML = this.objectives.map(obj => {
      const dist = obj.currentDistance ? `${obj.currentDistance.toFixed(1)}m` : '--';
      const statusIcon = obj.completed
        ? '<i class="bi bi-check-circle-fill text-success"></i>'
        : '<i class="bi bi-geo-alt-fill text-cyan"></i>';
      const statusBadge = obj.completed
        ? '<span class="badge bg-success-subtle text-success border border-success" style="font-size:0.65rem;">COMPLETED</span>'
        : `<span class="badge bg-dark border border-cyan text-cyan font-monospace" style="font-size:0.65rem;">${dist}</span>`;

      return `
        <div class="p-2 mb-1 rounded bg-dark border ${obj.completed ? 'border-success' : 'border-secondary'} d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center gap-2">
            ${statusIcon}
            <div>
              <div class="text-white small fw-bold lh-1">${obj.title}</div>
              <div class="text-dim font-monospace" style="font-size:0.68rem;">${obj.target_name}</div>
            </div>
          </div>
          <div>${statusBadge}</div>
        </div>
      `;
    }).join('');
  },

  showProximityPrompt(obj, dist) {
    const prompt = document.getElementById('exploration-proximity-prompt');
    const textEl = document.getElementById('proximity-prompt-text');
    const touchBtn = document.getElementById('touch-btn-interact');

    if (prompt && textEl) {
      textEl.innerHTML = `<strong>${obj.target_name}</strong> IN RANGE (${dist.toFixed(1)}m) — PRESS <kbd class="bg-cyan text-dark px-1">E</kbd> TO INTERACT`;
      prompt.classList.remove('d-none');
    }

    if (touchBtn) {
      touchBtn.classList.add('pulse-active');
    }
  },

  hideProximityPrompt() {
    const prompt = document.getElementById('exploration-proximity-prompt');
    const touchBtn = document.getElementById('touch-btn-interact');
    if (prompt) prompt.classList.add('d-none');
    if (touchBtn) touchBtn.classList.remove('pulse-active');
  },

  openObjectiveDialog(obj) {
    this.activeObjective = obj;
    const modal = document.getElementById('exploration-objective-modal');
    if (!modal) return;

    document.getElementById('modal-obj-title').textContent = obj.title;
    document.getElementById('modal-obj-target').textContent = `${obj.target_name} • ${obj.category}`;
    document.getElementById('modal-obj-desc').textContent = obj.description;
    document.getElementById('modal-obj-concept').textContent = obj.scientific_concept;
    document.getElementById('modal-obj-fact').textContent = obj.nasa_fact;

    const optList = document.getElementById('modal-obj-options');
    optList.innerHTML = '';

    if (obj.completed) {
      optList.innerHTML = `
        <div class="alert alert-success border border-success p-3 text-center">
          <i class="bi bi-check-circle-fill fs-4 me-2"></i>
          <strong>Objective Already Completed!</strong>
          <p class="small mb-0 mt-1">This telemetry task has already been resolved and recorded into the mission audit log.</p>
        </div>
      `;
    } else {
      obj.options.forEach((opt, idx) => {
        const optCard = document.createElement('div');
        optCard.className = 'card bg-dark border border-secondary p-3 mb-2 option-card';
        optCard.style.cursor = 'pointer';
        optCard.innerHTML = `
          <div class="d-flex justify-content-between align-items-start mb-1">
            <h6 class="text-white fw-bold mb-0">${idx + 1}. ${opt.title}</h6>
            <span class="badge bg-primary-subtle text-cyan border border-cyan font-monospace">${opt.resource_impact_preview}</span>
          </div>
          <p class="text-secondary small mb-2">${opt.description}</p>
          <div class="text-dim small fst-italic">
            <i class="bi bi-arrow-left-right text-cyan me-1"></i>Trade-off: ${opt.tradeoff_summary}
          </div>
          <button class="btn btn-astro-primary btn-sm mt-2 w-100 btn-select-opt" data-opt-id="${opt.id}">
            Execute Protocol (${opt.title})
          </button>
        `;

        optCard.querySelector('.btn-select-opt').addEventListener('click', () => {
          this.executeObjectiveChoice(obj.id, opt.id);
        });

        optList.appendChild(optCard);
      });
    }

    modal.classList.remove('d-none');
  },

  async executeObjectiveChoice(objectiveId, optionId) {
    const modal = document.getElementById('exploration-objective-modal');
    const optList = document.getElementById('modal-obj-options');
    optList.innerHTML = `
      <div class="text-center py-4">
        <div class="spinner-border text-cyan mb-2" role="status"></div>
        <div class="text-white font-monospace">TRANSMITTING EVA TELEMETRY TO FLIGHT COMPUTER...</div>
      </div>
    `;

    try {
      let result;
      if (AppState.currentMission && AppState.currentMission.mission_id) {
        result = await API.submitMissionExplorationAction(AppState.currentMission.mission_id, objectiveId, optionId);
        AppState.setCurrentMission(result.updated_state);
      } else {
        result = await API.submitSandboxExplorationAction(objectiveId, optionId);
      }

      if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();

      // Mark local objective as completed
      const localObj = this.objectives.find(o => o.id === objectiveId);
      if (localObj) {
        localObj.completed = true;
      }

      // Update 3D waypoint beacon to green
      const wp = ExplorationEnvironments.waypoints.find(w => w.userData.objective.id === objectiveId);
      if (wp) {
        const successColor = 0x00e676;
        wp.userData.diamond.material.color.setHex(successColor);
        wp.userData.core.material.color.setHex(successColor);
        wp.userData.beam.material.color.setHex(successColor);
        wp.userData.groundRing.material.color.setHex(successColor);
      }

      // Display Victory / Resolution Toast inside Modal
      optList.innerHTML = `
        <div class="alert alert-success border border-success p-3">
          <div class="d-flex align-items-center gap-2 mb-2">
            <i class="bi bi-patch-check-fill fs-3 text-success"></i>
            <div>
              <h5 class="text-white fw-bold mb-0">${result.outcome_title}</h5>
              <div class="text-success small font-monospace">+${result.score_delta} MISSION POINTS AWARDED</div>
            </div>
          </div>
          <p class="text-white small mb-2">${result.outcome_description}</p>
          <div class="p-2 rounded bg-dark border border-secondary mb-2 small text-secondary">
            <strong>Scientific Concept:</strong> ${result.scientific_concept}
          </div>
          <div class="p-2 rounded bg-dark border border-secondary small text-dim font-monospace">
            <strong>NASA Reference:</strong> ${result.nasa_reference}
          </div>
          <button class="btn btn-astro-primary btn-sm mt-3 w-100" id="btn-modal-dismiss-success">
            <i class="bi bi-check-lg me-1"></i>Return to Astronaut EVA Field
          </button>
        </div>
      `;

      document.getElementById('btn-modal-dismiss-success').addEventListener('click', () => {
        if (modal) modal.classList.add('d-none');
      });

      this.updateWaypointPanel();
      this.updateTelemetryBars();

    } catch (err) {
      optList.innerHTML = `
        <div class="alert alert-danger border border-danger p-3">
          <h6><i class="bi bi-exclamation-triangle-fill me-2"></i>Action Failed</h6>
          <p class="small mb-2">${err.message}</p>
          <button class="btn btn-outline-secondary btn-sm" onclick="ExplorationHUD.openObjectiveDialog(ExplorationHUD.activeObjective)">
            Try Again
          </button>
        </div>
      `;
    }
  },

  togglePauseMenu(forceState) {
    const pauseMenu = document.getElementById('exploration-pause-menu');
    if (!pauseMenu) return;

    if (forceState !== undefined) {
      if (forceState) pauseMenu.classList.remove('d-none');
      else pauseMenu.classList.add('d-none');
    } else {
      pauseMenu.classList.toggle('d-none');
    }
  },

  animate() {
    if (!this.isRunning) return;

    this.animationId = requestAnimationFrame(() => this.animate());

    const delta = Math.min(this.clock.getDelta(), 0.1);
    const elapsedTime = this.clock.getElapsedTime();

    // 1. Update Astronaut character
    if (this.astronaut) {
      this.astronaut.update(delta);
    }

    // 2. Animate 3D Waypoint beacons
    ExplorationEnvironments.waypoints.forEach(wp => {
      if (wp.userData && wp.userData.update) {
        wp.userData.update(delta, elapsedTime);
      }
    });

    // 3. Update Compass Radar & distances in HUD
    this.updateCompass();

    // 4. Render
    this.renderer.render(this.scene, this.camera);
  },

  updateCompass() {
    if (!this.astronaut) return;

    // Astronaut heading in degrees (0-360)
    let heading = (this.astronaut.camYaw * (180 / Math.PI)) % 360;
    if (heading < 0) heading += 360;

    const headingEl = document.getElementById('hud-compass-heading');
    if (headingEl) {
      headingEl.textContent = `${Math.round(heading)}°`;
    }

    // Update distances in panel
    this.updateWaypointPanel();
  },

  pause() {
    this.isRunning = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  },

  onResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || (window.innerHeight - 80);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }
};

