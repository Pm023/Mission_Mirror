/**
 * MISSION MIRROR — Astronaut Character & 3rd-Person Controller
 * Loads authentic NASA Astronaut.glb (with procedural EMU suit fallback),
 * dynamic walking cycle, environment gravity physics, 3rd-person follow camera,
 * and touch controls.
 */
class AstronautController {
  constructor(scene, camera, domElement) {
    this.scene = scene;
    this.camera = camera;
    this.domElement = domElement;

    // Movement state
    this.position = new THREE.Vector3(0, 0, 0);
    this.velocity = new THREE.Vector3(0, 0, 0);
    this.rotationY = 0; // Astronaut yaw
    this.isGrounded = true;
    this.moveSpeed = 6.8;

    // Environment physics
    this.gravity = 9.8;
    this.jumpPower = 5.0;
    this.environment = 'moon';

    // Camera follow parameters
    this.camDistance = 4.8;
    this.camHeight = 2.2;
    this.camYaw = 0;
    this.camPitch = 0.28;
    this.isOrbitDragging = false;
    this.prevMouseX = 0;
    this.prevMouseY = 0;

    // Key states
    this.keys = {
      forward: false,
      backward: false,
      left: false,
      right: false,
      jump: false,
      interact: false
    };

    // Animation state
    this.walkCycleTime = 0;
    this.isMoving = false;

    // Callbacks
    this.onProximity = null;
    this.onProximityExit = null;
    this.onInteract = null;
    this.activeObjectiveInProximity = null;
    this.objectives = [];

    // Terrain height function (provided by environment)
    this.getTerrainHeight = (x, z) => 0;

    // Root group
    this.mesh = new THREE.Group();
    this.scene.add(this.mesh);

    // Build procedural suit first (instant render)
    this.proceduralMesh = this.buildAstronautMesh();
    this.mesh.add(this.proceduralMesh);

    // Load authentic Astronaut.glb model
    this.glbModel = null;
    this.loadGLTFModel();

    // Setup input listeners
    this.setupInputs();
  }

  setEnvironment(envName) {
    this.environment = envName.toLowerCase();
    if (this.environment === 'moon') {
      this.gravity = 3.6; // 1/6 g
      this.jumpPower = 4.8;
      this.moveSpeed = 6.0;
    } else if (this.environment === 'mars') {
      this.gravity = 7.0; // 3/8 g
      this.jumpPower = 5.2;
      this.moveSpeed = 6.5;
    } else if (this.environment === 'station') {
      this.gravity = 0.8; // Microgravity floating
      this.jumpPower = 2.8;
      this.moveSpeed = 5.2;
    }
  }

  loadGLTFModel() {
    if (typeof THREE.GLTFLoader !== 'undefined') {
      const loader = new THREE.GLTFLoader();
      loader.load(
        'assets/models/Astronaut.glb',
        (gltf) => {
          const model = gltf.scene;

          // Compute size to normalize height to 2.1 meters
          const box = new THREE.Box3().setFromObject(model);
          const size = new THREE.Vector3();
          box.getSize(size);
          const center = new THREE.Vector3();
          box.getCenter(center);

          model.position.x = -center.x;
          model.position.y = -box.min.y;
          model.position.z = -center.z;

          const scale = 2.1 / size.y;
          model.scale.set(scale, scale, scale);

          model.traverse((child) => {
            if (child.isMesh && child.material) {
              child.castShadow = true;
              child.receiveShadow = true;
              if (child.material.color) {
                child.material.color.setRGB(1.2, 1.2, 1.2);
              }
              child.material.roughness = 0.52;
              child.material.metalness = 0.18;
              if (child.material.name && child.material.name.toLowerCase().includes('visor')) {
                child.material.metalness = 0.95;
                child.material.roughness = 0.05;
              }
            }
          });

          // Headlamp Spotlight attached to helmet
          const headlamp = new THREE.SpotLight(0xffffff, 3.5, 45, Math.PI / 4, 0.4);
          headlamp.position.set(0, 1.9, 0.35);
          headlamp.target.position.set(0, 1.5, 12);
          this.mesh.add(headlamp);
          this.mesh.add(headlamp.target);

          // Replace procedural mesh
          if (this.proceduralMesh && this.mesh.children.includes(this.proceduralMesh)) {
            this.mesh.remove(this.proceduralMesh);
          }
          this.glbModel = model;
          this.mesh.add(model);
          console.log('[AstronautController] Authentic Astronaut.glb loaded on character!');
        },
        undefined,
        (err) => {
          console.warn('[AstronautController] Falling back to procedural suit model:', err);
        }
      );
    }
  }

  buildAstronautMesh() {
    const root = new THREE.Group();

    // Material definitions
    const suitWhite = new THREE.MeshStandardMaterial({
      color: 0xeeeeee,
      roughness: 0.65,
      metalness: 0.1
    });

    const visorGold = new THREE.MeshPhysicalMaterial({
      color: 0xffaa00,
      metalness: 0.9,
      roughness: 0.1,
      clearcoat: 1.0,
      clearcoatRoughness: 0.05,
      emissive: 0x332200
    });

    const darkTrim = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      roughness: 0.5,
      metalness: 0.2
    });

    const cyanPack = new THREE.MeshBasicMaterial({ color: 0x00f2fe });

    // 1. Torso
    const torsoGeo = new THREE.BoxGeometry(0.75, 0.9, 0.5);
    const torso = new THREE.Mesh(torsoGeo, suitWhite);
    torso.position.y = 1.25;
    root.add(torso);

    // 2. Chest DCM (Display & Control Module)
    const chestGeo = new THREE.BoxGeometry(0.45, 0.35, 0.15);
    const chest = new THREE.Mesh(chestGeo, darkTrim);
    chest.position.set(0, 1.35, 0.28);
    root.add(chest);

    // DCM telemetry light
    const dcmLightGeo = new THREE.BoxGeometry(0.12, 0.06, 0.04);
    const dcmLight = new THREE.Mesh(dcmLightGeo, cyanPack);
    dcmLight.position.set(0.1, 1.4, 0.36);
    root.add(dcmLight);

    // 3. PLSS Backpack (Portable Life Support System)
    const plssGeo = new THREE.BoxGeometry(0.68, 0.95, 0.4);
    const plss = new THREE.Mesh(plssGeo, suitWhite);
    plss.position.set(0, 1.3, -0.4);
    root.add(plss);

    // PLSS antenna
    const antGeo = new THREE.CylinderGeometry(0.015, 0.015, 0.6, 8);
    const ant = new THREE.Mesh(antGeo, darkTrim);
    ant.position.set(0.25, 1.95, -0.4);
    root.add(ant);

    // 4. Helmet Dome & Visor
    const helmetGeo = new THREE.SphereGeometry(0.38, 20, 20);
    const helmet = new THREE.Mesh(helmetGeo, suitWhite);
    helmet.position.set(0, 1.95, 0);
    root.add(helmet);

    const visorGeo = new THREE.SphereGeometry(0.28, 16, 16, 0, Math.PI);
    const visor = new THREE.Mesh(visorGeo, visorGold);
    visor.rotation.y = Math.PI / 2;
    visor.rotation.x = -0.15;
    visor.position.set(0, 1.95, 0.18);
    root.add(visor);

    // Helmet Headlamp Flashlight
    const headlamp = new THREE.SpotLight(0xffffff, 3.5, 45, Math.PI / 4, 0.4);
    headlamp.position.set(0, 1.95, 0.35);
    headlamp.target.position.set(0, 1.6, 12);
    root.add(headlamp);
    root.add(headlamp.target);

    // 5. Articulated Limbs for Walking Cycle
    this.leftArm = new THREE.Group();
    const lArmGeo = new THREE.CylinderGeometry(0.12, 0.1, 0.7, 10);
    const lArmMesh = new THREE.Mesh(lArmGeo, suitWhite);
    lArmMesh.position.y = -0.35;
    this.leftArm.add(lArmMesh);
    this.leftArm.position.set(0.48, 1.6, 0);
    root.add(this.leftArm);

    this.rightArm = new THREE.Group();
    const rArmGeo = new THREE.CylinderGeometry(0.12, 0.1, 0.7, 10);
    const rArmMesh = new THREE.Mesh(rArmGeo, suitWhite);
    rArmMesh.position.y = -0.35;
    this.rightArm.add(rArmMesh);
    this.rightArm.position.set(-0.48, 1.6, 0);
    root.add(this.rightArm);

    this.leftLeg = new THREE.Group();
    const lLegGeo = new THREE.CylinderGeometry(0.14, 0.12, 0.8, 10);
    const lLegMesh = new THREE.Mesh(lLegGeo, suitWhite);
    lLegMesh.position.y = -0.4;
    this.leftLeg.add(lLegMesh);
    const lBootGeo = new THREE.BoxGeometry(0.24, 0.16, 0.4);
    const lBoot = new THREE.Mesh(lBootGeo, darkTrim);
    lBoot.position.set(0, -0.75, 0.08);
    this.leftLeg.add(lBoot);
    this.leftLeg.position.set(0.24, 0.8, 0);
    root.add(this.leftLeg);

    this.rightLeg = new THREE.Group();
    const rLegGeo = new THREE.CylinderGeometry(0.14, 0.12, 0.8, 10);
    const rLegMesh = new THREE.Mesh(rLegGeo, suitWhite);
    rLegMesh.position.y = -0.4;
    this.rightLeg.add(rLegMesh);
    const rBootGeo = new THREE.BoxGeometry(0.24, 0.16, 0.4);
    const rBoot = new THREE.Mesh(rBootGeo, darkTrim);
    rBoot.position.set(0, -0.75, 0.08);
    this.rightLeg.add(rBoot);
    this.rightLeg.position.set(-0.24, 0.8, 0);
    root.add(this.rightLeg);

    return root;
  }

  setupInputs() {
    window.addEventListener('keydown', (e) => {
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

      const code = e.code;
      if (code === 'KeyW' || code === 'ArrowUp') this.keys.forward = true;
      if (code === 'KeyS' || code === 'ArrowDown') this.keys.backward = true;
      if (code === 'KeyA' || code === 'ArrowLeft') this.keys.left = true;
      if (code === 'KeyD' || code === 'ArrowRight') this.keys.right = true;
      if (code === 'Space') {
        this.keys.jump = true;
        e.preventDefault();
      }
      if (code === 'KeyE') {
        this.triggerInteract();
      }
      if (code === 'Escape' || code === 'KeyP') {
        ExplorationHUD.togglePauseMenu();
      }
    });

    window.addEventListener('keyup', (e) => {
      const code = e.code;
      if (code === 'KeyW' || code === 'ArrowUp') this.keys.forward = false;
      if (code === 'KeyS' || code === 'ArrowDown') this.keys.backward = false;
      if (code === 'KeyA' || code === 'ArrowLeft') this.keys.left = false;
      if (code === 'KeyD' || code === 'ArrowRight') this.keys.right = false;
      if (code === 'Space') this.keys.jump = false;
    });

    // Mouse drag for camera orbit
    const canvas = this.domElement;
    canvas.addEventListener('mousedown', (e) => {
      if (e.button === 0) {
        this.isOrbitDragging = true;
        this.prevMouseX = e.clientX;
        this.prevMouseY = e.clientY;
      }
    });

    window.addEventListener('mouseup', () => {
      this.isOrbitDragging = false;
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isOrbitDragging) {
        const dx = e.clientX - this.prevMouseX;
        const dy = e.clientY - this.prevMouseY;

        this.camYaw -= dx * 0.005;
        this.camPitch = Math.max(-0.2, Math.min(0.85, this.camPitch + dy * 0.004));

        this.prevMouseX = e.clientX;
        this.prevMouseY = e.clientY;
      }
    });

    canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.camDistance = Math.max(2.5, Math.min(10.0, this.camDistance + (e.deltaY > 0 ? 0.4 : -0.4)));
    }, { passive: false });
  }

  triggerInteract() {
    if (this.activeObjectiveInProximity && this.onInteract) {
      if (typeof FlightAudio !== 'undefined') FlightAudio.playClick();
      this.onInteract(this.activeObjectiveInProximity);
    }
  }

  resetPosition(x = 0, z = 0) {
    this.position.set(x, this.getTerrainHeight(x, z), z);
    this.velocity.set(0, 0, 0);
    this.rotationY = 0;
    this.camYaw = 0;
    this.mesh.position.copy(this.position);
    this.updateCameraFollow(true);
  }

  update(delta) {
    let moveX = 0;
    let moveZ = 0;

    if (this.keys.forward) moveZ += 1;
    if (this.keys.backward) moveZ -= 1;
    if (this.keys.left) moveX -= 1;
    if (this.keys.right) moveX += 1;

    this.isMoving = (moveX !== 0 || moveZ !== 0);

    if (this.isMoving) {
      const len = Math.hypot(moveX, moveZ);
      moveX /= len;
      moveZ /= len;

      const forwardAngle = this.camYaw;
      const rightAngle = this.camYaw + Math.PI / 2;

      const worldMoveX = (Math.sin(forwardAngle) * moveZ) + (Math.sin(rightAngle) * moveX);
      const worldMoveZ = (Math.cos(forwardAngle) * moveZ) + (Math.cos(rightAngle) * moveX);

      this.velocity.x = worldMoveX * this.moveSpeed;
      this.velocity.z = worldMoveZ * this.moveSpeed;

      const targetRotation = Math.atan2(worldMoveX, worldMoveZ);
      let diff = targetRotation - this.rotationY;
      while (diff < -Math.PI) diff += Math.PI * 2;
      while (diff > Math.PI) diff -= Math.PI * 2;
      this.rotationY += diff * 0.15;
    } else {
      this.velocity.x *= 0.7;
      this.velocity.z *= 0.7;
    }

    if (this.keys.jump && this.isGrounded) {
      this.velocity.y = this.jumpPower;
      this.isGrounded = false;
      if (typeof FlightAudio !== 'undefined') FlightAudio.playTelemetryChirp();
    }

    this.velocity.y -= this.gravity * delta;

    this.position.x += this.velocity.x * delta;
    this.position.z += this.velocity.z * delta;
    this.position.y += this.velocity.y * delta;

    this.position.x = Math.max(-52, Math.min(52, this.position.x));
    this.position.z = Math.max(-52, Math.min(52, this.position.z));

    const terrainY = this.getTerrainHeight(this.position.x, this.position.z);
    if (this.position.y <= terrainY) {
      this.position.y = terrainY;
      this.velocity.y = 0;
      this.isGrounded = true;
    }

    this.mesh.position.copy(this.position);
    this.mesh.rotation.y = this.rotationY;

    // Movement animation
    if (this.glbModel) {
      // Gentle stride bobbing and natural lean for 3D GLB model
      if (this.isMoving && this.isGrounded) {
        this.walkCycleTime += delta * 7.5;
        this.glbModel.position.y = Math.abs(Math.sin(this.walkCycleTime * 2.0)) * 0.08;
        this.glbModel.rotation.z = Math.sin(this.walkCycleTime) * 0.04;
      } else if (!this.isGrounded) {
        this.glbModel.position.y = 0.1;
        this.glbModel.rotation.x = -0.12;
      } else {
        this.glbModel.position.y = 0;
        this.glbModel.rotation.z *= 0.85;
        this.glbModel.rotation.x *= 0.85;
      }
    } else if (this.leftLeg) {
      // Procedural limb animation
      if (this.isMoving && this.isGrounded) {
        this.walkCycleTime += delta * 7.5;
        const legAngle = Math.sin(this.walkCycleTime) * 0.45;
        const armAngle = -Math.sin(this.walkCycleTime) * 0.4;

        this.leftLeg.rotation.x = legAngle;
        this.rightLeg.rotation.x = -legAngle;
        this.leftArm.rotation.x = armAngle;
        this.rightArm.rotation.x = -armAngle;
      } else if (!this.isGrounded) {
        this.leftLeg.rotation.x = 0.25;
        this.rightLeg.rotation.x = -0.15;
        this.leftArm.rotation.x = -0.4;
        this.rightArm.rotation.x = -0.3;
      } else {
        this.leftLeg.rotation.x *= 0.85;
        this.rightLeg.rotation.x *= 0.85;
        this.leftArm.rotation.x *= 0.85;
        this.rightArm.rotation.x *= 0.85;
      }
    }

    this.updateCameraFollow();
    this.checkObjectiveProximity();
  }

  updateCameraFollow(immediate = false) {
    const targetCamX = this.position.x - Math.sin(this.camYaw) * this.camDistance * Math.cos(this.camPitch);
    const targetCamY = this.position.y + this.camHeight + Math.sin(this.camPitch) * this.camDistance;
    const targetCamZ = this.position.z - Math.cos(this.camYaw) * this.camDistance * Math.cos(this.camPitch);

    if (immediate) {
      this.camera.position.set(targetCamX, targetCamY, targetCamZ);
    } else {
      this.camera.position.x += (targetCamX - this.camera.position.x) * 0.12;
      this.camera.position.y += (targetCamY - this.camera.position.y) * 0.12;
      this.camera.position.z += (targetCamZ - this.camera.position.z) * 0.12;
    }

    const lookTarget = new THREE.Vector3(
      this.position.x,
      this.position.y + 1.4,
      this.position.z
    );
    this.camera.lookAt(lookTarget);
  }

  checkObjectiveProximity() {
    let closestObj = null;
    let closestDist = Infinity;

    for (const obj of this.objectives) {
      const dx = this.position.x - obj.coordinates.x;
      const dz = this.position.z - obj.coordinates.z;
      const dist = Math.hypot(dx, dz);

      obj.currentDistance = dist;

      if (dist < closestDist) {
        closestDist = dist;
        closestObj = obj;
      }
    }

    if (closestObj && closestDist <= 3.8) {
      if (this.activeObjectiveInProximity !== closestObj) {
        this.activeObjectiveInProximity = closestObj;
        if (this.onProximity) {
          this.onProximity(closestObj, closestDist);
        }
      } else if (this.onProximity) {
        this.onProximity(closestObj, closestDist);
      }
    } else {
      if (this.activeObjectiveInProximity !== null) {
        this.activeObjectiveInProximity = null;
        if (this.onProximityExit) {
          this.onProximityExit();
        }
      }
    }
  }

  dispose() {
    if (this.mesh && this.mesh.parent) {
      this.mesh.parent.remove(this.mesh);
    }
  }
}
