/**
 * Mission Control Dashboard Component
 * Manages live telemetry HUD, audio synthesis, blueprint cutaways,
 * auto-advance simulation speed, dynamic event modal, and mentor drawer.
 */
const Dashboard = {
  activeChoiceId: null,
  isAutoAdvancing: false,
  autoAdvanceTimer: null,
  autoSpeedMs: 1600,

  init() {
    this.bindEvents();
    AppState.subscribe((event, data) => {
      if (event === 'mission_updated') {
        this.render(data);
      }
    });
  },

  bindEvents() {
    const advanceBtn = document.getElementById('btn-advance-day');
    if (advanceBtn) {
      advanceBtn.addEventListener('click', () => {
        if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
        this.handleAdvanceDay();
      });
    }

    // Auto-advance play/pause toggle
    const autoPlayBtn = document.getElementById('btn-auto-advance');
    if (autoPlayBtn) {
      autoPlayBtn.addEventListener('click', () => this.toggleAutoAdvance());
    }

    const mentorToggle = document.getElementById('btn-toggle-mentor');
    if (mentorToggle) {
      mentorToggle.addEventListener('click', () => {
        if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
        const drawer = document.getElementById('mentor-offcanvas');
        if (drawer && window.bootstrap) {
          const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(drawer);
          bsOffcanvas.toggle();
        }
      });
    }

    // Modal decision submit
    const submitDecisionBtn = document.getElementById('btn-submit-event-decision');
    if (submitDecisionBtn) {
      submitDecisionBtn.addEventListener('click', () => this.handleDecisionSubmit());
    }

    // Guided Tour / Cadet Orientation trigger
    const tourBtn = document.getElementById('btn-cadet-tour');
    if (tourBtn) {
      tourBtn.addEventListener('click', () => this.startCadetTour());
    }
  },

  toggleAutoAdvance() {
    const btn = document.getElementById('btn-auto-advance');
    if (this.isAutoAdvancing) {
      this.stopAutoAdvance();
    } else {
      if (!AppState.currentMission || AppState.currentMission.status !== 'active') return;
      if (AppState.currentMission.active_event) {
        alert("Cannot auto-advance while an anomaly requires your decision.");
        return;
      }
      this.isAutoAdvancing = true;
      if (btn) {
        btn.classList.add('btn-warning');
        btn.classList.remove('btn-astro-secondary');
        btn.innerHTML = `<i class="bi bi-pause-fill me-1"></i>Pause Simulation`;
      }
      this.runAutoStep();
    }
  },

  stopAutoAdvance() {
    this.isAutoAdvancing = false;
    if (this.autoAdvanceTimer) {
      clearTimeout(this.autoAdvanceTimer);
      this.autoAdvanceTimer = null;
    }
    const btn = document.getElementById('btn-auto-advance');
    if (btn) {
      btn.classList.remove('btn-warning');
      btn.classList.add('btn-astro-secondary');
      btn.innerHTML = `<i class="bi bi-play-fill me-1"></i>Auto Run`;
    }
  },

  async runAutoStep() {
    if (!this.isAutoAdvancing) return;
    if (!AppState.currentMission || AppState.currentMission.status !== 'active' || AppState.currentMission.active_event) {
      this.stopAutoAdvance();
      return;
    }

    await this.handleAdvanceDay();

    if (this.isAutoAdvancing && AppState.currentMission && AppState.currentMission.status === 'active' && !AppState.currentMission.active_event) {
      this.autoAdvanceTimer = setTimeout(() => this.runAutoStep(), this.autoSpeedMs);
    } else {
      this.stopAutoAdvance();
    }
  },

  render(mission) {
    if (!mission) return;

    // Mission meta
    const dayEl = document.getElementById('hud-day-counter');
    const destEl = document.getElementById('hud-destination');
    const diffEl = document.getElementById('hud-difficulty');
    const scoreEl = document.getElementById('hud-score');
    const cmdEl = document.getElementById('hud-commander');
    const progressBar = document.getElementById('hud-day-progress');
    const advanceBtn = document.getElementById('btn-advance-day');

    if (dayEl) dayEl.textContent = `Day ${mission.current_day} / ${mission.total_days}`;
    if (destEl) destEl.textContent = mission.destination.toUpperCase();
    if (diffEl) diffEl.textContent = mission.difficulty.toUpperCase();
    if (scoreEl) scoreEl.textContent = mission.score;
    if (cmdEl) cmdEl.textContent = mission.commander_name;

    const progressPct = mission.total_days > 0 ? (mission.current_day / mission.total_days) * 100 : 0;
    if (progressBar) progressBar.style.width = `${progressPct}%`;

    // Resource Meters
    this.updateGauge('oxygen', mission.resources.oxygen, '%');
    this.updateGauge('water', mission.resources.water, '%');
    this.updateGauge('food', mission.resources.food, '%');
    this.updateGauge('energy', mission.resources.energy, '%');
    this.updateGauge('crew-health', mission.resources.crew_health, '%');
    this.updateGauge('systems', mission.resources.system_condition, '%');

    // Crew Vitals
    const crewStatusEl = document.getElementById('hud-crew-status');
    const crewRadEl = document.getElementById('hud-crew-rad');
    const crewCountEl = document.getElementById('hud-crew-count');

    if (crewStatusEl) {
      crewStatusEl.textContent = mission.crew.status.toUpperCase();
      crewStatusEl.className = `status-pill ${mission.crew.status === 'nominal' ? 'healthy' : (mission.crew.status === 'fatigued' ? 'warning' : 'critical')}`;
    }
    if (crewRadEl) crewRadEl.textContent = `${mission.crew.radiation_dose_msv.toFixed(1)} mSv`;
    if (crewCountEl) crewCountEl.textContent = `${mission.crew.crew_count} Astronauts`;

    // Objectives list
    const objListEl = document.getElementById('hud-objectives-list');
    if (objListEl && mission.objectives) {
      objListEl.innerHTML = mission.objectives.map(o => `
        <div class="mb-2 p-2 rounded bg-dark border border-secondary">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="fw-bold ${o.completed ? 'text-success' : 'text-white'}" style="font-size:0.92rem;">
              <i class="bi ${o.completed ? 'bi-check-circle-fill text-success' : 'bi-circle text-info'} me-1"></i>
              ${o.title}
            </span>
            <span class="badge ${o.completed ? 'bg-success text-dark fw-bold' : 'bg-secondary text-white font-monospace'}" style="font-size:0.75rem;">
              ${o.progress.toFixed(0)}%
            </span>
          </div>
          <div class="text-light" style="font-size:0.86rem; line-height:1.4;">${o.description}</div>
        </div>
      `).join('');
    }

    // Critical Warnings Banner & Sound
    const warnContainer = document.getElementById('hud-critical-warnings');
    if (warnContainer) {
      if (mission.warnings && mission.warnings.length > 0) {
        warnContainer.innerHTML = mission.warnings.map(w => `
          <div class="alert alert-danger py-2 px-3 small d-flex align-items-center mb-2" role="alert">
            <i class="bi bi-exclamation-octagon-fill fs-5 me-2 text-danger"></i>
            <div>${w}</div>
          </div>
        `).join('');
        warnContainer.classList.remove('d-none');
        if (typeof FlightAudio !== 'undefined') FlightAudio.playWarningChime();
      } else {
        warnContainer.classList.add('d-none');
      }
    }

    // Terminal log
    const logBox = document.getElementById('hud-log-box');
    if (logBox && mission.recent_logs) {
      logBox.innerHTML = mission.recent_logs.map(l => {
        let cls = '';
        if (l.includes('CRITICAL') || l.includes('Failed') || l.includes('ALERT')) cls = 'crit';
        else if (l.includes('Warning') || l.includes('strained')) cls = 'warn';
        return `<div class="log-entry ${cls}"><span class="text-dim">❯</span> ${l}</div>`;
      }).join('');
      logBox.scrollTop = logBox.scrollHeight;
    }

    // Active Dynamic Event Modal Trigger
    if (mission.active_event && !mission.active_event.resolved) {
      this.stopAutoAdvance();
      this.displayEventModal(mission.active_event);
      if (advanceBtn) {
        advanceBtn.disabled = true;
        advanceBtn.innerHTML = `<i class="bi bi-exclamation-triangle me-1"></i> Anomaly Pending Action`;
      }
      if (typeof FlightAudio !== 'undefined') FlightAudio.playEmergencyKlaxon();
    } else {
      if (advanceBtn) {
        if (mission.status === 'active') {
          advanceBtn.disabled = false;
          advanceBtn.innerHTML = `<i class="bi bi-fast-forward-fill me-1"></i> Advance Day (+24h Tick)`;
        } else {
          advanceBtn.disabled = true;
          advanceBtn.innerHTML = `<i class="bi bi-flag-fill me-1"></i> Mission ${mission.status.toUpperCase()}`;
        }
      }
    }

    // Check completion or failure
    if (mission.status === 'completed' || mission.status === 'failed') {
      this.stopAutoAdvance();
      if (typeof FlightAudio !== 'undefined') {
        if (mission.status === 'completed') FlightAudio.playSuccessChime();
        else FlightAudio.playEmergencyKlaxon();
      }
      setTimeout(() => {
        AppState.setView('debrief');
        Debrief.loadReport(mission.mission_id);
      }, 1200);
    }

    // Update Systems Dependency Graph & Habitat Blueprint Cutaway
    if (typeof SystemsGraph !== 'undefined') {
      SystemsGraph.render(mission.mission_id);
    }
    if (typeof HabitatView !== 'undefined') {
      HabitatView.render(mission.systems, mission.resources);
    }

    // Update Mentor Drawer if advice exists
    if (mission.mentor_advice) {
      this.updateMentorDrawer(mission.mentor_advice);
    }
  },

  updateGauge(idPrefix, val, unit) {
    const valEl = document.getElementById(`val-${idPrefix}`);
    const barEl = document.getElementById(`bar-${idPrefix}`);
    if (!valEl || !barEl) return;

    valEl.textContent = `${val.toFixed(1)}${unit}`;
    barEl.style.width = `${Math.min(100, Math.max(0, val))}%`;

    let status = 'healthy';
    if (val < 30) status = 'critical';
    else if (val < 60) status = 'warning';

    barEl.className = `astro-progress-bar ${status}`;
  },

  displayEventModal(event) {
    const modalEl = document.getElementById('anomaly-modal');
    if (!modalEl || !window.bootstrap) return;

    const titleEl = document.getElementById('modal-event-title');
    const descEl = document.getElementById('modal-event-desc');
    const sevEl = document.getElementById('modal-event-severity');
    const choicesContainer = document.getElementById('modal-event-choices');
    const submitBtn = document.getElementById('btn-submit-event-decision');

    if (titleEl) titleEl.textContent = event.title;
    if (descEl) descEl.textContent = event.description;
    if (sevEl) {
      sevEl.textContent = event.severity.toUpperCase();
      sevEl.className = `badge bg-${event.severity === 'critical' ? 'danger' : (event.severity === 'high' ? 'warning' : 'info')}`;
    }

    this.activeChoiceId = event.choices[0] ? event.choices[0].id : null;

    if (choicesContainer) {
      choicesContainer.innerHTML = event.choices.map((c, idx) => `
        <div class="choice-card mb-2 ${idx === 0 ? 'selected' : ''}" data-choice-id="${c.id}">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="fw-bold text-cyan" style="font-family: var(--font-title); font-size:1.05rem;">${c.title}</span>
            <span class="badge bg-dark border border-secondary text-info font-monospace" style="font-size:0.7rem;">Protocol ${idx + 1}</span>
          </div>
          <p class="small text-light mb-2">${c.description}</p>
          <div class="d-flex flex-wrap gap-2 small">
            <span class="badge bg-secondary font-monospace"><i class="bi bi-speedometer2 me-1"></i>${c.resource_impact_preview}</span>
            <span class="badge bg-dark border border-secondary text-warning font-monospace"><i class="bi bi-arrow-left-right me-1"></i>${c.tradeoff_summary}</span>
          </div>
        </div>
      `).join('');

      choicesContainer.querySelectorAll('.choice-card').forEach(card => {
        card.addEventListener('click', (e) => {
          if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
          choicesContainer.querySelectorAll('.choice-card').forEach(c => c.classList.remove('selected'));
          const selected = e.target.closest('.choice-card');
          selected.classList.add('selected');
          this.activeChoiceId = selected.dataset.choiceId;
          if (submitBtn) submitBtn.disabled = false;
        });
      });
    }

    const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false });
    bsModal.show();
  },

  async handleDecisionSubmit() {
    if (!AppState.currentMissionId || !this.activeChoiceId) return;

    const submitBtn = document.getElementById('btn-submit-event-decision');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Applying Triage Protocols...`;
    }

    try {
      const state = await API.submitDecision(AppState.currentMissionId, this.activeChoiceId);
      AppState.setCurrentMission(state);

      const modalEl = document.getElementById('anomaly-modal');
      if (modalEl && window.bootstrap) {
        const bsModal = bootstrap.Modal.getInstance(modalEl);
        if (bsModal) bsModal.hide();
      }

      if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();

      // Open mentor drawer with pedagogical explanation
      const drawer = document.getElementById('mentor-offcanvas');
      if (drawer && window.bootstrap) {
        const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(drawer);
        bsOffcanvas.show();
      }
    } catch (err) {
      alert(`Decision submission failed: ${err.message}`);
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="bi bi-check2-circle me-1"></i> Execute Protocol Choice`;
      }
    }
  },

  async handleAdvanceDay() {
    if (!AppState.currentMissionId) return;

    const advanceBtn = document.getElementById('btn-advance-day');
    if (advanceBtn) {
      advanceBtn.disabled = true;
      advanceBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Advancing 24h Cycle...`;
    }

    try {
      const state = await API.advanceDay(AppState.currentMissionId);
      AppState.setCurrentMission(state);
      if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();
    } catch (err) {
      alert(`Advance failed: ${err.message}`);
      if (advanceBtn) {
        advanceBtn.disabled = false;
        advanceBtn.innerHTML = `<i class="bi bi-fast-forward-fill me-1"></i> Advance Day (+24h Tick)`;
      }
    }
  },

  updateMentorDrawer(advice) {
    const whatChangedEl = document.getElementById('mentor-what-changed');
    const whyEl = document.getElementById('mentor-why-changed');
    const systemsEl = document.getElementById('mentor-affected-systems');
    const monitorEl = document.getElementById('mentor-what-monitor');
    const conceptEl = document.getElementById('mentor-scientific-concept');
    const sourceBadge = document.getElementById('mentor-source-badge');

    if (whatChangedEl) whatChangedEl.textContent = advice.what_changed;
    if (whyEl) whyEl.textContent = advice.why_it_changed;
    if (monitorEl) monitorEl.textContent = advice.what_to_monitor;
    if (conceptEl) conceptEl.textContent = advice.scientific_concept;

    if (systemsEl && advice.affected_systems) {
      systemsEl.innerHTML = advice.affected_systems.map(s => `
        <span class="badge bg-dark border border-cyan text-cyan me-1 font-monospace">${s}</span>
      `).join('');
    }

    if (sourceBadge) {
      if (advice.source === 'ai_model') {
        sourceBadge.textContent = "AI Mentor (Augmented)";
        sourceBadge.className = "mentor-badge";
      } else {
        sourceBadge.textContent = "Rule-Based Physics Engine";
        sourceBadge.className = "badge bg-secondary text-light font-monospace";
      }
    }
  },

  startCadetTour() {
    // Quick guided walk-through alerting cadet of key HUD elements
    alert(
      "🚀 CADET MISSION CONTROL ORIENTATION:\n\n" +
      "1. TOP HUD: Tracks elapsed days, score, and flight progress.\n" +
      "2. TELEMETRY GAUGES: Oxygen, Water, Food, Energy, Crew Health, and Systems. Keep all above 30%!\n" +
      "3. HABITAT BLUEPRINT: Live visual cutaway of the outpost. Notice how modules pulse according to health.\n" +
      "4. DEPENDENCY EXPLORER: Interconnected systems! Power directly feeds water pumps and oxygen scrubbers.\n" +
      "5. ADVANCE DAY: Runs a 24-hour simulation tick. Handle anomalies when they arise to keep your crew safe!"
    );
  }
};
