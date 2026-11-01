/**
 * Mission Mirror — Main Application Coordinator
 */
document.addEventListener('DOMContentLoaded', () => {
  // Initialize starfield canvas & audio system
  if (typeof Starfield !== 'undefined') Starfield.init();
  if (typeof FlightAudio !== 'undefined') FlightAudio.init();

  // Initialize subcomponents
  Planner.init();
  Dashboard.init();
  SystemsGraph.init();
  Debrief.init();
  ScienceExplorer.init();
  if (typeof UniverseView !== 'undefined') UniverseView.init();
  if (typeof ExplorationHUD !== 'undefined') ExplorationHUD.init();
  if (typeof AstronautPreview !== 'undefined') AstronautPreview.init();

  // AppState view lifecycle management
  AppState.subscribe((event, data) => {
    if (event === 'view_changed') {
      if (data === 'universe') {
        if (typeof UniverseView !== 'undefined') UniverseView.start();
        if (typeof ExplorationHUD !== 'undefined') ExplorationHUD.pause();
      } else if (data === 'exploration') {
        if (typeof UniverseView !== 'undefined') UniverseView.pause();
      } else {
        if (typeof UniverseView !== 'undefined') UniverseView.pause();
        if (typeof ExplorationHUD !== 'undefined') ExplorationHUD.pause();
      }
      if (data === 'landing' && typeof AstronautPreview !== 'undefined') {
        AstronautPreview.onResize();
      }
    }
  });

  // Navigation handlers
  setupNavigation();

  // Briefing form handlers
  setupBriefing();

  // Archive modal handlers
  setupArchive();

  // Check backend health
  checkBackendHealth();
});

function setupNavigation() {
  document.querySelectorAll('[data-nav-view]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
      const targetView = el.dataset.navView;
      AppState.setView(targetView);

      // Update active nav link style
      document.querySelectorAll('.nav-tab-btn').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.querySelector(`.nav-tab-btn[data-nav-view="${targetView}"]`);
      if (activeBtn) activeBtn.classList.add('active');
    });
  });

  // Universe quick planet selector pills
  document.querySelectorAll('.btn-planet-quick').forEach(btn => {
    btn.addEventListener('click', (e) => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
      document.querySelectorAll('.btn-planet-quick').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const planetId = btn.dataset.planet;
      if (typeof UniverseView !== 'undefined') {
        UniverseView.focusPlanet(planetId);
      }
    });
  });

  // Hero & Dashboard EVA Exploration Shortcuts
  const heroEvaBtn = document.getElementById('btn-hero-launch-eva');
  if (heroEvaBtn) {
    heroEvaBtn.addEventListener('click', () => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();
      if (typeof ExplorationHUD !== 'undefined') {
        ExplorationHUD.startExploration('moon');
      }
    });
  }

  const dashLaunchBtn = document.getElementById('btn-dashboard-launch-eva');
  if (dashLaunchBtn) {
    dashLaunchBtn.addEventListener('click', () => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();
      const dest = (AppState.currentMission && AppState.currentMission.destination) ? AppState.currentMission.destination : 'moon';
      if (typeof ExplorationHUD !== 'undefined') {
        ExplorationHUD.startExploration(dest);
      }
    });
  }

  // Dashboard EVA Exploration Shortcut
  const dashboardEvaBtn = document.getElementById('btn-dashboard-eva');
  if (dashboardEvaBtn) {
    dashboardEvaBtn.addEventListener('click', () => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();
      const dest = (AppState.currentMission && AppState.currentMission.destination) ? AppState.currentMission.destination : 'moon';
      if (typeof ExplorationHUD !== 'undefined') {
        ExplorationHUD.startExploration(dest);
      }
    });
  }

  const startBtn = document.getElementById('btn-hero-start');
  if (startBtn) {
    startBtn.addEventListener('click', () => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();
      AppState.setView('briefing');
    });
  }

  const howBtn = document.getElementById('btn-hero-how');
  if (howBtn) {
    howBtn.addEventListener('click', () => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
      const modalEl = document.getElementById('how-it-works-modal');
      if (modalEl && window.bootstrap) {
        const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
        bsModal.show();
      }
    });
  }
}

function setupBriefing() {
  let selectedDestination = 'moon';
  let selectedDuration = 10;
  let selectedDifficulty = 'intermediate';

  document.querySelectorAll('.dest-card').forEach(card => {
    card.addEventListener('click', (e) => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
      document.querySelectorAll('.dest-card').forEach(c => c.classList.remove('selected'));
      const selected = e.target.closest('.dest-card');
      selected.classList.add('selected');
      selectedDestination = selected.dataset.destination;
    });
  });

  document.querySelectorAll('.btn-duration').forEach(btn => {
    btn.addEventListener('click', (e) => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
      document.querySelectorAll('.btn-duration').forEach(b => b.classList.remove('active'));
      const selected = e.target.closest('.btn-duration');
      selected.classList.add('active');
      selectedDuration = parseInt(selected.dataset.days);
    });
  });

  document.querySelectorAll('.btn-difficulty').forEach(btn => {
    btn.addEventListener('click', (e) => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
      document.querySelectorAll('.btn-difficulty').forEach(b => b.classList.remove('active'));
      const selected = e.target.closest('.btn-difficulty');
      selected.classList.add('active');
      selectedDifficulty = selected.dataset.difficulty;
    });
  });

  const proceedBtn = document.getElementById('btn-proceed-to-planner');
  if (proceedBtn) {
    proceedBtn.addEventListener('click', async () => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();
      const commanderInput = document.getElementById('input-commander-name');
      const commanderName = (commanderInput && commanderInput.value.trim()) ? commanderInput.value.trim() : 'Cadet Explorer';

      proceedBtn.disabled = true;
      proceedBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Transmitting Flight Plan...`;

      try {
        const payload = {
          destination: selectedDestination,
          duration_days: selectedDuration,
          difficulty: selectedDifficulty,
          commander_name: commanderName
        };

        const missionState = await API.createMission(payload);
        AppState.setCurrentMission(missionState);

        const plannerDestEl = document.getElementById('planner-meta-dest');
        const plannerDiffEl = document.getElementById('planner-meta-diff');
        const plannerDaysEl = document.getElementById('planner-meta-days');
        if (plannerDestEl) plannerDestEl.textContent = selectedDestination.toUpperCase();
        if (plannerDiffEl) plannerDiffEl.textContent = selectedDifficulty.toUpperCase();
        if (plannerDaysEl) plannerDaysEl.textContent = `${selectedDuration} DAYS`;

        AppState.setView('planner');
      } catch (err) {
        alert(`Failed to establish mission briefing: ${err.message}`);
      } finally {
        proceedBtn.disabled = false;
        proceedBtn.innerHTML = `Proceed to Outpost Planner <i class="bi bi-arrow-right ms-1"></i>`;
      }
    });
  }
}

function setupArchive() {
  const archiveBtn = document.getElementById('btn-open-archive');
  if (archiveBtn) {
    archiveBtn.addEventListener('click', async () => {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
      const modalEl = document.getElementById('archive-modal');
      const listContainer = document.getElementById('archive-mission-list');

      if (listContainer) {
        listContainer.innerHTML = `<div class="text-center py-4"><span class="spinner-border text-cyan"></span><p class="text-muted small mt-2">Accessing SQLite Mission Logs...</p></div>`;
      }

      if (modalEl && window.bootstrap) {
        const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
        bsModal.show();
      }

      try {
        const missions = await API.listMissions();
        if (!missions || missions.length === 0) {
          if (listContainer) listContainer.innerHTML = `<p class="text-muted text-center py-4">No previous mission logs found in database.</p>`;
          return;
        }

        if (listContainer) {
          listContainer.innerHTML = missions.map(m => `
            <div class="astro-card p-3 mb-2 d-flex justify-content-between align-items-center">
              <div>
                <div class="fw-bold text-white">
                  ${m.commander_name} 
                  ${m.is_replay ? '<span class="badge bg-info text-dark ms-1 font-monospace">Counterfactual Replay</span>' : ''}
                </div>
                <div class="text-muted small">
                  <span class="text-cyan fw-bold">${m.destination.toUpperCase()}</span> &bull; 
                  <span>${m.duration_days} Days</span> &bull; 
                  <span>Status: <b class="${m.status === 'completed' ? 'text-success' : (m.status === 'failed' ? 'text-danger' : 'text-warning')}">${m.status.toUpperCase()}</b></span> &bull; 
                  <span>Score: <b class="text-white">${m.score}</b></span>
                </div>
                <div class="text-dim" style="font-size:0.75rem;">Created: ${m.created_at}</div>
              </div>
              <div class="d-flex gap-2">
                <button class="btn btn-sm btn-astro-secondary btn-load-archive-mission" data-mission-id="${m.id}">
                  <i class="bi bi-box-arrow-in-right me-1"></i>Load Telemetry
                </button>
              </div>
            </div>
          `).join('');

          listContainer.querySelectorAll('.btn-load-archive-mission').forEach(btn => {
            btn.addEventListener('click', async (e) => {
              const missionId = e.target.closest('.btn-load-archive-mission').dataset.missionId;
              try {
                const state = await API.getMissionState(missionId);
                AppState.setCurrentMission(state);
                if (modalEl && window.bootstrap) {
                  const bsModal = bootstrap.Modal.getInstance(modalEl);
                  if (bsModal) bsModal.hide();
                }
                if (state.status === 'completed' || state.status === 'failed') {
                  AppState.setView('debrief');
                  Debrief.loadReport(missionId);
                } else if (state.status === 'planning') {
                  AppState.setView('planner');
                } else {
                  AppState.setView('dashboard');
                }
              } catch (err) {
                alert(`Could not load mission: ${err.message}`);
              }
            });
          });
        }
      } catch (err) {
        if (listContainer) listContainer.innerHTML = `<div class="alert alert-danger">Error loading missions: ${err.message}</div>`;
      }
    });
  }
}

async function checkBackendHealth() {
  try {
    const health = await API.getHealth();
    const statusDot = document.getElementById('nav-health-status');
    if (statusDot) {
      statusDot.className = 'status-pill healthy';
      statusDot.innerHTML = `<i class="bi bi-circle-fill" style="font-size:0.5rem;"></i> Telemetry Linked`;
    }
  } catch (err) {
    const statusDot = document.getElementById('nav-health-status');
    if (statusDot) {
      statusDot.className = 'status-pill critical';
      statusDot.innerHTML = `<i class="bi bi-circle-fill" style="font-size:0.5rem;"></i> Link Severed`;
    }
  }
}
