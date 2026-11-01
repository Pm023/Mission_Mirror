/**
 * Mission Mirror — Habitat Blueprint & Outpost Cutaway View
 * Renders an interactive aerospace schematic showing the 6 modules with live health glow.
 */
const HabitatView = {
  containerId: 'habitat-blueprint-svg',

  render(systems, resources) {
    const svg = document.getElementById(this.containerId);
    if (!svg) return;

    const sys = systems || {
      power_grid: 100,
      life_support: 100,
      water_recovery: 100,
      greenhouse: 100,
      radiation_shield: 100,
      hull_integrity: 100
    };
    const res = resources || { crew_health: 100 };

    const getColor = (val) => {
      if (val >= 70) return { stroke: '#00e676', fill: 'rgba(0, 230, 118, 0.12)', label: 'NOMINAL' };
      if (val >= 40) return { stroke: '#ffb300', fill: 'rgba(255, 179, 0, 0.15)', label: 'WARNING' };
      return { stroke: '#ff1744', fill: 'rgba(255, 23, 68, 0.25)', label: 'CRITICAL' };
    };

    const pwr = getColor(sys.power_grid);
    const eclss = getColor(sys.life_support);
    const h2o = getColor(sys.water_recovery);
    const bio = getColor(sys.greenhouse);
    const rad = getColor(sys.radiation_shield);
    const hull = getColor(sys.hull_integrity);
    const crew = getColor(res.crew_health);

    svg.innerHTML = `
      <defs>
        <filter id="glow-green" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <pattern id="grid-pattern" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(56, 189, 248, 0.08)" stroke-width="1" />
        </pattern>
      </defs>

      <!-- Background Grid -->
      <rect width="100%" height="100%" fill="url(#grid-pattern)" />

      <!-- Subterranean Regolith Barrier (Shielding) -->
      <path d="M 20 220 Q 350 200 680 220 L 680 250 L 20 250 Z" 
            fill="${rad.fill}" stroke="${rad.stroke}" stroke-width="2" class="module-zone" data-node="radiation_shield" />
      <text x="350" y="240" fill="${rad.stroke}" font-family="JetBrains Mono, monospace" font-size="11" text-anchor="middle" font-weight="bold">
        SUBTERRANEAN REGOLITH BUNKER (${sys.radiation_shield.toFixed(0)}%)
      </text>

      <!-- Central Habitation Core (Crew) -->
      <circle cx="350" cy="130" r="55" fill="${crew.fill}" stroke="${crew.stroke}" stroke-width="2.5" class="module-zone" data-node="crew_health" />
      <text x="350" y="125" fill="#ffffff" font-family="Rajdhani, sans-serif" font-size="13" font-weight="bold" text-anchor="middle">CREW CORE</text>
      <text x="350" y="142" fill="${crew.stroke}" font-family="JetBrains Mono, monospace" font-size="11" text-anchor="middle">
        VITALS: ${res.crew_health.toFixed(0)}%
      </text>

      <!-- Power Grid Module (West Wing) -->
      <rect x="60" y="90" width="100" height="75" rx="8" fill="${pwr.fill}" stroke="${pwr.stroke}" stroke-width="2" class="module-zone" data-node="power_grid" />
      <text x="110" y="122" fill="#ffffff" font-family="Rajdhani, sans-serif" font-size="12" font-weight="bold" text-anchor="middle">POWER GRID</text>
      <text x="110" y="140" fill="${pwr.stroke}" font-family="JetBrains Mono, monospace" font-size="11" text-anchor="middle">
        ${sys.power_grid.toFixed(0)}%
      </text>

      <!-- Life Support ECLSS (North Core) -->
      <rect x="290" y="20" width="120" height="50" rx="8" fill="${eclss.fill}" stroke="${eclss.stroke}" stroke-width="2" class="module-zone" data-node="life_support" />
      <text x="350" y="42" fill="#ffffff" font-family="Rajdhani, sans-serif" font-size="12" font-weight="bold" text-anchor="middle">ECLSS O2 / CO2</text>
      <text x="350" y="58" fill="${eclss.stroke}" font-family="JetBrains Mono, monospace" font-size="11" text-anchor="middle">
        ${sys.life_support.toFixed(0)}%
      </text>

      <!-- Water Recovery Loop (East Core) -->
      <rect x="430" y="95" width="100" height="70" rx="8" fill="${h2o.fill}" stroke="${h2o.stroke}" stroke-width="2" class="module-zone" data-node="water_recovery" />
      <text x="480" y="125" fill="#ffffff" font-family="Rajdhani, sans-serif" font-size="12" font-weight="bold" text-anchor="middle">H2O RECOVERY</text>
      <text x="480" y="143" fill="${h2o.stroke}" font-family="JetBrains Mono, monospace" font-size="11" text-anchor="middle">
        ${sys.water_recovery.toFixed(0)}%
      </text>

      <!-- Hydroponic Bio-Dome (Far East) -->
      <path d="M 555 160 A 45 45 0 0 1 645 160 Z" fill="${bio.fill}" stroke="${bio.stroke}" stroke-width="2" class="module-zone" data-node="greenhouse" />
      <text x="600" y="145" fill="#ffffff" font-family="Rajdhani, sans-serif" font-size="11" font-weight="bold" text-anchor="middle">BIO-DOME</text>
      <text x="600" y="175" fill="${bio.stroke}" font-family="JetBrains Mono, monospace" font-size="10" text-anchor="middle">
        ${sys.greenhouse.toFixed(0)}%
      </text>

      <!-- Airlock & Hull Gasket (Far West) -->
      <rect x="180" y="110" width="40" height="35" rx="4" fill="${hull.fill}" stroke="${hull.stroke}" stroke-width="2" class="module-zone" data-node="hull_integrity" />
      <text x="200" y="130" fill="#ffffff" font-family="Rajdhani, sans-serif" font-size="9" font-weight="bold" text-anchor="middle">AIRLOCK</text>

      <!-- Connecting Conduits -->
      <line x1="160" y1="128" x2="180" y2="128" stroke="${pwr.stroke}" stroke-width="2" stroke-dasharray="3,2" />
      <line x1="220" y1="128" x2="295" y2="128" stroke="${hull.stroke}" stroke-width="2" />
      <line x1="350" y1="70" x2="350" y2="75" stroke="${eclss.stroke}" stroke-width="2" />
      <line x1="405" y1="130" x2="430" y2="130" stroke="${h2o.stroke}" stroke-width="2" />
      <line x1="530" y1="130" x2="555" y2="130" stroke="${h2o.stroke}" stroke-width="2" stroke-dasharray="3,2" />
    `;

    // Click on module zones triggers graph inspector
    svg.querySelectorAll('.module-zone').forEach(el => {
      el.addEventListener('click', (e) => {
        const nodeId = e.currentTarget.dataset.node;
        if (nodeId && typeof SystemsGraph !== 'undefined') {
          SystemsGraph.selectedNodeId = nodeId;
          SystemsGraph.inspectNode(nodeId);
          SystemsGraph.highlightEdges(nodeId);
          if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
        }
      });
    });
  }
};

