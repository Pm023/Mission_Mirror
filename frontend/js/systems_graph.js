/**
 * Engineering Consequence Explorer (System Dependency Graph)
 * Interactive dependency graph visualization with live status and cascading consequence inspector.
 */
const SystemsGraph = {
  containerId: 'systems-graph-container',
  svgLayerId: 'graph-svg-layer',
  nodesData: [],
  edgesData: [],
  selectedNodeId: 'power_grid',

  nodeLayout: {
    power_grid: { x: 10, y: 15 },
    water_recovery: { x: 42, y: 15 },
    greenhouse: { x: 74, y: 15 },
    radiation_shield: { x: 10, y: 65 },
    hull_integrity: { x: 42, y: 65 },
    life_support: { x: 74, y: 65 },
    crew_health: { x: 44, y: 40 }
  },

  init() {
    window.addEventListener('resize', () => this.drawEdges());
  },

  async render(missionId) {
    try {
      const graphData = await API.getSystemsGraph(missionId);
      this.nodesData = graphData.nodes;
      this.edgesData = graphData.edges;
      this.drawNodes();
      this.drawEdges();
      this.inspectNode(this.selectedNodeId || (this.nodesData[0] ? this.nodesData[0].id : null));
    } catch (err) {
      console.error("Failed to render systems graph:", err);
    }
  },

  drawNodes() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    const oldNodes = container.querySelectorAll('.graph-node-card');
    oldNodes.forEach(n => n.remove());

    this.nodesData.forEach(node => {
      const pos = this.nodeLayout[node.id] || { x: 50, y: 50 };
      const card = document.createElement('div');
      card.className = `graph-node-card ${node.status} ${node.id === this.selectedNodeId ? 'selected' : ''}`;
      card.id = `node-${node.id}`;
      card.style.left = `${pos.x}%`;
      card.style.top = `${pos.y}%`;

      const statusIcon = node.status === 'healthy' 
        ? '<i class="bi bi-shield-check text-success"></i>' 
        : (node.status === 'warning' 
            ? '<i class="bi bi-exclamation-triangle-fill text-warning"></i>' 
            : '<i class="bi bi-exclamation-octagon-fill text-danger"></i>');

      card.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-1">
          <span class="badge bg-dark border border-secondary text-info font-monospace" style="font-size:0.65rem;">${node.category.toUpperCase()}</span>
          <span>${statusIcon}</span>
        </div>
        <div class="fw-bold text-white small text-truncate" style="font-family: var(--font-title); font-size: 0.95rem;">${node.name}</div>
        <div class="d-flex justify-content-between align-items-center mt-1">
          <span class="font-monospace text-cyan small fw-bold">${node.value.toFixed(1)}${node.unit}</span>
          <span class="text-dim small font-monospace" style="font-size:0.65rem;">${node.status.toUpperCase()}</span>
        </div>
      `;

      card.addEventListener('click', () => {
        this.selectedNodeId = node.id;
        document.querySelectorAll('.graph-node-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.inspectNode(node.id);
        this.highlightEdges(node.id);
        if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
      });

      container.appendChild(card);
    });
  },

  drawEdges() {
    const svg = document.getElementById(this.svgLayerId);
    const container = document.getElementById(this.containerId);
    if (!svg || !container) return;

    svg.innerHTML = `
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#00f2fe" />
        </marker>
        <marker id="arrow-warn" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#ffb300" />
        </marker>
        <marker id="arrow-crit" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#ff1744" />
        </marker>
      </defs>
    `;

    const containerRect = container.getBoundingClientRect();
    if (containerRect.width === 0) return;

    this.edgesData.forEach(edge => {
      const srcEl = document.getElementById(`node-${edge.source}`);
      const tgtEl = document.getElementById(`node-${edge.target}`);
      if (!srcEl || !tgtEl) return;

      const srcRect = srcEl.getBoundingClientRect();
      const tgtRect = tgtEl.getBoundingClientRect();

      const x1 = srcRect.left + srcRect.width / 2 - containerRect.left;
      const y1 = srcRect.top + srcRect.height / 2 - containerRect.top;
      const x2 = tgtRect.left + tgtRect.width / 2 - containerRect.left;
      const y2 = tgtRect.top + tgtRect.height / 2 - containerRect.top;

      const dx = x2 - x1;
      const dy = y2 - y1;
      const cx1 = x1 + dx * 0.4;
      const cy1 = y1;
      const cx2 = x1 + dx * 0.6;
      const cy2 = y2;

      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`);
      path.setAttribute('class', 'graph-edge-line');
      path.setAttribute('data-source', edge.source);
      path.setAttribute('data-target', edge.target);
      path.setAttribute('marker-end', 'url(#arrow)');

      svg.appendChild(path);
    });
  },

  highlightEdges(nodeId) {
    const lines = document.querySelectorAll('.graph-edge-line');
    lines.forEach(line => {
      const isConnected = line.dataset.source === nodeId || line.dataset.target === nodeId;
      if (isConnected) {
        line.style.stroke = '#00f2fe';
        line.style.strokeWidth = '3.5';
        line.style.opacity = '1';
        line.style.animation = 'energyFlow 4s linear infinite';
      } else {
        line.style.stroke = 'rgba(56, 189, 248, 0.2)';
        line.style.strokeWidth = '1.5';
        line.style.opacity = '0.35';
        line.style.animation = 'energyFlow 18s linear infinite';
      }
    });
  },

  inspectNode(nodeId) {
    const node = this.nodesData.find(n => n.id === nodeId);
    if (!node) return;

    const nameEl = document.getElementById('inspector-node-name');
    const badgeEl = document.getElementById('inspector-node-status');
    const descEl = document.getElementById('inspector-node-desc');
    const valEl = document.getElementById('inspector-node-val');
    const impactsEl = document.getElementById('inspector-downstream-impacts');
    const inputsEl = document.getElementById('inspector-depended-inputs');

    if (nameEl) nameEl.textContent = node.name;
    if (badgeEl) {
      badgeEl.className = `status-pill ${node.status}`;
      badgeEl.textContent = `${node.status.toUpperCase()} (${node.value.toFixed(1)}${node.unit})`;
    }
    if (descEl) descEl.textContent = node.description;
    if (valEl) {
      valEl.innerHTML = `
        <div class="d-flex justify-content-between small text-muted font-monospace mb-1">
          <span>OPERATIONAL CAPACITY</span>
          <span class="text-white fw-bold">${node.value.toFixed(1)}%</span>
        </div>
        <div class="astro-progress">
          <div class="astro-progress-bar ${node.status}" style="width: ${node.value}%"></div>
        </div>
      `;
    }

    if (impactsEl) {
      if (node.impacts && node.impacts.length > 0) {
        impactsEl.innerHTML = node.impacts.map(i => `
          <div class="badge bg-dark border border-secondary text-light me-1 mb-1 p-2 font-monospace">
            <i class="bi bi-arrow-down-right-circle text-info me-1"></i>${i}
          </div>
        `).join('');
      } else {
        impactsEl.innerHTML = `<span class="text-muted small">Terminal subsystem (no direct downstream hardware).</span>`;
      }
    }

    if (inputsEl) {
      if (node.depended_by && node.depended_by.length > 0) {
        inputsEl.innerHTML = node.depended_by.map(i => `
          <div class="badge bg-dark border border-secondary text-cyan me-1 mb-1 p-2 font-monospace">
            <i class="bi bi-lightning-charge text-warning me-1"></i>Supplied by: ${i}
          </div>
        `).join('');
      } else {
        inputsEl.innerHTML = `<span class="text-muted small">Primary source infrastructure (Autonomous).</span>`;
      }
    }
  }
};
