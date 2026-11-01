/**
 * Mission Debrief & Counterfactual Replay Component
 * Telemetry charting with Chart.js, comparative counterfactual analysis, and lessons learned.
 */
const Debrief = {
  telemetryChart: null,
  comparisonChart: null,

  init() {
    this.bindEvents();
  },

  bindEvents() {
    const replayBtn = document.getElementById('btn-launch-replay');
    if (replayBtn) {
      replayBtn.addEventListener('click', () => this.handleLaunchReplay());
    }

    const backToDashboardBtn = document.getElementById('btn-debrief-to-dashboard');
    if (backToDashboardBtn) {
      backToDashboardBtn.addEventListener('click', () => AppState.setView('dashboard'));
    }

    const backHomeBtn = document.getElementById('btn-debrief-home');
    if (backHomeBtn) {
      backHomeBtn.addEventListener('click', () => AppState.setView('landing'));
    }
  },

  async loadReport(missionId) {
    try {
      const report = await API.getMissionReport(missionId);
      this.renderReport(report);
    } catch (err) {
      console.error("Failed to load mission debrief report:", err);
    }
  },

  renderReport(report) {
    const outcomeEl = document.getElementById('debrief-outcome');
    const scoreEl = document.getElementById('debrief-score');
    const gradeEl = document.getElementById('debrief-grade');
    const daysEl = document.getElementById('debrief-days');
    const objsEl = document.getElementById('debrief-objectives');
    const challengeEl = document.getElementById('debrief-next-challenge');
    const lessonsList = document.getElementById('debrief-lessons-list');
    const decisionsTable = document.getElementById('debrief-decisions-table');
    const counterfactualSection = document.getElementById('debrief-counterfactual-section');

    if (outcomeEl) {
      outcomeEl.textContent = report.outcome.toUpperCase();
      outcomeEl.className = report.outcome.includes('Success') ? 'text-success fw-bold' : 'text-danger fw-bold';
    }
    if (scoreEl) scoreEl.textContent = report.final_score;
    if (gradeEl) gradeEl.textContent = report.grade;
    if (daysEl) daysEl.textContent = `${report.days_survived} / ${report.total_days} Days`;
    if (objsEl) objsEl.textContent = `${report.objectives_completed} / ${report.total_objectives} Met`;
    if (challengeEl) challengeEl.textContent = report.recommended_challenge;

    // Lessons learned
    if (lessonsList && report.lessons_learned) {
      lessonsList.innerHTML = report.lessons_learned.map(l => `
        <li class="mb-2 text-light">
          <i class="bi bi-lightbulb text-warning me-2"></i>${l}
        </li>
      `).join('');
    }

    // Key decisions table
    if (decisionsTable && report.key_decisions) {
      if (report.key_decisions.length === 0) {
        decisionsTable.innerHTML = `<tr><td colspan="4" class="text-white text-center py-3 font-monospace">No dynamic anomalies occurred during this run.</td></tr>`;
      } else {
        decisionsTable.innerHTML = report.key_decisions.map(d => `
          <tr>
            <td class="font-monospace text-cyan fw-bold">Day ${d.day}</td>
            <td class="fw-bold text-white">${d.choice}</td>
            <td class="text-light" style="font-size:0.92rem;">${d.impact}</td>
            <td class="text-cyan font-monospace" style="font-size:0.9rem;">${d.scientific_concept || 'ECLSS Resource Triage'}</td>
          </tr>
        `).join('');
      }
    }

    // Render Telemetry Chart
    this.renderTelemetryChart(report.telemetry_history);

    // If this is a replay or has counterfactual comparison data, render it!
    if (report.counterfactual_comparison) {
      if (counterfactualSection) counterfactualSection.classList.remove('d-none');
      this.renderCounterfactualComparison(report.counterfactual_comparison);
    } else {
      if (counterfactualSection) counterfactualSection.classList.add('d-none');
    }
  },

  renderTelemetryChart(telemetry) {
    const canvas = document.getElementById('chart-telemetry');
    if (!canvas || !window.Chart) return;

    if (this.telemetryChart) {
      this.telemetryChart.destroy();
    }

    const labels = telemetry.map(t => `Day ${t.day}`);
    const o2Data = telemetry.map(t => t.oxygen);
    const waterData = telemetry.map(t => t.water);
    const energyData = telemetry.map(t => t.energy);
    const healthData = telemetry.map(t => t.crew_health);

    const ctx = canvas.getContext('2d');
    this.telemetryChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          { label: 'Oxygen (%)', data: o2Data, borderColor: '#06b6d4', backgroundColor: 'rgba(6, 182, 212, 0.1)', tension: 0.3, fill: false },
          { label: 'Water (%)', data: waterData, borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', tension: 0.3, fill: false },
          { label: 'Energy (%)', data: energyData, borderColor: '#f59e0b', backgroundColor: 'rgba(245, 158, 11, 0.1)', tension: 0.3, fill: false },
          { label: 'Crew Health (%)', data: healthData, borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', tension: 0.3, fill: false }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#94a3b8', font: { family: 'SFMono-Regular, Consolas' } } }
        },
        scales: {
          x: { grid: { color: 'rgba(30, 49, 88, 0.4)' }, ticks: { color: '#94a3b8' } },
          y: { min: 0, max: 100, grid: { color: 'rgba(30, 49, 88, 0.4)' }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  },

  renderCounterfactualComparison(comparison) {
    const deltaScoreEl = document.getElementById('cf-score-delta');
    const deltaDaysEl = document.getElementById('cf-days-delta');
    const divergencesTable = document.getElementById('cf-divergences-table');
    const attributionList = document.getElementById('cf-attribution-list');
    const canvas = document.getElementById('chart-counterfactual');

    if (deltaScoreEl) {
      const delta = comparison.deltas.score_delta;
      deltaScoreEl.textContent = `${delta >= 0 ? '+' : ''}${delta} pts`;
      deltaScoreEl.className = delta >= 0 ? 'text-success fw-bold' : 'text-danger fw-bold';
    }

    if (deltaDaysEl) {
      const delta = comparison.deltas.days_survived_delta;
      deltaDaysEl.textContent = `${delta >= 0 ? '+' : ''}${delta} days`;
    }

    if (attributionList && comparison.deltas.outcome_attribution) {
      attributionList.innerHTML = comparison.deltas.outcome_attribution.map(a => `
        <li class="mb-1 text-light"><i class="bi bi-arrow-right-circle text-info me-2"></i>${a}</li>
      `).join('');
    }

    if (divergencesTable && comparison.deltas.decision_divergences) {
      if (comparison.deltas.decision_divergences.length === 0) {
        divergencesTable.innerHTML = `<tr><td colspan="3" class="text-muted text-center py-2">Identical tactical choices made in both runs.</td></tr>`;
      } else {
        divergencesTable.innerHTML = comparison.deltas.decision_divergences.map(d => `
          <tr>
            <td class="font-monospace text-info">Day ${d.day}</td>
            <td class="text-danger small"><i class="bi bi-x-circle me-1"></i>${d.original_choice}</td>
            <td class="text-success small"><i class="bi bi-check-circle me-1"></i>${d.counterfactual_choice}</td>
          </tr>
        `).join('');
      }
    }

    // Render comparison chart: Crew Health of Original vs Replay
    if (canvas && window.Chart) {
      if (this.comparisonChart) {
        this.comparisonChart.destroy();
      }

      const origTelemetry = comparison.original_run.telemetry;
      const altTelemetry = comparison.counterfactual_run.telemetry;

      const maxDays = Math.max(origTelemetry.length, altTelemetry.length);
      const labels = Array.from({ length: maxDays }, (_, i) => `Day ${i + 1}`);

      const origHealth = labels.map((_, i) => origTelemetry[i] ? origTelemetry[i].crew_health : null);
      const altHealth = labels.map((_, i) => altTelemetry[i] ? altTelemetry[i].crew_health : null);

      const ctx = canvas.getContext('2d');
      this.comparisonChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Original Run (Crew Health)',
              data: origHealth,
              borderColor: '#f43f5e',
              borderDash: [5, 5],
              backgroundColor: 'rgba(244, 63, 94, 0.1)',
              tension: 0.3,
              fill: false
            },
            {
              label: 'Counterfactual Replay (Crew Health)',
              data: altHealth,
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              tension: 0.3,
              fill: false
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#94a3b8', font: { family: 'SFMono-Regular, Consolas' } } }
          },
          scales: {
            x: { grid: { color: 'rgba(30, 49, 88, 0.4)' }, ticks: { color: '#94a3b8' } },
            y: { min: 0, max: 100, grid: { color: 'rgba(30, 49, 88, 0.4)' }, ticks: { color: '#94a3b8' } }
          }
        }
      });
    }
  },

  async handleLaunchReplay() {
    if (!AppState.currentMissionId) return;

    const replayBtn = document.getElementById('btn-launch-replay');
    if (replayBtn) {
      replayBtn.disabled = true;
      replayBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Cloning Initial Simulation State...`;
    }

    try {
      const replayState = await API.createReplay(AppState.currentMissionId);
      AppState.setCurrentMission(replayState);
      AppState.setView('dashboard');
    } catch (err) {
      alert(`Could not launch counterfactual replay: ${err.message}`);
      if (replayBtn) {
        replayBtn.disabled = false;
        replayBtn.innerHTML = `<i class="bi bi-arrow-repeat me-1"></i> Launch Counterfactual Replay`;
      }
    }
  }
};

