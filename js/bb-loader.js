/**
 * RAF Otomatik BB Loader — procedural Three.js model
 * Hopper + gövde + krank/dişli besleme + nozul + şarjör adaptörü
 */

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const POLYMER = 0x2c2a28;
const POLYMER_LIGHT = 0x3a3a38;
const STEEL = 0x5a5854;
const BRASS = 0xc4a35a;
const ACCENT = 0xa63d1b;
const RUBBER = 0x1a1a1a;
const GRIP = 0x1e2a22;
const BB = 0xe8e4dc;
const WINDOW = 0x88a8b8;

let scene, camera, renderer, controls, root;
let clock = new THREE.Clock();
let highlightTarget = null;
let highlightPulse = 0;
let loading = false;
let crankAngle = 0;
let gearMesh = null;
let crankMesh = null;
let bbParticles = [];
const partMeshes = {};

init();
animate();

function init() {
  const wrap = document.getElementById("canvas-wrap");

  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x12100e, 0.022);

  camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.05, 50);
  camera.position.set(0.55, 0.28, 0.85);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  wrap.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.minDistance = 0.45;
  controls.maxDistance = 2.4;
  controls.target.set(0, 0.08, 0.05);
  controls.maxPolarAngle = Math.PI * 0.88;

  addLights();
  root = buildLoader();
  scene.add(root);

  const floor = new THREE.Mesh(
    new THREE.CircleGeometry(0.9, 48),
    new THREE.MeshStandardMaterial({
      color: 0x0a0908,
      roughness: 1,
      metalness: 0,
      transparent: true,
      opacity: 0.55,
    })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.28;
  floor.receiveShadow = true;
  scene.add(floor);

  window.addEventListener("resize", onResize);
  bindUI();
}

function addLights() {
  scene.add(new THREE.AmbientLight(0xfff0e0, 0.38));

  const key = new THREE.DirectionalLight(0xffe8c8, 1.4);
  key.position.set(1.2, 1.8, 1.4);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.near = 0.2;
  key.shadow.camera.far = 8;
  key.shadow.camera.left = -1.5;
  key.shadow.camera.right = 1.5;
  key.shadow.camera.top = 1.5;
  key.shadow.camera.bottom = -1.5;
  key.shadow.bias = -0.0003;
  scene.add(key);

  const fill = new THREE.DirectionalLight(0xb8c4d8, 0.5);
  fill.position.set(-1.5, 0.8, -0.8);
  scene.add(fill);

  const rim = new THREE.SpotLight(0xc4a35a, 8, 6, Math.PI / 5, 0.45, 1);
  rim.position.set(-0.6, 1.2, 0.9);
  rim.target.position.set(0, 0.1, 0);
  scene.add(rim);
  scene.add(rim.target);
}

function mat(color, opts = {}) {
  return new THREE.MeshStandardMaterial({
    color,
    roughness: opts.roughness ?? 0.55,
    metalness: opts.metalness ?? 0.15,
    ...opts,
  });
}

function box(w, h, d, material, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  m.position.set(x, y, z);
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

function cyl(rTop, rBot, h, material, segs = 28) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rTop, rBot, h, segs), material);
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

function buildLoader() {
  const group = new THREE.Group();
  group.position.y = -0.05;

  const polymer = mat(POLYMER, { roughness: 0.62, metalness: 0.12 });
  const polymerLite = mat(POLYMER_LIGHT, { roughness: 0.55, metalness: 0.18 });
  const steel = mat(STEEL, { roughness: 0.35, metalness: 0.75 });
  const brass = mat(BRASS, { roughness: 0.28, metalness: 0.9 });
  const accent = mat(ACCENT, { roughness: 0.4, metalness: 0.35 });
  const rubber = mat(RUBBER, { roughness: 0.92, metalness: 0.05 });
  const grip = mat(GRIP, { roughness: 0.88, metalness: 0.05 });
  const glass = mat(WINDOW, {
    roughness: 0.15,
    metalness: 0.05,
    transparent: true,
    opacity: 0.35,
  });
  const bbMat = mat(BB, { roughness: 0.25, metalness: 0.05 });

  // --- Gövde ---
  const body = new THREE.Group();
  body.add(box(0.12, 0.22, 0.145, polymer, 0, 0.05, 0));
  // yan paneller
  body.add(box(0.01, 0.2, 0.13, polymerLite, -0.055, 0.05, 0));
  body.add(box(0.01, 0.2, 0.13, polymerLite, 0.055, 0.05, 0));
  // kapasite penceresi
  body.add(box(0.055, 0.08, 0.006, glass, 0, 0.04, -0.072));
  // marka plakası
  body.add(box(0.05, 0.018, 0.004, brass, 0, -0.02, -0.074));
  group.add(body);
  partMeshes.body = body;

  // --- Tutamak ---
  const gripG = new THREE.Group();
  gripG.add(box(0.09, 0.12, 0.03, grip, 0, -0.01, -0.085));
  for (let i = 0; i < 5; i++) {
    gripG.add(box(0.085, 0.008, 0.006, rubber, 0, -0.05 + i * 0.022, -0.098));
  }
  group.add(gripG);
  partMeshes.grip = gripG;

  // --- Hopper ---
  const hopper = new THREE.Group();
  const hopperWall = cyl(0.078, 0.078, 0.11, polymerLite, 40);
  hopperWall.position.set(0, 0.22, 0);
  hopper.add(hopperWall);

  const hopperInner = cyl(0.068, 0.068, 0.1, glass, 40);
  hopperInner.position.set(0, 0.22, 0);
  hopper.add(hopperInner);

  const funnel = cyl(0.068, 0.02, 0.04, polymer, 32);
  funnel.position.set(0, 0.155, 0);
  hopper.add(funnel);

  const cap = cyl(0.082, 0.082, 0.012, brass, 40);
  cap.position.set(0, 0.28, 0);
  hopper.add(cap);
  const capKnob = cyl(0.02, 0.02, 0.012, brass, 20);
  capKnob.position.set(0, 0.292, 0);
  hopper.add(capKnob);

  // hopper içi BB dolgusu
  for (let i = 0; i < 48; i++) {
    const bb = new THREE.Mesh(new THREE.SphereGeometry(0.006, 10, 10), bbMat);
    const a = Math.random() * Math.PI * 2;
    const r = Math.random() * 0.055;
    bb.position.set(
      Math.cos(a) * r,
      0.18 + Math.random() * 0.08,
      Math.sin(a) * r
    );
    bb.castShadow = true;
    hopper.add(bb);
  }
  group.add(hopper);
  partMeshes.hopper = hopper;

  // --- Dişli + krank ---
  const drive = new THREE.Group();
  gearMesh = makeGear(steel, brass);
  gearMesh.position.set(0, 0.03, 0.02);
  drive.add(gearMesh);

  crankMesh = new THREE.Group();
  crankMesh.position.set(0.09, 0.03, 0.02);

  const shaft = cyl(0.008, 0.008, 0.04, steel, 16);
  shaft.rotation.z = Math.PI / 2;
  shaft.position.set(-0.02, 0, 0);
  crankMesh.add(shaft);

  const hub = cyl(0.016, 0.016, 0.01, brass, 20);
  hub.rotation.z = Math.PI / 2;
  crankMesh.add(hub);

  const arm = box(0.008, 0.065, 0.008, brass, 0, 0.032, 0);
  crankMesh.add(arm);
  const knob = new THREE.Mesh(new THREE.SphereGeometry(0.014, 16, 16), rubber);
  knob.position.set(0, 0.065, 0);
  knob.castShadow = true;
  crankMesh.add(knob);
  drive.add(crankMesh);
  group.add(drive);
  partMeshes.drive = drive;

  // --- Besleme tüpü + nozul ---
  const feed = new THREE.Group();
  const tube = cyl(0.014, 0.014, 0.12, steel, 20);
  tube.rotation.x = Math.PI / 2;
  tube.position.set(0, -0.04, 0.12);
  feed.add(tube);

  const nozzle = cyl(0.014, 0.01, 0.045, steel, 20);
  nozzle.rotation.x = Math.PI / 2;
  nozzle.position.set(0, -0.04, 0.195);
  feed.add(nozzle);

  const collar = cyl(0.022, 0.022, 0.028, accent, 24);
  collar.rotation.x = Math.PI / 2;
  collar.position.set(0, -0.04, 0.225);
  feed.add(collar);

  // O-ring
  const oring = cyl(0.024, 0.024, 0.006, rubber, 24);
  oring.rotation.x = Math.PI / 2;
  oring.position.set(0, -0.04, 0.24);
  feed.add(oring);
  group.add(feed);
  partMeshes.feed = feed;

  // --- Pil bölmesi ---
  const battery = new THREE.Group();
  battery.add(box(0.06, 0.1, 0.036, rubber, 0, -0.02, -0.055));
  battery.add(box(0.02, 0.012, 0.006, brass, 0.018, 0.02, -0.072));
  group.add(battery);
  partMeshes.battery = battery;

  // --- Demo şarjör ---
  const mag = new THREE.Group();
  mag.add(box(0.035, 0.14, 0.045, polymerLite, 0, -0.05, 0.3));
  mag.add(box(0.038, 0.02, 0.048, steel, 0, 0.02, 0.3));
  mag.add(box(0.02, 0.03, 0.02, accent, 0, 0.045, 0.3));
  // şarjör doluluk göstergesi
  for (let i = 0; i < 8; i++) {
    const pellet = new THREE.Mesh(new THREE.SphereGeometry(0.005, 8, 8), bbMat);
    pellet.position.set(0, -0.1 + i * 0.015, 0.3);
    mag.add(pellet);
  }
  group.add(mag);
  partMeshes.magazine = mag;

  // animasyon parçacıkları (besleme hattı)
  for (let i = 0; i < 16; i++) {
    const p = new THREE.Mesh(new THREE.SphereGeometry(0.0055, 8, 8), bbMat);
    p.visible = false;
    p.userData.phase = i / 16;
    group.add(p);
    bbParticles.push(p);
  }

  return group;
}

function makeGear(steel, brass) {
  const g = new THREE.Group();
  const disc = cyl(0.032, 0.032, 0.012, steel, 32);
  disc.rotation.x = Math.PI / 2;
  g.add(disc);
  for (let i = 0; i < 12; i++) {
    const tooth = box(0.01, 0.012, 0.012, brass, 0, 0, 0);
    const a = (i / 12) * Math.PI * 2;
    tooth.position.set(Math.cos(a) * 0.034, Math.sin(a) * 0.034, 0);
    tooth.rotation.z = a;
    g.add(tooth);
  }
  const hub = cyl(0.01, 0.01, 0.016, brass, 16);
  hub.rotation.x = Math.PI / 2;
  g.add(hub);
  return g;
}

function bindUI() {
  document.getElementById("btn-reset")?.addEventListener("click", () => {
    camera.position.set(0.55, 0.28, 0.85);
    controls.target.set(0, 0.08, 0.05);
    controls.update();
    setLoading(false);
  });

  document.getElementById("btn-spin")?.addEventListener("click", () => {
    controls.autoRotate = !controls.autoRotate;
    controls.autoRotateSpeed = 1.4;
    const btn = document.getElementById("btn-spin");
    btn.classList.toggle("active", controls.autoRotate);
    btn.textContent = controls.autoRotate ? "Döndürmeyi Durdur" : "Otomatik Döndür";
  });

  document.getElementById("btn-load")?.addEventListener("click", () => {
    setLoading(!loading);
  });

  document.querySelectorAll(".part-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".part-chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      focusPart(chip.dataset.part);
    });
  });
}

function setLoading(on) {
  loading = on;
  const btn = document.getElementById("btn-load");
  if (btn) {
    btn.classList.toggle("active", loading);
    btn.textContent = loading ? "Yüklemeyi Durdur" : "Otomatik Yükle";
  }
  bbParticles.forEach((p) => {
    p.visible = loading;
  });
}

function focusPart(key) {
  const target = partMeshes[key];
  if (!target) return;

  highlightTarget = target;
  highlightPulse = 0;

  const box3 = new THREE.Box3().setFromObject(target);
  const center = box3.getCenter(new THREE.Vector3());
  const size = box3.getSize(new THREE.Vector3());
  const dist = Math.max(size.x, size.y, size.z) * 3.8 + 0.35;

  const endPos = new THREE.Vector3(
    center.x + dist * 0.55,
    center.y + dist * 0.3,
    center.z + dist * 0.75
  );
  animateCamera(endPos, center);
}

function animateCamera(toPos, toTarget) {
  const fromPos = camera.position.clone();
  const fromTarget = controls.target.clone();
  const start = performance.now();
  const dur = 700;

  function step(now) {
    const t = Math.min(1, (now - start) / dur);
    const e = 1 - Math.pow(1 - t, 3);
    camera.position.lerpVectors(fromPos, toPos, e);
    controls.target.lerpVectors(fromTarget, toTarget, e);
    controls.update();
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  if (root) {
    root.rotation.y = Math.sin(t * 0.3) * 0.05;
    root.position.y = -0.05 + Math.sin(t * 0.45) * 0.008;
  }

  if (loading) {
    crankAngle = t * 8;
    if (gearMesh) gearMesh.rotation.z = crankAngle;
    if (crankMesh) crankMesh.rotation.x = crankAngle;

    // BB parçacık yolu: hopper → tüp → şarjör
    bbParticles.forEach((p) => {
      const u = (t * 0.55 + p.userData.phase) % 1;
      if (u < 0.25) {
        const v = u / 0.25;
        p.position.set(Math.sin(t + p.userData.phase * 10) * 0.01, 0.14 - v * 0.16, 0);
      } else if (u < 0.7) {
        const v = (u - 0.25) / 0.45;
        p.position.set(0, -0.04, 0.06 + v * 0.16);
      } else {
        const v = (u - 0.7) / 0.3;
        p.position.set(0, -0.1 + v * 0.12, 0.3);
      }
    });
  }

  if (highlightTarget) {
    highlightPulse += 0.05;
    const pulse = 0.5 + Math.sin(highlightPulse) * 0.5;
    highlightTarget.traverse((c) => {
      if (c.isMesh && c.material && c.material.emissive) {
        c.material.emissive.setHex(0xc4a35a);
        c.material.emissiveIntensity = pulse * 0.28;
      }
    });
  }

  controls.update();
  renderer.render(scene, camera);
}
