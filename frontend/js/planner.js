/**
 * Outpost Planner Component
 * Manages 100-credit budget allocation, trade-off analysis, presets,
 * real-time survival projection, and validation.
 */
const Planner = {
  totalBudget: 100,
  allocation: {
    life_support: 20,
    power_generation: 25,
    water_recycling: 20,
    food_production: 15,
    radiation_protection: 10,
    emergency_reserves: 10
  },

  tradeoffDescriptions: {
    life_support: {
      low: "Fragile O2 reserve: Minimum catalytic scrubbers. Hypoxia risk during unexpected airlock cycling.",
      med: "Nominal ECLSS: Reliable CO2 scrubbing and balanced daily oxygen electrolysis.",
      high: "Redundant scrubbers: Heavy atmospheric buffer capable of surviving extended seal failures."
    },
    power_generation: {
      low: "Brownout danger: Baseline solar panels only. Low margin for greenhouse grow lamps or dust storms.",
      med: "Balanced grid: Photovoltaics backed by regenerative fuel cell storage.",
      high: "Kilopower reactor: High continuous wattage, immunity to planetary night cycles and storms."
    },
    water_recycling: {
      low: "Leaky loop: Basic distillation; only 65% water recovery. Heavy reliance on initial reservoir.",
      med: "Closed-loop nominal: Vacuum compression filtration recovering ~85% of graywater.",
      high: "Ultra-pure closed loop: Catalytic bioreactor recovering up to 98% of crew moisture."
    },
    food_production: {
      low: "Emergency rations: Small crop bay; crew relies primarily on freeze-dried rations.",
      med: "Hydroponic balance: Active aeroponic trays provide fresh greens and calorie offset.",
      high: "Full biomass dome: Automated LED cultivation beds, high vitamin synthesis and crew morale."
    },
    radiation_protection: {
      low: "Thin skin: Minimal habitat shielding; solar particle events will deliver severe radiation doses.",
      med: "Regolith barrier: 2-meter compacted soil overburden; blocks secondary cosmic particles.",
      high: "Active magnetosphere: Superconducting deflector coils repelling high-energy CME protons."
    },
    emergency_reserves: {
      low: "Zero margin: Only 1 spare kit; any mechanical failure requires costly improvisation.",
      med: "Standard inventory: 2-3 spare cartridges and medical kits for rapid triage.",
      high: "Fully stocked: 4+ factory spares allowing immediate restoration of critical failures."
    }
  },

  init() {
    this.bindEvents();
    this.updateUI();
  },

  bindEvents() {
    const sectors = ['life_support', 'power_generation', 'water_recycling', 'food_production', 'radiation_protection', 'emergency_reserves'];
    sectors.forEach(sec => {
      const slider = document.getElementById(`slider-${sec}`);
      const numInput = document.getElementById(`input-${sec}`);
      if (slider && numInput) {
        slider.addEventListener('input', (e) => {
          this.setAllocation(sec, parseInt(e.target.value) || 0);
        });
        numInput.addEventListener('input', (e) => {
          this.setAllocation(sec, parseInt(e.target.value) || 0);
        });
      }
    });

    // Preset buttons
    document.querySelectorAll('.btn-preset').forEach(btn => {
      btn.addEventListener('click', (e) => {
        if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
        const preset = e.target.closest('.btn-preset').dataset.preset;
        this.applyPreset(preset);
      });
    });

    // Confirm deploy button
    const deployBtn = document.getElementById('btn-confirm-deploy');
    if (deployBtn) {
      deployBtn.addEventListener('click', () => {
        if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();
        this.handleDeploy();
      });
    }
  },

  setAllocation(sector, value) {
    this.allocation[sector] = Math.max(0, Math.min(100, value));
    this.updateUI();
  },

  applyPreset(presetName) {
    const presets = {
      balanced: { life_support: 20, power_generation: 25, water_recycling: 20, food_production: 15, radiation_protection: 10, emergency_reserves: 10 },
      power_heavy: { life_support: 15, power_generation: 35, water_recycling: 15, food_production: 10, radiation_protection: 15, emergency_reserves: 10 },
      eclss_focus: { life_support: 25, power_generation: 20, water_recycling: 25, food_production: 15, radiation_protection: 10, emergency_reserves: 5 },
      resilient: { life_support: 15, power_generation: 20, water_recycling: 15, food_production: 15, radiation_protection: 15, emergency_reserves: 20 }
    };
    if (presets[presetName]) {
      this.allocation = { ...presets[presetName] };
      this.updateUI();
    }
  },

  calculateTotal() {
    return Object.values(this.allocation).reduce((sum, val) => sum + val, 0);
  },

  updateUI() {
    const total = this.calculateTotal();
    const remaining = this.totalBudget - total;

    // Sliders and inputs
    Object.keys(this.allocation).forEach(sec => {
      const val = this.allocation[sec];
      const slider = document.getElementById(`slider-${sec}`);
      const numInput = document.getElementById(`input-${sec}`);
      const descEl = document.getElementById(`desc-${sec}`);

      if (slider) slider.value = val;
      if (numInput) numInput.value = val;

      if (descEl && this.tradeoffDescriptions[sec]) {
        let tier = 'med';
        if (val < 15) tier = 'low';
        else if (val >= 25) tier = 'high';
        descEl.textContent = this.tradeoffDescriptions[sec][tier];
      }
    });

    // Budget summary badge
    const budgetTotalEl = document.getElementById('planner-budget-total');
    const budgetRemainingEl = document.getElementById('planner-budget-remaining');
    const deployBtn = document.getElementById('btn-confirm-deploy');
    const warningEl = document.getElementById('planner-budget-warning');
    const survivalRateEl = document.getElementById('planner-projected-stability');

    if (budgetTotalEl) budgetTotalEl.textContent = `${total} / 100 Credits`;
    if (budgetRemainingEl) {
      budgetRemainingEl.textContent = `${remaining} Credits`;
      budgetRemainingEl.className = remaining < 0 
        ? 'text-danger font-monospace fw-bold' 
        : (remaining === 0 ? 'text-success font-monospace fw-bold' : 'text-cyan font-monospace fw-bold');
    }

    // Dynamic Projected Stability calculation
    if (survivalRateEl) {
      const balanceBonus = (this.allocation.life_support >= 15 && this.allocation.power_generation >= 20 && this.allocation.water_recycling >= 15) ? 20 : 0;
      const rawScore = Math.min(100, Math.round((total * 0.75) + balanceBonus));
      survivalRateEl.textContent = `${rawScore}% Stability`;
      survivalRateEl.className = rawScore >= 75 ? 'text-success font-monospace fw-bold' : (rawScore >= 50 ? 'text-warning font-monospace fw-bold' : 'text-danger font-monospace fw-bold');
    }

    if (deployBtn) {
      if (total > 100) {
        deployBtn.disabled = true;
        deployBtn.innerHTML = `<i class="bi bi-x-circle me-1"></i> Over Budget (${total}/100)`;
        if (warningEl) {
          warningEl.classList.remove('d-none');
          warningEl.textContent = `Budget limit exceeded by ${total - 100} credits. Reduce allocations to proceed.`;
        }
      } else if (total < 50) {
        deployBtn.disabled = true;
        deployBtn.innerHTML = `<i class="bi bi-exclamation-triangle me-1"></i> Minimum 50 Credits Required`;
        if (warningEl) {
          warningEl.classList.remove('d-none');
          warningEl.textContent = `Outpost requires at least 50 credits allocated for viable deployment. Current: ${total}.`;
        }
      } else {
        deployBtn.disabled = false;
        deployBtn.innerHTML = `<i class="bi bi-rocket-takeoff me-1"></i> Confirm & Deploy Outpost`;
        if (warningEl) warningEl.classList.add('d-none');
      }
    }
  },

  async handleDeploy() {
    if (!AppState.currentMissionId) {
      alert("No active mission briefing found. Please return to briefing.");
      return;
    }
    const deployBtn = document.getElementById('btn-confirm-deploy');
    if (deployBtn) {
      deployBtn.disabled = true;
      deployBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Pressurizing Habitat...`;
    }

    try {
      const state = await API.deployOutpost(AppState.currentMissionId, this.allocation);
      AppState.setCurrentMission(state);
      AppState.setView('dashboard');
    } catch (err) {
      alert(`Deployment failed: ${err.message}`);
      if (deployBtn) {
        deployBtn.disabled = false;
        deployBtn.innerHTML = `<i class="bi bi-rocket-takeoff me-1"></i> Confirm & Deploy Outpost`;
      }
    }
  }
};
