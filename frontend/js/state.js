/**
 * Global Application State
 */
const AppState = {
  activeView: 'landing', // 'landing', 'briefing', 'planner', 'dashboard', 'debrief', 'replay_compare', 'science'
  currentMission: null,   // Current MissionStateResponse from API
  currentMissionId: null,
  previousRunData: null,  // For counterfactual comparison
  scienceData: [],
  selectedGraphNode: null,

  listeners: [],

  subscribe(listener) {
    this.listeners.push(listener);
  },

  notify(event, data) {
    this.listeners.forEach(fn => fn(event, data));
  },

  setCurrentMission(mission) {
    this.currentMission = mission;
    if (mission && mission.mission_id) {
      this.currentMissionId = mission.mission_id;
    }
    this.notify('mission_updated', this.currentMission);
  },

  setView(viewName) {
    this.activeView = viewName;
    document.querySelectorAll('.view-section').forEach(el => {
      el.classList.add('d-none');
    });
    const target = document.getElementById(`view-${viewName}`);
    if (target) {
      target.classList.remove('d-none');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    this.notify('view_changed', viewName);
  }
};

