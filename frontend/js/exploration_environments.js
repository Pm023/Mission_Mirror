/**
 * MISSION MIRROR — 3D Exploration Environments
 * Generates three scientifically authentic 3D environments:
 * 1. MOON (Shackleton Crater rim, Earth in sky, lunar hab, solar arrays, rover, ISRU drill)
 * 2. MARS (Jezero Crater, salmon sky, Ares habitat, 6-wheel rover, core drill, weather mast)
 * 3. STATION (Pressurized orbital module, Cupola observation bay, giant Earth below, ECLSS racks)
 */
const ExplorationEnvironments = {
  currentMeshes: [],
  waypoints: [],

  cleanup(scene) {
    this.currentMeshes.forEach(m => {
      scene.remove(m);
      if (m.geometry) m.geometry.dispose();
      if (m.material) {
        if (Array.isArray(m.material)) m.material.forEach(mat => mat.dispose());
        else m.material.dispose();
      }
    });
    this.currentMeshes = [];
    this.waypoints = [];
    scene.fog = null;
  },

  build(environment, scene, getTerrainHeightCallback) {
    this.cleanup(scene);
    const env = environment.toLowerCase();

    if (env === 'moon') {
      return this.buildMoon(scene);
    } else if (env === 'mars') {
      return this.buildMars(scene);
    } else if (env === 'station') {
      return this.buildStation(scene);
    }
    return this.buildMoon(scene);
  },

  // --------------------------------------------------------------------------
  // 1. MOON ENVIRONMENT
  // --------------------------------------------------------------------------
  buildMoon(scene) {
    const meshes = [];

    // Terrain height function for Moon (craters and gentle undulations)
    const getTerrainHeight = (x, z) => {
      // Shackleton crater depression near (12, 28)
      const dCrater = Math.hypot(x - 12, z - 28);
      let craterDepth = 0;
      if (dCrater < 16) {
        craterDepth = -Math.cos((dCrater / 16) * (Math.PI / 2)) * 3.2;
      }
      const rolling = Math.sin(x * 0.08) * Math.cos(z * 0.08) * 0.9;
      return craterDepth + rolling;
    };

    // Lunar regolith terrain
    const terrainGeo = new THREE.PlaneGeometry(120, 120, 64, 64);
    terrainGeo.rotateX(-Math.PI / 2);
    const posAttr = terrainGeo.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
      const vx = posAttr.getX(i);
      const vz = posAttr.getZ(i);
      posAttr.setY(i, getTerrainHeight(vx, vz));
    }
    terrainGeo.computeVertexNormals();

    const terrainMat = new THREE.MeshStandardMaterial({
      color: 0x828892,
      roughness: 0.95,
      metalness: 0.05
    });
    const terrain = new THREE.Mesh(terrainGeo, terrainMat);
    scene.add(terrain);
    meshes.push(terrain);

    // Deep space black sky with stars
    scene.background = new THREE.Color(0x020409);

    // Earth in the Lunar Sky!
    const earthGroup = new THREE.Group();
    earthGroup.position.set(40, 50, -85);

    const earthGeo = new THREE.SphereGeometry(14, 32, 32);
    const earthMat = new THREE.MeshStandardMaterial({
      color: 0x1d65af,
      roughness: 0.6,
      metalness: 0.1
    });
    const earthMesh = new THREE.Mesh(earthGeo, earthMat);
    earthGroup.add(earthMesh);

    // Earth cloud layer
    const cloudGeo = new THREE.SphereGeometry(14.2, 32, 32);
    const cloudMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.45,
      roughness: 1.0
    });
    const cloudMesh = new THREE.Mesh(cloudGeo, cloudMat);
    earthGroup.add(cloudMesh);

    // Earth atmospheric blue rim glow
    const glowGeo = new THREE.SphereGeometry(15.2, 24, 24);
    const glowMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.25,
      side: THREE.BackSide
    });
    const glowMesh = new THREE.Mesh(glowGeo, glowMat);
    earthGroup.add(glowMesh);

    scene.add(earthGroup);
    meshes.push(earthGroup);

    // Harsh directional solar light (high contrast, no atmospheric diffusion)
    const sunLight = new THREE.DirectionalLight(0xfff5e6, 2.4);
    sunLight.position.set(50, 45, 30);
    scene.add(sunLight);
    meshes.push(sunLight);

    // Soft bluish earth-shine ambient fill
    const earthShine = new THREE.DirectionalLight(0x38bdf8, 0.45);
    earthShine.position.set(-40, 20, 50);
    scene.add(earthShine);
    meshes.push(earthShine);

    const ambient = new THREE.AmbientLight(0x1a2233, 0.5);
    scene.add(ambient);
    meshes.push(ambient);

    // PROPS: Lunar Habitat Dome at (0, y, -6)
    const habGroup = new THREE.Group();
    habGroup.position.set(0, getTerrainHeight(0, -6), -6);

    const domeGeo = new THREE.SphereGeometry(5.5, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2);
    const domeMat = new THREE.MeshStandardMaterial({ color: 0xdde3ea, roughness: 0.4, metalness: 0.3 });
    const dome = new THREE.Mesh(domeGeo, domeMat);
    habGroup.add(dome);

    // Airlock tunnel
    const airlockGeo = new THREE.CylinderGeometry(1.4, 1.4, 4.0, 16);
    airlockGeo.rotateX(Math.PI / 2);
    const airlockMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.5, metalness: 0.4 });
    const airlock = new THREE.Mesh(airlockGeo, airlockMat);
    airlock.position.set(0, 1.4, 4.5);
    habGroup.add(airlock);

    // Comms Dish
    const dishGeo = new THREE.CylinderGeometry(1.6, 0.2, 0.6, 16);
    dishGeo.rotateX(Math.PI / 4);
    const dishMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const dish = new THREE.Mesh(dishGeo, dishMat);
    dish.position.set(2.5, 6.2, 0);
    habGroup.add(dish);

    scene.add(habGroup);
    meshes.push(habGroup);

    // PROPS: Solar Array Alpha at (24, y, -22)
    const solarGroup = new THREE.Group();
    solarGroup.position.set(24, getTerrainHeight(24, -22), -22);

    for (let i = -1; i <= 1; i += 2) {
      const mastGeo = new THREE.CylinderGeometry(0.2, 0.25, 6.0, 8);
      const mastMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.8 });
      const mast = new THREE.Mesh(mastGeo, mastMat);
      mast.position.set(i * 3.5, 3.0, 0);
      solarGroup.add(mast);

      // Panel wing
      const panelGeo = new THREE.BoxGeometry(4.2, 0.1, 2.5);
      panelGeo.rotateX(-0.4);
      const panelMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, metalness: 0.9, roughness: 0.2 });
      const panel = new THREE.Mesh(panelGeo, panelMat);
      panel.position.set(i * 3.5, 6.0, 0);
      solarGroup.add(panel);
    }
    scene.add(solarGroup);
    meshes.push(solarGroup);

    // PROPS: Power Conduit Junction Hub at (-16, y, -12)
    const powerJunction = new THREE.Group();
    powerJunction.position.set(-16, getTerrainHeight(-16, -12), -12);
    const hubBoxGeo = new THREE.BoxGeometry(2.4, 1.8, 2.4);
    const hubBoxMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.5 });
    const hubBox = new THREE.Mesh(hubBoxGeo, hubBoxMat);
    hubBox.position.y = 0.9;
    powerJunction.add(hubBox);

    // Glowing conduit rings
    const ringGeo = new THREE.TorusGeometry(1.4, 0.08, 8, 24);
    ringGeo.rotateX(Math.PI / 2);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f2fe });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.position.y = 1.0;
    powerJunction.add(ringMesh);

    scene.add(powerJunction);
    meshes.push(powerJunction);

    // PROPS: Cold Trap Sampling Site Drill Rig at (12, y, 28)
    const drillGroup = new THREE.Group();
    drillGroup.position.set(12, getTerrainHeight(12, 28), 28);
    const tripodGeo = new THREE.CylinderGeometry(0.1, 0.15, 4.5, 6);
    const tripodMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.6 });
    for (let a = 0; a < 3; a++) {
      const ang = (a / 3) * Math.PI * 2;
      const leg = new THREE.Mesh(tripodGeo, tripodMat);
      leg.position.set(Math.cos(ang) * 1.2, 2.0, Math.sin(ang) * 1.2);
      leg.rotation.z = Math.cos(ang) * 0.2;
      leg.rotation.x = Math.sin(ang) * 0.2;
      drillGroup.add(leg);
    }
    // Drill cylinder
    const drillCylGeo = new THREE.CylinderGeometry(0.2, 0.2, 3.8, 12);
    const drillCylMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9 });
    const drillCyl = new THREE.Mesh(drillCylGeo, drillCylMat);
    drillCyl.position.y = 1.9;
    drillGroup.add(drillCyl);

    scene.add(drillGroup);
    meshes.push(drillGroup);

    // PROPS: Lunar Rover Vehicle at (-8, y, 14)
    const rover = this.buildRover(0xcccccc);
    rover.position.set(-8, getTerrainHeight(-8, 14), 14);
    rover.rotation.y = 0.7;
    scene.add(rover);
    meshes.push(rover);

    // Scattered boulders
    this.spawnBoulders(scene, meshes, getTerrainHeight, 0x64748b, 25);

    this.currentMeshes = meshes;
    return { getTerrainHeight };
  },

  // --------------------------------------------------------------------------
  // 2. MARS ENVIRONMENT
  // --------------------------------------------------------------------------
  buildMars(scene) {
    const meshes = [];

    const getTerrainHeight = (x, z) => {
      // Martian dunes and rocky ridges
      const ridge = Math.sin(x * 0.05 + z * 0.04) * 1.4;
      const dunes = Math.sin(x * 0.12) * Math.cos(z * 0.1) * 0.7;
      return ridge + dunes;
    };

    // Red terrain
    const terrainGeo = new THREE.PlaneGeometry(120, 120, 64, 64);
    terrainGeo.rotateX(-Math.PI / 2);
    const posAttr = terrainGeo.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
      const vx = posAttr.getX(i);
      const vz = posAttr.getZ(i);
      posAttr.setY(i, getTerrainHeight(vx, vz));
    }
    terrainGeo.computeVertexNormals();

    const terrainMat = new THREE.MeshStandardMaterial({
      color: 0xb94c25,
      roughness: 0.9,
      metalness: 0.05
    });
    const terrain = new THREE.Mesh(terrainGeo, terrainMat);
    scene.add(terrain);
    meshes.push(terrain);

    // Salmon-pink Martian sky & atmospheric haze
    scene.background = new THREE.Color(0xd27552);
    scene.fog = new THREE.FogExp2(0xd27552, 0.009);

    // Warm diffused sunlight
    const sunLight = new THREE.DirectionalLight(0xffedd5, 1.9);
    sunLight.position.set(40, 35, 25);
    scene.add(sunLight);
    meshes.push(sunLight);

    const ambient = new THREE.AmbientLight(0x7c2d12, 0.65);
    scene.add(ambient);
    meshes.push(ambient);

    // PROPS: Ares Habitat Cylinders at (0, y, -8)
    const habGroup = new THREE.Group();
    habGroup.position.set(0, getTerrainHeight(0, -8), -8);

    const habCylGeo = new THREE.CylinderGeometry(4.0, 4.0, 5.0, 24);
    const habCylMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, metalness: 0.4, roughness: 0.4 });
    const habCyl = new THREE.Mesh(habCylGeo, habCylMat);
    habCyl.position.y = 2.5;
    habGroup.add(habCyl);

    // Inflatable greenhouse dome beside hab
    const ghGeo = new THREE.SphereGeometry(3.2, 20, 16, 0, Math.PI * 2, 0, Math.PI / 2);
    const ghMat = new THREE.MeshStandardMaterial({ color: 0x86efac, transparent: true, opacity: 0.65, roughness: 0.2 });
    const ghMesh = new THREE.Mesh(ghGeo, ghMat);
    ghMesh.position.set(6.5, 0, 0);
    habGroup.add(ghMesh);

    scene.add(habGroup);
    meshes.push(habGroup);

    // PROPS: Ares Exploration Rover at (-22, y, 18)
    const rover = this.buildRover(0xd97706, true);
    rover.position.set(-22, getTerrainHeight(-22, 18), 18);
    rover.rotation.y = -0.5;
    scene.add(rover);
    meshes.push(rover);

    // PROPS: Sample Cache Core Drill Rig at (16, y, 24)
    const drillGroup = new THREE.Group();
    drillGroup.position.set(16, getTerrainHeight(16, 24), 24);
    const mastGeo = new THREE.BoxGeometry(0.8, 5.0, 0.8);
    const mastMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.7 });
    const mast = new THREE.Mesh(mastGeo, mastMat);
    mast.position.y = 2.5;
    drillGroup.add(mast);

    // Sample carousel
    const carGeo = new THREE.CylinderGeometry(1.2, 1.2, 0.4, 16);
    const carMat = new THREE.MeshStandardMaterial({ color: 0x0284c7 });
    const carMesh = new THREE.Mesh(carGeo, carMat);
    carMesh.position.y = 1.0;
    drillGroup.add(carMesh);

    scene.add(drillGroup);
    meshes.push(drillGroup);

    // PROPS: Weather Station & Dust Storm Anemometer at (-14, y, -25)
    const weatherGroup = new THREE.Group();
    weatherGroup.position.set(-14, getTerrainHeight(-14, -25), -25);
    const wMastGeo = new THREE.CylinderGeometry(0.12, 0.18, 7.0, 8);
    const wMastMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.8 });
    const wMast = new THREE.Mesh(wMastGeo, wMastMat);
    wMast.position.y = 3.5;
    weatherGroup.add(wMast);

    // Spinning anemometer cross
    const crossGeo = new THREE.BoxGeometry(1.8, 0.08, 0.08);
    const crossMat = new THREE.MeshBasicMaterial({ color: 0xff1744 });
    const crossMesh = new THREE.Mesh(crossGeo, crossMat);
    crossMesh.position.y = 6.8;
    weatherGroup.add(crossMesh);

    scene.add(weatherGroup);
    meshes.push(weatherGroup);

    // Martian dark basalt rocks
    this.spawnBoulders(scene, meshes, getTerrainHeight, 0x451a03, 30);

    this.currentMeshes = meshes;
    return { getTerrainHeight };
  },

  // --------------------------------------------------------------------------
  // 3. SPACE STATION ENVIRONMENT (Orbital Lab & Panoramic Cupola)
  // --------------------------------------------------------------------------
  buildStation(scene) {
    const meshes = [];

    // Flat interior floor
    const getTerrainHeight = (x, z) => 0;

    // Deep space dark void
    scene.background = new THREE.Color(0x01030a);

    // GIGANTIC ROTATING BLUE EARTH VISIBLE BELOW!
    const earthGroup = new THREE.Group();
    earthGroup.position.set(0, -180, 0); // Positioned directly below station

    const earthGeo = new THREE.SphereGeometry(170, 48, 48);
    const earthMat = new THREE.MeshStandardMaterial({
      color: 0x1e5ba3,
      roughness: 0.7,
      metalness: 0.1
    });
    const earthMesh = new THREE.Mesh(earthGeo, earthMat);
    earthGroup.add(earthMesh);

    // Earth atmospheric limb glow
    const atmGeo = new THREE.SphereGeometry(175, 32, 32);
    const atmMat = new THREE.MeshBasicMaterial({
      color: 0x00f2fe,
      transparent: true,
      opacity: 0.28,
      side: THREE.BackSide
    });
    const atmMesh = new THREE.Mesh(atmGeo, atmMat);
    earthGroup.add(atmMesh);

    scene.add(earthGroup);
    meshes.push(earthGroup);

    // Cool fluorescent module lighting
    const interiorLight1 = new THREE.PointLight(0xe0f2fe, 1.8, 35);
    interiorLight1.position.set(0, 4.0, 0);
    scene.add(interiorLight1);
    meshes.push(interiorLight1);

    const interiorLight2 = new THREE.PointLight(0x00f2fe, 1.2, 30);
    interiorLight2.position.set(0, 3.5, 15);
    scene.add(interiorLight2);
    meshes.push(interiorLight2);

    const earthLight = new THREE.DirectionalLight(0x38bdf8, 0.8);
    earthLight.position.set(0, -10, 0);
    scene.add(earthLight);
    meshes.push(earthLight);

    // Station Module Deck & Enclosure (High-tech white panels)
    const floorGeo = new THREE.PlaneGeometry(36, 48);
    floorGeo.rotateX(-Math.PI / 2);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x334155,
      metalness: 0.6,
      roughness: 0.3
    });
    const floorMesh = new THREE.Mesh(floorGeo, floorMat);
    scene.add(floorMesh);
    meshes.push(floorMesh);

    // Observation Deck Rails & Structure
    const railMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.8 });
    const deckRails = new THREE.BoxGeometry(36, 1.2, 0.4);
    const railNorth = new THREE.Mesh(deckRails, railMat);
    railNorth.position.set(0, 0.6, -24);
    scene.add(railNorth);
    meshes.push(railNorth);

    // PANORAMIC CUPOLA OBSERVATION BAY at (0, 0, 20)
    const cupolaGroup = new THREE.Group();
    cupolaGroup.position.set(0, 0, 20);

    // Glass viewport floor looking straight down at Earth
    const glassGeo = new THREE.CylinderGeometry(5.0, 5.0, 0.2, 24);
    const glassMat = new THREE.MeshPhysicalMaterial({
      color: 0x00f2fe,
      transparent: true,
      opacity: 0.35,
      roughness: 0.1,
      metalness: 0.1,
      transmission: 0.8
    });
    const glassPort = new THREE.Mesh(glassGeo, glassMat);
    glassPort.position.y = 0.1;
    cupolaGroup.add(glassPort);

    // Cupola arch ring
    const archGeo = new THREE.TorusGeometry(5.0, 0.3, 12, 32);
    archGeo.rotateX(Math.PI / 2);
    const archMesh = new THREE.Mesh(archGeo, railMat);
    archMesh.position.y = 0.2;
    cupolaGroup.add(archMesh);

    scene.add(cupolaGroup);
    meshes.push(cupolaGroup);

    // PROPS: ECLSS Carbon Dioxide Removal Assembly (CDRA) at (-12, 0, 8)
    const eclssRack = new THREE.Group();
    eclssRack.position.set(-12, 0, 8);
    const rackBoxGeo = new THREE.BoxGeometry(2.8, 3.8, 1.4);
    const rackBoxMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.5 });
    const rackBox = new THREE.Mesh(rackBoxGeo, rackBoxMat);
    rackBox.position.y = 1.9;
    eclssRack.add(rackBox);

    // Zeolite canister cylinders
    const canGeo = new THREE.CylinderGeometry(0.4, 0.4, 3.0, 16);
    const canMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, metalness: 0.8 });
    const can1 = new THREE.Mesh(canGeo, canMat);
    can1.position.set(-0.6, 1.8, 0.8);
    const can2 = new THREE.Mesh(canGeo, canMat);
    can2.position.set(0.6, 1.8, 0.8);
    eclssRack.add(can1);
    eclssRack.add(can2);

    scene.add(eclssRack);
    meshes.push(eclssRack);

    // PROPS: Nitrogen High-Pressure Gas Manifold at (14, 0, -10)
    const n2Manifold = new THREE.Group();
    n2Manifold.position.set(14, 0, -10);
    const tankGeo = new THREE.CylinderGeometry(0.65, 0.65, 3.2, 16);
    const tankMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.6 });
    for (let i = -1; i <= 1; i++) {
      const tank = new THREE.Mesh(tankGeo, tankMat);
      tank.position.set(i * 1.5, 1.6, 0);
      n2Manifold.add(tank);
    }
    scene.add(n2Manifold);
    meshes.push(n2Manifold);

    this.currentMeshes = meshes;
    return { getTerrainHeight };
  },

  // Helper: Build Procedural Rover Mesh
  buildRover(bodyColor, isMarsAres = false) {
    const roverGroup = new THREE.Group();

    // Chassis body
    const bodyGeo = new THREE.BoxGeometry(2.6, 0.9, 4.0);
    const bodyMat = new THREE.MeshStandardMaterial({ color: bodyColor, metalness: 0.5, roughness: 0.4 });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 1.2;
    roverGroup.add(body);

    // 4 or 6 wheels
    const wheelCount = isMarsAres ? 6 : 4;
    const wheelGeo = new THREE.CylinderGeometry(0.5, 0.5, 0.4, 16);
    wheelGeo.rotateZ(Math.PI / 2);
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.9 });

    const zOffsets = isMarsAres ? [-1.5, 0, 1.5] : [-1.3, 1.3];
    zOffsets.forEach(z => {
      const wL = new THREE.Mesh(wheelGeo, wheelMat);
      wL.position.set(-1.6, 0.5, z);
      const wR = new THREE.Mesh(wheelGeo, wheelMat);
      wR.position.set(1.6, 0.5, z);
      roverGroup.add(wL);
      roverGroup.add(wR);
    });

    // Mast camera
    const mastGeo = new THREE.CylinderGeometry(0.08, 0.08, 1.6, 8);
    const mastMat = new THREE.MeshStandardMaterial({ color: 0x64748b });
    const mast = new THREE.Mesh(mastGeo, mastMat);
    mast.position.set(0.6, 2.3, 1.4);
    roverGroup.add(mast);

    const camHeadGeo = new THREE.BoxGeometry(0.5, 0.25, 0.35);
    const camHeadMat = new THREE.MeshStandardMaterial({ color: 0x0f172a });
    const camHead = new THREE.Mesh(camHeadGeo, camHeadMat);
    camHead.position.set(0.6, 3.1, 1.4);
    roverGroup.add(camHead);

    return roverGroup;
  },

  // Helper: Scatter boulders across terrain
  spawnBoulders(scene, meshes, getTerrainHeight, color, count) {
    const rockGeo = new THREE.DodecahedronGeometry(1.0, 1);
    const rockMat = new THREE.MeshStandardMaterial({ color, roughness: 0.9, metalness: 0.1 });

    for (let i = 0; i < count; i++) {
      const x = (Math.random() - 0.5) * 90;
      const z = (Math.random() - 0.5) * 90;
      // Don't spawn rocks directly on spawn point (0,0) or habitat
      if (Math.hypot(x, z) < 8) continue;

      const scale = 0.5 + Math.random() * 1.5;
      const rock = new THREE.Mesh(rockGeo, rockMat);
      rock.scale.set(scale, scale * (0.6 + Math.random() * 0.5), scale);
      rock.position.set(x, getTerrainHeight(x, z) + (scale * 0.3), z);
      rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);

      scene.add(rock);
      meshes.push(rock);
    }
  },

  // --------------------------------------------------------------------------
  // Glowing Waypoint Beacons for 3D Objectives
  // --------------------------------------------------------------------------
  createWaypointMarker(scene, objective, terrainHeight) {
    const group = new THREE.Group();
    const x = objective.coordinates.x;
    const z = objective.coordinates.z;
    const y = terrainHeight(x, z);

    group.position.set(x, y, z);

    const beaconColor = objective.completed ? 0x00e676 : 0x00f2fe;

    // 1. Floating rotating diamond
    const diamondGeo = new THREE.OctahedronGeometry(0.9, 0);
    const diamondMat = new THREE.MeshBasicMaterial({
      color: beaconColor,
      wireframe: true
    });
    const diamond = new THREE.Mesh(diamondGeo, diamondMat);
    diamond.position.y = 2.4;
    group.add(diamond);

    // Inner core
    const coreGeo = new THREE.OctahedronGeometry(0.5, 0);
    const coreMat = new THREE.MeshBasicMaterial({ color: beaconColor });
    const core = new THREE.Mesh(coreGeo, coreMat);
    core.position.y = 2.4;
    group.add(core);

    // 2. Vertical Light Pillar / Beam
    const beamGeo = new THREE.CylinderGeometry(0.12, 0.4, 25, 8);
    beamGeo.translate(0, 12.5, 0);
    const beamMat = new THREE.MeshBasicMaterial({
      color: beaconColor,
      transparent: true,
      opacity: 0.28
    });
    const beam = new THREE.Mesh(beamGeo, beamMat);
    group.add(beam);

    // 3. Ground target pulsing ring
    const groundRingGeo = new THREE.RingGeometry(1.2, 1.5, 24);
    groundRingGeo.rotateX(-Math.PI / 2);
    const groundRingMat = new THREE.MeshBasicMaterial({
      color: beaconColor,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.6
    });
    const groundRing = new THREE.Mesh(groundRingGeo, groundRingMat);
    groundRing.position.y = 0.08;
    group.add(groundRing);

    group.userData = {
      objective,
      diamond,
      core,
      beam,
      groundRing,
      update(delta, time) {
        diamond.rotation.y += delta * 1.5;
        diamond.rotation.x += delta * 0.8;
        diamond.position.y = 2.4 + Math.sin(time * 3.0) * 0.3;
        core.position.y = diamond.position.y;
        groundRing.scale.setScalar(1.0 + Math.sin(time * 4.0) * 0.15);
      }
    };

    scene.add(group);
    this.currentMeshes.push(group);
    this.waypoints.push(group);

    return group;
  }
};

