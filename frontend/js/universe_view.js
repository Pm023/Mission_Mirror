/**
 * MISSION MIRROR — Interactive 3D Solar System (Three.js)
 * High-performance virtual universe with orbital paths, click raycasting,
 * educational planetary science, and seamless transition to 3D surface exploration.
 */
const UniverseView = {
  container: null,
  scene: null,
  camera: null,
  renderer: null,
  clock: null,
  animationId: null,
  isRunning: false,

  // Camera control state
  camRadius: 110,
  targetCamRadius: 110,
  camTheta: 0.6,
  targetCamTheta: 0.6,
  camPhi: 0.75,
  targetCamPhi: 0.75,
  targetLookAt: new THREE.Vector3(0, 0, 0),
  currentLookAt: new THREE.Vector3(0, 0, 0),
  isDragging: false,
  prevMouseX: 0,
  prevMouseY: 0,

  raycaster: new THREE.Raycaster(),
  mouse: new THREE.Vector2(),

  // Celestial objects
  celestials: [],
  selectedCelestial: null,

  planetData: [
    {
      id: 'sun',
      name: 'The Sun',
      radius: 6.8,
      orbit: 0,
      speed: 0,
      color: 0xffbb00,
      emissive: 0xff8800,
      type: 'G-Type Main-Sequence Star (Yellow Dwarf)',
      gravity: '274.0 m/s² (28g)',
      temp: '5,500°C (Surface) / 15,000,000°C (Core)',
      atmos: 'Hydrogen 73%, Helium 25%',
      dist: '0 AU (Center of Solar System)',
      nasaFact: 'The Sun accounts for 99.86% of the total mass of the solar system. Solar particle events (SPEs) pose the primary radiation hazard to interplanetary astronaut crews.',
      previewOnly: true,
      badge: 'STELLAR CORE'
    },
    {
      id: 'mercury',
      name: 'Mercury',
      radius: 0.9,
      orbit: 18,
      speed: 0.038,
      color: 0x9e9e9e,
      type: 'Airless Rocky Terrestrial',
      gravity: '3.70 m/s² (0.38g)',
      temp: '-180°C to +430°C',
      atmos: 'Trace exosphere (Na, Mg, O2)',
      dist: '0.39 AU (~58 million km)',
      nasaFact: 'Mercury experiences the most extreme temperature swings in the solar system due to its lack of a heat-trapping atmosphere.',
      previewOnly: true,
      badge: 'FUTURE TARGET'
    },
    {
      id: 'venus',
      name: 'Venus',
      radius: 1.8,
      orbit: 28,
      speed: 0.024,
      color: 0xe6b87d,
      type: 'Supercritical Greenhouse Terrestrial',
      gravity: '8.87 m/s² (0.91g)',
      temp: '465°C constant',
      atmos: 'CO2 96.5%, N2 3.5%, Sulfuric Acid Clouds',
      dist: '0.72 AU (~108 million km)',
      nasaFact: 'Surface pressure on Venus is 92 times Earth’s—equivalent to being 900 meters deep underwater. NASA VERITAS & DAVINCI will explore its atmosphere.',
      previewOnly: true,
      badge: 'FUTURE TARGET'
    },
    {
      id: 'earth',
      name: 'Earth',
      radius: 2.2,
      orbit: 44,
      speed: 0.016,
      color: 0x2277cc,
      type: 'Habitable Terrestrial (Home World)',
      gravity: '9.81 m/s² (1.0g)',
      temp: '15°C mean',
      atmos: 'N2 78%, O2 21%, Ar 0.9%, CO2 0.04%',
      dist: '1.00 AU (~149.6 million km)',
      nasaFact: 'Earth is our planetary baseline for Environmental Control and Life Support Systems (ECLSS), providing 101.3 kPa pressure and shielding via geomagnetic field.',
      missionReady: true,
      hasStation: true,
      badge: 'HOME ORBIT'
    },
    {
      id: 'moon',
      name: 'The Moon (Luna)',
      radius: 0.75,
      orbit: 44, // Attached to Earth in hierarchy
      parent: 'earth',
      orbitLocal: 5.2,
      speed: 0.06,
      color: 0xc8cdd0,
      type: 'Natural Satellite / Lunar South Pole',
      gravity: '1.62 m/s² (0.166g — 1/6th Earth)',
      temp: '-130°C (Night) to +120°C (Day)',
      atmos: 'Ultra-high vacuum (<10⁻¹² Pa)',
      dist: '384,400 km from Earth',
      nasaFact: 'Permanently shadowed craters at the lunar south pole hold gigatons of water ice. NASA’s Artemis program is establishing a long-term human presence here.',
      missionReady: true,
      environment: 'moon',
      badge: 'MISSION READY'
    },
    {
      id: 'station',
      name: 'International Space Station (ISS)',
      radius: 0.5,
      orbit: 44,
      parent: 'earth',
      orbitLocal: 3.4,
      speed: 0.09,
      color: 0x00f2fe,
      emissive: 0x007799,
      type: 'Low Earth Orbit (LEO) Microgravity Laboratory',
      gravity: '0.00 m/s² (Effective Free-fall Microgravity)',
      temp: 'Controlled 21°C inside habitable volume',
      atmos: 'Pressurized 101.3 kPa (78% N2, 21% O2)',
      dist: '420 km Altitude (LEO)',
      nasaFact: 'The ISS recycles over 98% of astronaut urine and sweat into drinking water through its Environmental Control and Life Support System (ECLSS).',
      missionReady: true,
      environment: 'station',
      badge: 'MISSION READY'
    },
    {
      id: 'mars',
      name: 'Mars (The Red Planet)',
      radius: 1.4,
      orbit: 64,
      speed: 0.011,
      color: 0xd95328,
      type: 'Cold Oxidized Desert Terrestrial',
      gravity: '3.72 m/s² (0.38g — 3/8th Earth)',
      temp: '-63°C average (-125°C winter pole to +20°C equator)',
      atmos: 'CO2 95.3%, N2 2.6%, Ar 1.9% (Pressure 0.6 kPa)',
      dist: '1.52 AU (~228 million km)',
      nasaFact: 'Mars features Olympus Mons (22km high volcano) and Jezero crater lake-bed deposits. MOXIE demonstrated producing pure breathable O2 from Martian atmospheric CO2.',
      missionReady: true,
      environment: 'mars',
      badge: 'MISSION READY'
    },
    {
      id: 'jupiter',
      name: 'Jupiter',
      radius: 4.8,
      orbit: 86,
      speed: 0.005,
      color: 0xd6a87c,
      type: 'Gas Giant (System Mass Center)',
      gravity: '24.79 m/s² (2.53g)',
      temp: '-110°C (Cloud tops)',
      atmos: 'Hydrogen 90%, Helium 10%',
      dist: '5.20 AU (~778 million km)',
      nasaFact: 'Jupiter’s magnetic field is 14 times stronger than Earth’s, creating extreme trapped radiation belts lethal to unshielded human astronauts in minutes.',
      previewOnly: true,
      badge: 'FUTURE TARGET'
    },
    {
      id: 'saturn',
      name: 'Saturn',
      radius: 4.0,
      orbit: 108,
      speed: 0.003,
      color: 0xe8cf9d,
      hasRings: true,
      type: 'Ringed Gas Giant',
      gravity: '10.44 m/s² (1.06g)',
      temp: '-140°C',
      atmos: 'Hydrogen 96%, Helium 3%',
      dist: '9.58 AU (~1.43 billion km)',
      nasaFact: 'Saturn’s rings extend up to 282,000 km from the planet but are mostly less than 10 meters thick, consisting of 99% pure water-ice boulders and dust.',
      previewOnly: true,
      badge: 'FUTURE TARGET'
    }
  ],

  init() {
    this.container = document.getElementById('universe-canvas-container');
    if (!this.container) return;

    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || (window.innerHeight - 80);

    // 1. Scene
    this.scene = new THREE.Scene();
    this.clock = new THREE.Clock();

    // 2. Camera
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.5, 2000);
    this.updateCameraPos();

    // 3. Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = false; // Optimize rendering performance
    this.container.innerHTML = '';
    this.container.appendChild(this.renderer.domElement);

    // 4. Lighting
    this.setupLighting();

    // 5. Starfield & Space Nebulae
    this.buildStarfield();

    // 6. Build Planets & Orbits
    this.buildSolarSystem();

    // 7. Event listeners
    this.setupControls();

    // Window resize
    window.addEventListener('resize', () => this.onResize());

    // Auto-focus Moon or Earth initially
    this.focusPlanet('earth');
  },

  setupLighting() {
    // Ambient fill for non-sunlit sides
    const ambient = new THREE.AmbientLight(0x223344, 0.6);
    this.scene.add(ambient);

    // Primary omnidirectional solar light from the Sun (0,0,0)
    const sunLight = new THREE.PointLight(0xfff6dd, 2.5, 300, 0.6);
    sunLight.position.set(0, 0, 0);
    this.scene.add(sunLight);
  },

  buildStarfield() {
    // 2500 background stars
    const starCount = 2500;
    const starGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(starCount * 3);
    const colors = new Float32Array(starCount * 3);

    for (let i = 0; i < starCount; i++) {
      const radius = 600 + Math.random() * 400;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);

      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);

      // Star hues: bluish-white, golden, cyan
      const rPick = Math.random();
      if (rPick > 0.7) {
        colors[i * 3] = 0.6; colors[i * 3 + 1] = 0.85; colors[i * 3 + 2] = 1.0; // Cyan-white
      } else if (rPick > 0.4) {
        colors[i * 3] = 1.0; colors[i * 3 + 1] = 0.95; colors[i * 3 + 2] = 0.8; // Warm golden
      } else {
        colors[i * 3] = 1.0; colors[i * 3 + 1] = 1.0; colors[i * 3 + 2] = 1.0; // Crisp white
      }
    }

    starGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    starGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const starMat = new THREE.PointsMaterial({
      size: 1.8,
      vertexColors: true,
      transparent: true,
      opacity: 0.9
    });

    const starPoints = new THREE.Points(starGeo, starMat);
    this.scene.add(starPoints);
  },

  buildSolarSystem() {
    this.celestials = [];
    const earthGroup = new THREE.Group();
    earthGroup.name = 'earthGroup';

    this.planetData.forEach(p => {
      let mesh;
      const objData = { ...p };

      if (p.id === 'sun') {
        // Glowing sun core
        const sunGeo = new THREE.SphereGeometry(p.radius, 32, 32);
        const sunMat = new THREE.MeshBasicMaterial({
          color: 0xffe066
        });
        mesh = new THREE.Mesh(sunGeo, sunMat);

        // Sun coronal halo glow
        const glowGeo = new THREE.SphereGeometry(p.radius * 1.25, 24, 24);
        const glowMat = new THREE.MeshBasicMaterial({
          color: 0xff9900,
          transparent: true,
          opacity: 0.35,
          side: THREE.BackSide
        });
        const glowMesh = new THREE.Mesh(glowGeo, glowMat);
        mesh.add(glowMesh);

        mesh.position.set(0, 0, 0);
        this.scene.add(mesh);
      }
      else if (p.parent === 'earth') {
        // Sub-orbiters (Moon or Space Station)
        const geo = new THREE.SphereGeometry(p.radius, 20, 20);
        const mat = new THREE.MeshStandardMaterial({
          color: p.color,
          roughness: 0.85,
          metalness: 0.1,
          emissive: p.emissive || 0x000000,
          emissiveIntensity: 0.5
        });
        mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(p.orbitLocal, 0, 0);

        if (p.id === 'station') {
          // Add solar wings to ISS mesh
          const wingGeo = new THREE.BoxGeometry(0.9, 0.05, 0.3);
          const wingMat = new THREE.MeshBasicMaterial({ color: 0x00f2fe });
          const wingMesh = new THREE.Mesh(wingGeo, wingMat);
          mesh.add(wingMesh);
        }

        // Add local orbit ring around Earth
        const localOrbitGeo = new THREE.BufferGeometry();
        const pts = [];
        for (let i = 0; i <= 64; i++) {
          const a = (i / 64) * Math.PI * 2;
          pts.push(new THREE.Vector3(Math.cos(a) * p.orbitLocal, 0, Math.sin(a) * p.orbitLocal));
        }
        localOrbitGeo.setFromPoints(pts);
        const localOrbitMat = new THREE.LineBasicMaterial({
          color: p.id === 'station' ? 0x00f2fe : 0x778899,
          transparent: true,
          opacity: 0.35
        });
        const localLine = new THREE.Line(localOrbitGeo, localOrbitMat);
        earthGroup.add(localLine);
        earthGroup.add(mesh);
      }
      else {
        // Standard Sun-orbiting planet
        const geo = new THREE.SphereGeometry(p.radius, 28, 28);
        const mat = new THREE.MeshStandardMaterial({
          color: p.color,
          roughness: 0.7,
          metalness: 0.1
        });
        mesh = new THREE.Mesh(geo, mat);

        if (p.hasRings) {
          // Saturn Rings
          const ringGeo = new THREE.RingGeometry(p.radius * 1.35, p.radius * 2.3, 40);
          ringGeo.rotateX(Math.PI / 2.3);
          const ringMat = new THREE.MeshBasicMaterial({
            color: 0xd6bf8e,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.75
          });
          const ringMesh = new THREE.Mesh(ringGeo, ringMat);
          mesh.add(ringMesh);
        }

        // Primary Solar Orbit Path Line
        const orbitGeo = new THREE.BufferGeometry();
        const pts = [];
        for (let i = 0; i <= 100; i++) {
          const a = (i / 100) * Math.PI * 2;
          pts.push(new THREE.Vector3(Math.cos(a) * p.orbit, 0, Math.sin(a) * p.orbit));
        }
        orbitGeo.setFromPoints(pts);
        const orbitMat = new THREE.LineBasicMaterial({
          color: 0x38bdf8,
          transparent: true,
          opacity: 0.22
        });
        const orbitLine = new THREE.Line(orbitGeo, orbitMat);
        this.scene.add(orbitLine);

        if (p.id === 'earth') {
          mesh.position.set(0, 0, 0);
          earthGroup.position.set(p.orbit, 0, 0);
          earthGroup.add(mesh);
          this.scene.add(earthGroup);
        } else {
          mesh.position.set(p.orbit, 0, 0);
          this.scene.add(mesh);
        }
      }

      mesh.userData = objData;
      objData.mesh = mesh;
      objData.angle = Math.random() * Math.PI * 2;
      this.celestials.push(objData);
    });

    this.earthGroup = earthGroup;
  },

  setupControls() {
    const canvas = this.renderer.domElement;

    // Mouse drag rotation
    canvas.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.prevMouseX = e.clientX;
      this.prevMouseY = e.clientY;
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        const deltaX = e.clientX - this.prevMouseX;
        const deltaY = e.clientY - this.prevMouseY;

        this.targetCamTheta -= deltaX * 0.006;
        this.targetCamPhi = Math.max(0.08, Math.min(Math.PI / 2.05, this.targetCamPhi + deltaY * 0.005));

        this.prevMouseX = e.clientX;
        this.prevMouseY = e.clientY;
      }
    });

    // Mouse wheel zoom
    canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY > 0 ? 1.12 : 0.88;
      this.targetCamRadius = Math.max(10, Math.min(260, this.targetCamRadius * zoomFactor));
    }, { passive: false });

    // Click selection via Raycaster
    canvas.addEventListener('click', (e) => {
      if (Math.abs(e.clientX - this.prevMouseX) > 4 || Math.abs(e.clientY - this.prevMouseY) > 4) {
        return; // Dragged, ignore as click
      }

      const rect = canvas.getBoundingClientRect();
      this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      this.raycaster.setFromCamera(this.mouse, this.camera);
      const meshes = this.celestials.map(c => c.mesh);
      const intersects = this.raycaster.intersectObjects(meshes, true);

      if (intersects.length > 0) {
        // Find topmost ancestor that has userData.id
        let curr = intersects[0].object;
        while (curr && (!curr.userData || !curr.userData.id)) {
          curr = curr.parent;
        }
        if (curr && curr.userData && curr.userData.id) {
          if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
          this.selectPlanet(curr.userData);
        }
      }
    });

    // Touch controls for mobile/tablet
    let touchDist = 0;
    canvas.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        this.isDragging = true;
        this.prevMouseX = e.touches[0].clientX;
        this.prevMouseY = e.touches[0].clientY;
      } else if (e.touches.length === 2) {
        this.isDragging = false;
        touchDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
      }
    }, { passive: true });

    canvas.addEventListener('touchmove', (e) => {
      if (e.touches.length === 1 && this.isDragging) {
        const deltaX = e.touches[0].clientX - this.prevMouseX;
        const deltaY = e.touches[0].clientY - this.prevMouseY;

        this.targetCamTheta -= deltaX * 0.007;
        this.targetCamPhi = Math.max(0.08, Math.min(Math.PI / 2.05, this.targetCamPhi + deltaY * 0.006));

        this.prevMouseX = e.touches[0].clientX;
        this.prevMouseY = e.touches[0].clientY;
      } else if (e.touches.length === 2) {
        const newDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        const zoomFactor = touchDist / newDist;
        this.targetCamRadius = Math.max(10, Math.min(260, this.targetCamRadius * zoomFactor));
        touchDist = newDist;
      }
    }, { passive: true });

    canvas.addEventListener('touchend', () => {
      this.isDragging = false;
    });
  },

  selectPlanet(pData) {
    this.selectedCelestial = pData;
    this.updateInfoPanel(pData);

    // Smooth focus camera on selected planet
    const targetPos = new THREE.Vector3();
    pData.mesh.getWorldPosition(targetPos);
    this.targetLookAt.copy(targetPos);

    // Appropriate zoom distance based on object size
    this.targetCamRadius = Math.max(pData.radius * 3.8, 14);
  },

  focusPlanet(planetId) {
    const p = this.celestials.find(c => c.id.toLowerCase() === planetId.toLowerCase());
    if (p) {
      this.selectPlanet(p);
    }
  },

  updateInfoPanel(p) {
    const card = document.getElementById('universe-planet-card');
    if (!card) return;

    card.classList.remove('d-none');

    document.getElementById('planet-name').textContent = p.name;
    document.getElementById('planet-type').textContent = p.type;
    document.getElementById('planet-gravity').textContent = p.gravity;
    document.getElementById('planet-temp').textContent = p.temp;
    document.getElementById('planet-atmos').textContent = p.atmos;
    document.getElementById('planet-dist').textContent = p.dist;
    document.getElementById('planet-fact').textContent = p.nasaFact;

    const badgeEl = document.getElementById('planet-badge');
    if (badgeEl) {
      badgeEl.textContent = p.badge;
      badgeEl.className = p.missionReady ? 'badge bg-success-subtle text-success border border-success' : 'badge bg-dark border border-secondary text-secondary';
    }

    // Action button states
    const actionContainer = document.getElementById('planet-action-buttons');
    if (!actionContainer) return;

    if (p.environment) {
      actionContainer.innerHTML = `
        <div class="d-grid gap-2 mt-3">
          <button class="btn btn-astro-primary btn-sm py-2" id="btn-explore-surface-3d">
            <i class="bi bi-person-walking me-1"></i>Explore 3D Surface (${p.name})
          </button>
          <button class="btn btn-outline-cyan btn-sm" id="btn-deploy-mission-here">
            <i class="bi bi-rocket-takeoff me-1"></i>Begin Flight Mission Here
          </button>
        </div>
      `;

      document.getElementById('btn-explore-surface-3d').addEventListener('click', () => {
        if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();
        ExplorationHUD.startExploration(p.environment);
      });

      document.getElementById('btn-deploy-mission-here').addEventListener('click', () => {
        if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
        AppState.setView('briefing');
        // Pre-select destination in briefing view
        const destCard = document.querySelector(`.dest-card[data-destination="${p.environment}"]`);
        if (destCard) destCard.click();
      });
    } else if (p.hasStation) {
      actionContainer.innerHTML = `
        <div class="d-grid gap-2 mt-3">
          <button class="btn btn-astro-primary btn-sm py-2" id="btn-board-iss">
            <i class="bi bi-hdd-network me-1"></i>Board Space Station 3D
          </button>
          <button class="btn btn-outline-secondary btn-sm" id="btn-inspect-earth">
            <i class="bi bi-globe-americas me-1"></i>View Earth System Overview
          </button>
        </div>
      `;

      document.getElementById('btn-board-iss').addEventListener('click', () => {
        if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();
        ExplorationHUD.startExploration('station');
      });

      document.getElementById('btn-inspect-earth').addEventListener('click', () => {
        AppState.setView('science');
      });
    } else {
      actionContainer.innerHTML = `
        <div class="alert alert-dark border border-secondary text-dim small mt-3 p-2 text-center">
          <i class="bi bi-lock-fill me-1"></i>Surface exploration unavailable. Automated orbiter mission planned for Artemis V+ deep-space deployment.
        </div>
      `;
    }
  },

  updateCameraPos() {
    // Spherical coordinates
    const x = this.targetLookAt.x + this.camRadius * Math.sin(this.camPhi) * Math.sin(this.camTheta);
    const y = this.targetLookAt.y + this.camRadius * Math.cos(this.camPhi);
    const z = this.targetLookAt.z + this.camRadius * Math.sin(this.camPhi) * Math.cos(this.camTheta);

    this.camera.position.set(x, y, z);
    this.camera.lookAt(this.currentLookAt);
  },

  animate() {
    if (!this.isRunning) return;

    this.animationId = requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();

    // 1. Smooth camera interpolation
    this.camRadius += (this.targetCamRadius - this.camRadius) * 0.08;
    this.camTheta += (this.targetCamTheta - this.camTheta) * 0.08;
    this.camPhi += (this.targetCamPhi - this.camPhi) * 0.08;
    this.currentLookAt.lerp(this.targetLookAt, 0.08);

    this.updateCameraPos();

    // 2. Celestial orbits & rotations
    this.celestials.forEach(c => {
      // Axial rotation
      if (c.mesh) {
        c.mesh.rotation.y += delta * 0.4;
      }

      // Orbital movement
      if (c.speed > 0 && c.orbit > 0 && !c.parent) {
        c.angle += c.speed * delta * 0.6;
        if (c.id === 'earth') {
          this.earthGroup.position.x = Math.cos(c.angle) * c.orbit;
          this.earthGroup.position.z = Math.sin(c.angle) * c.orbit;
        } else {
          c.mesh.position.x = Math.cos(c.angle) * c.orbit;
          c.mesh.position.z = Math.sin(c.angle) * c.orbit;
        }
      } else if (c.parent === 'earth' && c.speed > 0) {
        c.angle += c.speed * delta * 0.8;
        c.mesh.position.x = Math.cos(c.angle) * c.orbitLocal;
        c.mesh.position.z = Math.sin(c.angle) * c.orbitLocal;
      }
    });

    // If tracking selected planet, follow its world position smoothly
    if (this.selectedCelestial && this.selectedCelestial.mesh) {
      const worldPos = new THREE.Vector3();
      this.selectedCelestial.mesh.getWorldPosition(worldPos);
      this.targetLookAt.lerp(worldPos, 0.05);
    }

    this.renderer.render(this.scene, this.camera);
  },

  start() {
    if (!this.renderer) {
      this.init();
    }
    if (!this.isRunning) {
      this.isRunning = true;
      this.clock.start();
      this.animate();
    }
    this.onResize();
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

