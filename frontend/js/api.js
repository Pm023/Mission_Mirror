/**
 * Mission Mirror REST API Client
 */
const API = {
  baseUrl: '',

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    const config = {
      ...options,
      headers: { ...defaultHeaders, ...(options.headers || {}) }
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      if (!response.ok) {
        const errorMsg = data.detail || (data.message ? data.message : 'API Request failed');
        throw new Error(errorMsg);
      }
      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  // Health
  getHealth() {
    return this.request('/api/health');
  },

  // Missions
  createMission(payload) {
    return this.request('/api/missions', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  listMissions() {
    return this.request('/api/missions');
  },

  getMissionState(missionId) {
    return this.request(`/api/missions/${missionId}/state`);
  },

  deployOutpost(missionId, allocation) {
    return this.request(`/api/missions/${missionId}/deploy`, {
      method: 'POST',
      body: JSON.stringify(allocation)
    });
  },

  advanceDay(missionId) {
    return this.request(`/api/missions/${missionId}/advance`, {
      method: 'POST'
    });
  },

  submitDecision(missionId, choiceId) {
    return this.request(`/api/missions/${missionId}/decisions`, {
      method: 'POST',
      body: JSON.stringify({ choice_id: choiceId })
    });
  },

  getSystemsGraph(missionId) {
    return this.request(`/api/missions/${missionId}/systems`);
  },

  getMissionReport(missionId) {
    return this.request(`/api/missions/${missionId}/report`);
  },

  createReplay(missionId) {
    return this.request(`/api/missions/${missionId}/replay`, {
      method: 'POST'
    });
  },

  compareMissions(missionId, otherId) {
    return this.request(`/api/missions/${missionId}/compare/${otherId}`);
  },

  // Science
  getScienceResources() {
    return this.request('/api/science/resources');
  },

  // Mentor explain
  mentorExplain(payload) {
    return this.request('/api/mentor/explain', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // 3D Exploration & Universe
  getExplorationObjectives(environment, missionId = null) {
    const q = missionId ? `?mission_id=${encodeURIComponent(missionId)}` : '';
    return this.request(`/api/exploration/objectives/${environment}${q}`);
  },

  submitMissionExplorationAction(missionId, objectiveId, optionId) {
    return this.request(`/api/exploration/missions/${missionId}/action`, {
      method: 'POST',
      body: JSON.stringify({
        objective_id: objectiveId,
        option_id: optionId
      })
    });
  },

  submitSandboxExplorationAction(objectiveId, optionId) {
    return this.request('/api/exploration/sandbox/action', {
      method: 'POST',
      body: JSON.stringify({
        objective_id: objectiveId,
        option_id: optionId
      })
    });
  }
};
