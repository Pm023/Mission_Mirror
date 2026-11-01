/**
 * Science Explorer Component
 * Verified open-access NASA science facts, life support concepts, and educational citations.
 */
const ScienceExplorer = {
  topics: [],

  init() {
    this.loadTopics();
  },

  async loadTopics() {
    try {
      this.topics = await API.getScienceResources();
      this.render();
    } catch (err) {
      console.error("Failed to load science topics:", err);
    }
  },

  render() {
    const container = document.getElementById('science-topics-grid');
    if (!container) return;

    if (!this.topics || this.topics.length === 0) {
      container.innerHTML = `<div class="text-center py-5 text-cyan font-monospace">Accessing space science telemetry modules...</div>`;
      return;
    }

    container.innerHTML = this.topics.map(t => `
      <div class="col-md-6 mb-4">
        <div class="astro-card h-100 p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <span class="badge bg-dark border border-cyan text-cyan font-monospace px-2 py-1" style="font-size:0.75rem;">${t.category.toUpperCase()}</span>
            <span class="text-light small font-monospace"><i class="bi bi-book-half text-cyan me-1"></i>Open-Access References</span>
          </div>
          <h5 class="fw-bold text-white mb-2" style="font-family: var(--font-title); font-size:1.3rem;">${t.title}</h5>
          <p class="text-white mb-3" style="font-size:0.95rem; line-height:1.55;">${t.summary}</p>

          <div class="mb-3 p-3 rounded bg-dark border border-secondary">
            <h6 class="text-cyan small text-uppercase font-monospace mb-2 fw-bold">
              <i class="bi bi-patch-check-fill text-success me-1"></i>Real Scientific Facts
            </h6>
            <ul class="text-light ps-3 mb-0" style="font-size:0.92rem; line-height:1.55;">
              ${t.real_science_facts.map(f => `<li class="mb-1">${f}</li>`).join('')}
            </ul>
          </div>

          <div class="p-3 mb-3 rounded bg-dark border border-info" style="font-size:0.9rem; line-height:1.5;">
            <span class="text-warning fw-bold font-monospace"><i class="bi bi-controller me-1"></i>Game Model Simplification:</span>
            <span class="text-light ms-1">${t.game_model_simplification}</span>
          </div>

          <div class="border-top border-secondary pt-3 mt-auto">
            <span class="text-cyan small font-monospace d-block mb-1 fw-bold">Primary Citations & NASA References:</span>
            ${t.citations.map(c => `
              <div class="text-truncate my-1" style="font-size:0.88rem;">
                <a href="${c.url}" target="_blank" rel="noopener noreferrer" class="text-cyan text-decoration-none fw-bold">
                  <i class="bi bi-link-45deg me-1"></i>${c.title}
                </a>
                <span class="text-dim ms-1">(${c.source}, retrieved ${c.retrieved_date})</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `).join('');
  }
};
