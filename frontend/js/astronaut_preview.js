/**
 * MISSION MIRROR — 3D Astronaut Holographic Preview
 * Renders an interactive, photorealistic Apollo/Artemis NASA Astronaut
 * on the Landing Page Hero deck with authentic EMU suit, gold visor reflections,
 * holographic pedestal rings, and interactive 360° inspection.
 */
const AstronautPreview = {
  container: null,
  scene: null,
  camera: null,
  renderer: null,
  astronautMesh: null,
  clock: null,
  animationId: null,
  isDragging: false,
  prevMouseX: 0,
  targetRotationY: 0.15, // Forward-facing hero angle towards viewer
  currentRotationY: 0.15,

  init() {
    this.container = document.getElementById('hero-astronaut-canvas-container');
    if (!this.container) return;

    const width = this.container.clientWidth || 440;
    const height = this.container.clientHeight || 440;

    // 1. Scene & Clock
    this.scene = new THREE.Scene();
    this.clock = new THREE.Clock();

    // 2. Camera - Positioned to frame entire astronaut with generous top & bottom breathing room
    this.camera = new THREE.PerspectiveCamera(36, width / height, 0.1, 100);
    this.camera.position.set(0, 1.05, 4.4);
    this.camera.lookAt(0, 0.95, 0);

    // 3. WebGL Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    if (this.renderer.outputEncoding !== undefined) {
      this.renderer.outputEncoding = THREE.sRGBEncoding;
    }
    this.container.innerHTML = '';
    this.container.appendChild(this.renderer.domElement);

    // 4. Studio Cinematic Aerospace Lighting
    this.setupLighting();

    // 5. Holographic Pedestal
    this.buildHolographicPedestal();

    // 6. Load Astronaut Model (Procedural base + Astronaut.glb)
    this.loadAstronautModel();

    // 7. Interactive Controls
    this.setupControls();

    // 8. Start Animation Loop
    this.animate();

    window.addEventListener('resize', () => this.onResize());
  },

  setupLighting() {
    // Soft ambient space illumination
    const ambient = new THREE.AmbientLight(0x243247, 1.6);
    this.scene.add(ambient);

    // Primary Solar Key Light (illuminates front of suit and visor)
    const keyLight = new THREE.DirectionalLight(0xfff5e6, 3.2);
    keyLight.position.set(2.5, 4.0, 4.5);
    this.scene.add(keyLight);

    // Cyan Laser Rim Light (creates sharp aerospace rim outline)
    const rimLight = new THREE.DirectionalLight(0x00f2fe, 3.5);
    rimLight.position.set(-3.5, 2.5, -2.5);
    this.scene.add(rimLight);

    // Earthshine Blue Fill Light from bottom
    const earthLight = new THREE.DirectionalLight(0x38bdf8, 1.6);
    earthLight.position.set(0, -2.0, 2.0);
    this.scene.add(earthLight);
  },

  buildHolographicPedestal() {
    const group = new THREE.Group();

    // Primary glowing laser ring
    const ringGeo1 = new THREE.RingGeometry(1.0, 1.06, 64);
    ringGeo1.rotateX(-Math.PI / 2);
    const ringMat1 = new THREE.MeshBasicMaterial({ color: 0x00f2fe, side: THREE.DoubleSide, transparent: true, opacity: 0.85 });
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    ring1.position.y = 0.05;
    group.add(ring1);

    // Secondary pulsing ring
    const ringGeo2 = new THREE.RingGeometry(1.22, 1.26, 64);
    ringGeo2.rotateX(-Math.PI / 2);
    const ringMat2 = new THREE.MeshBasicMaterial({ color: 0x38bdf8, side: THREE.DoubleSide, transparent: true, opacity: 0.4 });
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.position.y = 0.05;
    group.add(ring2);

    // Center emitter disc
    const discGeo = new THREE.CircleGeometry(0.85, 32);
    discGeo.rotateX(-Math.PI / 2);
    const discMat = new THREE.MeshBasicMaterial({ color: 0x071530, transparent: true, opacity: 0.7 });
    const disc = new THREE.Mesh(discGeo, discMat);
    disc.position.y = 0.03;
    group.add(disc);

    this.pedestal = group;
    this.scene.add(group);
  },

  loadAstronautModel() {
    // 1. Build high-fidelity procedural astronaut immediately
    this.astronautMesh = this.buildMasterpieceAstronaut();
    this.scene.add(this.astronautMesh);

    // 2. Load authentic NASA Astronaut.glb
    if (typeof THREE.GLTFLoader !== 'undefined') {
      const loader = new THREE.GLTFLoader();
      loader.load(
        'assets/models/Astronaut.glb',
        (gltf) => {
          const model = gltf.scene;

          // Compute bounding box
          const box = new THREE.Box3().setFromObject(model);
          const size = new THREE.Vector3();
          box.getSize(size);
          const center = new THREE.Vector3();
          box.getCenter(center);

          // Center precisely
          model.position.x = -center.x;
          model.position.y = -box.min.y;
          model.position.z = -center.z;

          // Scale to ~1.62m to fit perfectly in canvas with margins
          const scale = 1.65 / size.y;
          model.scale.set(scale, scale, scale);

          // Rotate to face camera forward (Astronaut.glb faces -Z, so rotate Math.PI)
          model.rotation.y = Math.PI + 0.15;

          // Enhance shading & materials
          model.traverse((child) => {
            if (child.isMesh) {
              child.castShadow = true;
              child.receiveShadow = true;
              if (child.geometry) {
                child.geometry.computeVertexNormals();
              }
              if (child.material) {
                child.material.roughness = Math.max(child.material.roughness, 0.4);
                // Gold visor reflection enhancement
                if (child.material.name && child.material.name.toLowerCase().includes('visor')) {
                  child.material.metalness = 0.98;
                  child.material.roughness = 0.05;
                }
              }
            }
          });

          const rootGroup = new THREE.Group();
          rootGroup.add(model);

          if (this.astronautMesh) {
            this.scene.remove(this.astronautMesh);
          }
          this.astronautMesh = rootGroup;
          this.scene.add(this.astronautMesh);

          const badge = document.getElementById('hero-model-status-badge');
          if (badge) {
            badge.innerHTML = `<i class="bi bi-patch-check-fill text-success me-1"></i>NASA 3D ASTRONAUT RIG LOADED`;
          }
        },
        undefined,
        (err) => {
          console.warn('[AstronautPreview] GLTF load fallback to procedural masterpiece:', err);
        }
      );
    }
  },

  buildMasterpieceAstronaut() {
    const root = new THREE.Group();

    // High quality PBR materials
    const suitWhite = new THREE.MeshStandardMaterial({
      color: 0xf3f4f6,
      roughness: 0.65,
      metalness: 0.08
    });

    const visorGold = new THREE.MeshPhysicalMaterial({
      color: 0xffaa00,
      metalness: 0.96,
      roughness: 0.06,
      clearcoat: 1.0,
      clearcoatRoughness: 0.04,
      emissive: 0x442a00,
      emissiveIntensity: 0.3
    });

    const navyTrim = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      roughness: 0.5,
      metalness: 0.3
    });

    const cyanGlow = new THREE.MeshBasicMaterial({ color: 0x00f2fe });
    const redAccent = new THREE.MeshBasicMaterial({ color: 0xef4444 });

    // 1. Torso & Thermal Garment (Facing towards +Z)
    const torsoGeo = new THREE.CylinderGeometry(0.32, 0.28, 0.75, 24);
    const torso = new THREE.Mesh(torsoGeo, suitWhite);
    torso.position.y = 1.05;
    root.add(torso);

    // 2. Chest DCM (Display & Control Module) on front (+Z)
    const dcmGeo = new THREE.BoxGeometry(0.34, 0.28, 0.14);
    const dcm = new THREE.Mesh(dcmGeo, navyTrim);
    dcm.position.set(0, 1.15, 0.22);
    root.add(dcm);

    // DCM Status Gauges & LEDs
    const led1 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.04, 0.02), cyanGlow);
    led1.position.set(0.08, 1.22, 0.3);
    root.add(led1);
    const led2 = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.04, 0.02), redAccent);
    led2.position.set(-0.08, 1.22, 0.3);
    root.add(led2);

    // 3. PLSS Backpack on rear (-Z)
    const plssGeo = new THREE.BoxGeometry(0.5, 0.75, 0.3);
    const plss = new THREE.Mesh(plssGeo, suitWhite);
    plss.position.set(0, 1.1, -0.26);
    root.add(plss);

    // Oxygen tank cylinders on backpack
    const tankGeo = new THREE.CylinderGeometry(0.09, 0.09, 0.6, 16);
    const tank1 = new THREE.Mesh(tankGeo, navyTrim);
    tank1.position.set(0.14, 1.15, -0.36);
    const tank2 = new THREE.Mesh(tankGeo, navyTrim);
    tank2.position.set(-0.14, 1.15, -0.36);
    root.add(tank1);
    root.add(tank2);

    // Comms antenna
    const antGeo = new THREE.CylinderGeometry(0.008, 0.008, 0.45, 8);
    const ant = new THREE.Mesh(antGeo, navyTrim);
    ant.position.set(0.18, 1.6, -0.26);
    root.add(ant);

    // 4. Helmet Dome & Gleaming Gold Visor (Facing forward towards +Z)
    const helmetGeo = new THREE.SphereGeometry(0.28, 28, 28);
    const helmet = new THREE.Mesh(helmetGeo, suitWhite);
    helmet.position.set(0, 1.55, 0);
    root.add(helmet);

    // Curved gold visor
    const visorGeo = new THREE.SphereGeometry(0.22, 24, 24, 0, Math.PI);
    const visor = new THREE.Mesh(visorGeo, visorGold);
    visor.rotation.y = Math.PI / 2;
    visor.rotation.x = -0.12;
    visor.position.set(0, 1.55, 0.12);
    root.add(visor);

    // 5. Arms & Detailed Gloves
    const armGeo = new THREE.CylinderGeometry(0.09, 0.08, 0.58, 16);
    const lArm = new THREE.Mesh(armGeo, suitWhite);
    lArm.position.set(0.36, 1.22, 0.05);
    lArm.rotation.z = -0.3;
    lArm.rotation.x = 0.15;
    root.add(lArm);

    const rArm = new THREE.Mesh(armGeo, suitWhite);
    rArm.position.set(-0.36, 1.22, 0.05);
    rArm.rotation.z = 0.3;
    rArm.rotation.x = 0.15;
    root.add(rArm);

    // Gloves
    const gloveGeo = new THREE.BoxGeometry(0.12, 0.14, 0.12);
    const lGlove = new THREE.Mesh(gloveGeo, navyTrim);
    lGlove.position.set(0.5, 0.95, 0.12);
    const rGlove = new THREE.Mesh(gloveGeo, navyTrim);
    rGlove.position.set(-0.5, 0.95, 0.12);
    root.add(lGlove);
    root.add(rGlove);

    // 6. Legs & Lunar Boots
    const legGeo = new THREE.CylinderGeometry(0.11, 0.09, 0.68, 16);
    const lLeg = new THREE.Mesh(legGeo, suitWhite);
    lLeg.position.set(0.15, 0.48, 0);
    root.add(lLeg);

    const rLeg = new THREE.Mesh(legGeo, suitWhite);
    rLeg.position.set(-0.15, 0.48, 0);
    root.add(rLeg);

    // Boots
    const bootGeo = new THREE.BoxGeometry(0.18, 0.14, 0.32);
    const lBoot = new THREE.Mesh(bootGeo, navyTrim);
    lBoot.position.set(0.15, 0.1, 0.06);
    const rBoot = new THREE.Mesh(bootGeo, navyTrim);
    rBoot.position.set(-0.15, 0.1, 0.06);
    root.add(lBoot);
    root.add(rBoot);

    // Initial slight 3/4 hero rotation
    root.rotation.y = 0.15;
    return root;
  },

  setupControls() {
    const canvas = this.renderer.domElement;

    canvas.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.prevMouseX = e.clientX;
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        const dx = e.clientX - this.prevMouseX;
        this.targetRotationY += dx * 0.012;
        this.prevMouseX = e.clientX;
      }
    });

    // Touch controls for mobile
    canvas.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        this.isDragging = true;
        this.prevMouseX = e.touches[0].clientX;
      }
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (this.isDragging && e.touches.length === 1) {
        const dx = e.touches[0].clientX - this.prevMouseX;
        this.targetRotationY += dx * 0.014;
        this.prevMouseX = e.touches[0].clientX;
      }
    }, { passive: true });

    window.addEventListener('touchend', () => {
      this.isDragging = false;
    });
  },

  animate() {
    this.animationId = requestAnimationFrame(() => this.animate());

    const elapsedTime = this.clock.getElapsedTime();

    // Smooth drag interpolation
    this.currentRotationY += (this.targetRotationY - this.currentRotationY) * 0.08;

    // Elegant zero-gravity idle float:
    // Astronaut maintains forward-facing orientation with subtle natural sway
    if (this.astronautMesh) {
      this.astronautMesh.position.y = Math.sin(elapsedTime * 1.4) * 0.04;
      this.astronautMesh.rotation.y = this.currentRotationY + Math.sin(elapsedTime * 0.9) * 0.05;
      this.astronautMesh.rotation.z = Math.cos(elapsedTime * 0.7) * 0.02;
    }

    if (this.pedestal) {
      this.pedestal.rotation.y = -elapsedTime * 0.25;
    }

    this.renderer.render(this.scene, this.camera);
  },

  onResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const width = this.container.clientWidth || 440;
    const height = this.container.clientHeight || 440;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }
};
