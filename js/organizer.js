/**
 * Wall-mounted firearm organizer — procedural Three.js model
 * Layout: oak backboard + steel frame, 4 rifle cradles, 2 pistol mounts,
 * magazine rack, accessory shelf, peg strip.
 */

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";

const OAK = 0x8b5a2b;
const OAK_DARK = 0x5c3a1a;
const STEEL = 0x3a3a38;
const STEEL_LIGHT = 0x5a5854;
const BRASS = 0xc4a35a;
const FELT = 0x1e2a22;
const RUBBER = 0x1a1a1a;

let scene, camera, renderer, controls, root;
let clock = new THREE.Clock();
let highlightTarget = null;
let highlightPulse = 0;
const partMeshes = {};

const stlLoader = new STLLoader();
let uploadedModel = null;

init();
animate();

function init() {
  const wrap = document.getElementById("canvas-wrap");

  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x12100e, 0.018);

  camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(2.8, 1.1, 4.2);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  wrap.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.minDistance = 2.2;
  controls.maxDistance = 8;
  controls.target.set(0, 0.55, 0);
  controls.maxPolarAngle = Math.PI * 0.85;

  addLights();
  root = buildOrganizer();
  scene.add(root);

  // Soft floor shadow plane
  const floor = new THREE.Mesh(
    new THREE.CircleGeometry(3.2, 48),
    new THREE.MeshStandardMaterial({
      color: 0x0a0908,
      roughness: 1,
      metalness: 0,
      transparent: true,
      opacity: 0.55,
    })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.9;
  floor.receiveShadow = true;
  scene.add(floor);

  window.addEventListener("resize", onResize);
  bindUI();
}

function addLights() {
  const amb = new THREE.AmbientLight(0xfff0e0, 0.35);
  scene.add(amb);

  const key = new THREE.DirectionalLight(0xffe8c8, 1.35);
  key.position.set(3.5, 5, 4);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.near = 1;
  key.shadow.camera.far = 20;
  key.shadow.camera.left = -4;
  key.shadow.camera.right = 4;
  key.shadow.camera.top = 4;
  key.shadow.camera.bottom = -4;
  key.shadow.bias = -0.0002;
  scene.add(key);

  const fill = new THREE.DirectionalLight(0xb8c4d8, 0.45);
  fill.position.set(-4, 2, -2);
  scene.add(fill);

  const rim = new THREE.SpotLight(0xc4a35a, 12, 12, Math.PI / 5, 0.4, 1);
  rim.position.set(-1.5, 3.5, 3);
  rim.target.position.set(0, 0.5, 0);
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

function cyl(rTop, rBot, h, material, x = 0, y = 0, z = 0, rx = 0, rz = 0) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rTop, rBot, h, 24), material);
  m.position.set(x, y, z);
  m.rotation.x = rx;
  m.rotation.z = rz;
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

function buildOrganizer() {
  const group = new THREE.Group();
  group.position.y = -0.35;

  const oak = mat(OAK, { roughness: 0.7, metalness: 0.05 });
  const oakDark = mat(OAK_DARK, { roughness: 0.75, metalness: 0.05 });
  const steel = mat(STEEL, { roughness: 0.35, metalness: 0.85 });
  const steelLite = mat(STEEL_LIGHT, { roughness: 0.4, metalness: 0.7 });
  const brass = mat(BRASS, { roughness: 0.3, metalness: 0.9 });
  const felt = mat(FELT, { roughness: 0.95, metalness: 0 });
  const rubber = mat(RUBBER, { roughness: 0.9, metalness: 0.05 });

  // --- Backboard ---
  const board = box(2.4, 2.0, 0.08, oak, 0, 1.0, -0.04);
  group.add(board);
  partMeshes.board = board;

  // Edge trim
  group.add(box(2.48, 0.06, 0.12, oakDark, 0, 2.03, -0.02));
  group.add(box(2.48, 0.06, 0.12, oakDark, 0, -0.03, -0.02));
  group.add(box(0.06, 2.12, 0.12, oakDark, -1.23, 1.0, -0.02));
  group.add(box(0.06, 2.12, 0.12, oakDark, 1.23, 1.0, -0.02));

  // Steel vertical rails
  group.add(box(0.05, 1.85, 0.05, steel, -1.05, 1.0, 0.05));
  group.add(box(0.05, 1.85, 0.05, steel, 1.05, 1.0, 0.05));

  // --- Top accessory shelf ---
  const shelf = new THREE.Group();
  shelf.add(box(2.2, 0.04, 0.28, oakDark, 0, 1.88, 0.14));
  shelf.add(box(2.2, 0.03, 0.03, steel, 0, 1.86, 0.27));
  // Small brass pegs on shelf edge
  for (let i = -3; i <= 3; i++) {
    shelf.add(cyl(0.012, 0.012, 0.06, brass, i * 0.28, 1.91, 0.22));
  }
  group.add(shelf);
  partMeshes.shelf = shelf;

  // --- Rifle cradles (4) ---
  const cradles = new THREE.Group();
  const cradleXs = [-0.72, -0.24, 0.24, 0.72];
  cradleXs.forEach((x, i) => {
    cradles.add(makeRifleCradle(x, oak, felt, steel, rubber, i));
  });
  group.add(cradles);
  partMeshes.cradles = cradles;

  // --- Magazine rack (lower left) ---
  const magRack = makeMagazineRack(oakDark, steel, felt);
  magRack.position.set(-0.72, 0.22, 0.12);
  group.add(magRack);
  partMeshes.magazines = magRack;

  // --- Pistol mounts (right side) ---
  const pistols = new THREE.Group();
  pistols.add(makePistolMount(0.85, 1.35, steel, felt, brass));
  pistols.add(makePistolMount(0.85, 0.85, steel, felt, brass));
  group.add(pistols);
  partMeshes.pistols = pistols;

  // --- Peg strip with hooks ---
  const pegs = new THREE.Group();
  pegs.add(box(0.9, 0.08, 0.04, steelLite, 0.55, 0.35, 0.06));
  for (let i = 0; i < 5; i++) {
    const hx = 0.25 + i * 0.15;
    pegs.add(makeHook(hx, 0.32, steel, brass));
  }
  group.add(pegs);
  partMeshes.pegs = pegs;

  // Brand plate
  const plate = box(0.55, 0.12, 0.02, steel, 0, 0.08, 0.05);
  group.add(plate);
  const badge = box(0.5, 0.08, 0.015, brass, 0, 0.08, 0.065);
  group.add(badge);

  // Wall mount brackets
  group.add(box(0.12, 0.08, 0.1, steel, -1.1, 1.85, -0.1));
  group.add(box(0.12, 0.08, 0.1, steel, 1.1, 1.85, -0.1));
  group.add(box(0.12, 0.08, 0.1, steel, -1.1, 0.15, -0.1));
  group.add(box(0.12, 0.08, 0.1, steel, 1.1, 0.15, -0.1));

  // Subtle demo firearms (silhouettes) — optional visual fill
  cradleXs.forEach((x, i) => {
    group.add(makeRifleSilhouette(x, 0.15 + (i % 2) * 0.05, felt));
  });
  group.add(makePistolSilhouette(0.85, 1.35, felt));
  group.add(makePistolSilhouette(0.85, 0.85, felt));

  return group;
}

function makeRifleCradle(x, oak, felt, steel, rubber, index) {
  const g = new THREE.Group();
  // Upper barrel rest
  const upper = box(0.22, 0.06, 0.18, oak, x, 1.55, 0.12);
  g.add(upper);
  g.add(box(0.16, 0.02, 0.14, felt, x, 1.58, 0.13));
  // Lower stock rest with V-notch look (two angled pads)
  g.add(box(0.28, 0.08, 0.2, oak, x, 0.55, 0.13));
  g.add(box(0.1, 0.04, 0.16, felt, x - 0.05, 0.6, 0.14));
  g.add(box(0.1, 0.04, 0.16, felt, x + 0.05, 0.6, 0.14));
  // Rubber bumper
  g.add(cyl(0.03, 0.03, 0.08, rubber, x, 0.42, 0.14, Math.PI / 2));
  // Steel retainer pin
  g.add(cyl(0.01, 0.01, 0.14, steel, x, 1.62, 0.18, Math.PI / 2));
  // Number badge
  const num = box(0.06, 0.06, 0.01, steel, x, 0.48, 0.24);
  g.add(num);
  return g;
}

function makeMagazineRack(oak, steel, felt) {
  const g = new THREE.Group();
  g.add(box(0.55, 0.04, 0.22, oak, 0, 0, 0));
  g.add(box(0.55, 0.18, 0.02, oak, 0, 0.09, -0.1));
  // Dividers — 4 mag slots
  for (let i = 0; i < 5; i++) {
    g.add(box(0.015, 0.16, 0.2, steel, -0.24 + i * 0.12, 0.1, 0));
  }
  // Soft lining bottoms
  for (let i = 0; i < 4; i++) {
    g.add(box(0.09, 0.01, 0.18, felt, -0.18 + i * 0.12, 0.025, 0.01));
    // Mag silhouette
    g.add(box(0.07, 0.14, 0.04, steel, -0.18 + i * 0.12, 0.1, 0.04));
  }
  return g;
}

function makePistolMount(x, y, steel, felt, brass) {
  const g = new THREE.Group();
  // Cradle plate
  g.add(box(0.28, 0.08, 0.16, steel, x, y, 0.1));
  g.add(box(0.22, 0.02, 0.12, felt, x, y + 0.05, 0.11));
  // Trigger-guard hook
  g.add(cyl(0.018, 0.018, 0.1, brass, x, y - 0.02, 0.18, Math.PI / 2));
  g.add(cyl(0.022, 0.022, 0.04, brass, x, y - 0.06, 0.22));
  return g;
}

function makeHook(x, y, steel, brass) {
  const g = new THREE.Group();
  g.add(cyl(0.012, 0.012, 0.08, steel, x, y, 0.08, Math.PI / 2));
  g.add(cyl(0.014, 0.014, 0.05, brass, x, y - 0.02, 0.12, 0, Math.PI / 2));
  return g;
}

function makeRifleSilhouette(x, lean, material) {
  const g = new THREE.Group();
  // Stock
  g.add(box(0.06, 0.12, 0.18, material, x, 0.72, 0.16));
  // Receiver
  g.add(box(0.05, 0.08, 0.28, material, x, 0.95, 0.14));
  // Barrel
  g.add(cyl(0.015, 0.015, 0.7, material, x, 1.35, 0.14));
  // Handguard
  g.add(box(0.045, 0.05, 0.22, material, x, 1.15, 0.14));
  g.rotation.z = lean * 0.02;
  g.traverse((c) => {
    if (c.isMesh) {
      c.castShadow = true;
      c.material = material.clone();
      c.material.transparent = true;
      c.material.opacity = 0.55;
    }
  });
  return g;
}

function makePistolSilhouette(x, y, material) {
  const g = new THREE.Group();
  g.add(box(0.04, 0.08, 0.14, material, x, y + 0.08, 0.14));
  g.add(box(0.035, 0.1, 0.05, material, x, y - 0.02, 0.12));
  g.traverse((c) => {
    if (c.isMesh) {
      c.castShadow = true;
      c.material = material.clone();
      c.material.transparent = true;
      c.material.opacity = 0.5;
    }
  });
  return g;
}

function bindUI() {
  document.getElementById("btn-reset")?.addEventListener("click", () => {
    camera.position.set(2.8, 1.1, 4.2);
    controls.target.set(0, 0.55, 0);
    controls.update();
  });

  document.getElementById("btn-spin")?.addEventListener("click", () => {
    controls.autoRotate = !controls.autoRotate;
    controls.autoRotateSpeed = 1.2;
    const btn = document.getElementById("btn-spin");
    btn.classList.toggle("active", controls.autoRotate);
    btn.textContent = controls.autoRotate ? "Döndürmeyi Durdur" : "Otomatik Döndür";
  });

  document.querySelectorAll(".part-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".part-chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      const key = chip.dataset.part;
      focusPart(key);
    });
  });

  const uploadBtn = document.getElementById("btn-upload");
  const fileInput = document.getElementById("stl-input");
  const clearBtn = document.getElementById("btn-clear-stl");

  uploadBtn?.addEventListener("click", () => fileInput?.click());

  fileInput?.addEventListener("change", (e) => {
    const file = e.target.files && e.target.files[0];
    if (file) loadSTLFile(file);
    // Reset so selecting the same file again re-triggers change.
    e.target.value = "";
  });

  clearBtn?.addEventListener("click", clearUploadedModel);

  bindDragAndDrop();
}

function bindDragAndDrop() {
  const overlay = document.getElementById("drop-overlay");
  let dragDepth = 0;

  const showOverlay = () => overlay?.classList.add("is-active");
  const hideOverlay = () => overlay?.classList.remove("is-active");

  window.addEventListener("dragenter", (e) => {
    e.preventDefault();
    dragDepth += 1;
    showOverlay();
  });

  window.addEventListener("dragover", (e) => {
    e.preventDefault();
    if (e.dataTransfer) e.dataTransfer.dropEffect = "copy";
  });

  window.addEventListener("dragleave", (e) => {
    e.preventDefault();
    dragDepth = Math.max(0, dragDepth - 1);
    if (dragDepth === 0) hideOverlay();
  });

  window.addEventListener("drop", (e) => {
    e.preventDefault();
    dragDepth = 0;
    hideOverlay();
    const file = e.dataTransfer?.files && e.dataTransfer.files[0];
    if (file) loadSTLFile(file);
  });
}

function setUploadStatus(message, kind = "") {
  const el = document.getElementById("upload-status");
  if (!el) return;
  el.textContent = message;
  el.classList.remove("is-error", "is-ok");
  if (kind) el.classList.add(kind);
}

function loadSTLFile(file) {
  const name = file.name || "model.stl";
  if (!/\.stl$/i.test(name)) {
    setUploadStatus(`"${name}" bir STL dosyası değil.`, "is-error");
    return;
  }

  setUploadStatus(`"${name}" yükleniyor…`);

  const reader = new FileReader();
  reader.onerror = () => setUploadStatus(`"${name}" okunamadı.`, "is-error");
  reader.onload = (ev) => {
    try {
      const geometry = stlLoader.parse(ev.target.result);
      addUploadedGeometry(geometry, name);
    } catch (err) {
      console.error("STL parse error:", err);
      setUploadStatus(`"${name}" ayrıştırılamadı. Geçerli bir STL dosyası olduğundan emin olun.`, "is-error");
    }
  };
  reader.readAsArrayBuffer(file);
}

function addUploadedGeometry(geometry, name) {
  clearUploadedModel();

  geometry.computeBoundingBox();
  geometry.computeVertexNormals();

  // Center the geometry on its own origin.
  const bbox = geometry.boundingBox;
  const size = bbox.getSize(new THREE.Vector3());
  const center = bbox.getCenter(new THREE.Vector3());
  geometry.translate(-center.x, -center.y, -center.z);

  // Normalize scale so the largest dimension is a comfortable size in-scene.
  const maxDim = Math.max(size.x, size.y, size.z) || 1;
  const targetSize = 1.4;
  const scale = targetSize / maxDim;

  const material = new THREE.MeshStandardMaterial({
    color: 0xc4a35a,
    roughness: 0.4,
    metalness: 0.6,
    flatShading: false,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.scale.setScalar(scale);
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  // Float the model clearly in front of the organizer so it does not overlap it.
  mesh.position.set(0, 0.9, 1.9);

  uploadedModel = mesh;
  partMeshes.uploaded = mesh;
  scene.add(mesh);

  const dims = `${size.x.toFixed(1)} × ${size.y.toFixed(1)} × ${size.z.toFixed(1)}`;
  setUploadStatus(`"${name}" yüklendi (${dims} birim).`, "is-ok");

  const clearBtn = document.getElementById("btn-clear-stl");
  if (clearBtn) clearBtn.hidden = false;

  frameObject(mesh);
}

function clearUploadedModel() {
  if (!uploadedModel) return;
  scene.remove(uploadedModel);
  uploadedModel.geometry?.dispose();
  uploadedModel.material?.dispose();
  if (highlightTarget === uploadedModel) highlightTarget = null;
  uploadedModel = null;
  delete partMeshes.uploaded;

  const clearBtn = document.getElementById("btn-clear-stl");
  if (clearBtn) clearBtn.hidden = true;
  setUploadStatus("Yüklenen model kaldırıldı.");
}

function frameObject(object) {
  const box3 = new THREE.Box3().setFromObject(object);
  const center = box3.getCenter(new THREE.Vector3());
  const size = box3.getSize(new THREE.Vector3());
  const dist = Math.max(size.x, size.y, size.z) * 2.4 + 1.4;

  highlightTarget = object;
  highlightPulse = 0;

  const endPos = new THREE.Vector3(
    center.x + dist * 0.55,
    center.y + dist * 0.28,
    center.z + dist * 0.75
  );
  animateCamera(endPos, center);
}

function focusPart(key) {
  const target = partMeshes[key];
  if (!target) return;

  highlightTarget = target;
  highlightPulse = 0;

  const box3 = new THREE.Box3().setFromObject(target);
  const center = box3.getCenter(new THREE.Vector3());
  const size = box3.getSize(new THREE.Vector3());
  const dist = Math.max(size.x, size.y, size.z) * 3.2 + 1.2;

  const endPos = new THREE.Vector3(center.x + dist * 0.55, center.y + dist * 0.25, center.z + dist * 0.7);
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

  // Gentle idle bob of whole organizer
  if (root) {
    root.rotation.y = Math.sin(t * 0.25) * 0.04;
    root.position.y = -0.35 + Math.sin(t * 0.4) * 0.015;
  }

  // Highlight pulse
  if (highlightTarget) {
    highlightPulse += 0.05;
    const pulse = 0.5 + Math.sin(highlightPulse) * 0.5;
    highlightTarget.traverse((c) => {
      if (c.isMesh && c.material && c.material.emissive) {
        c.material.emissive.setHex(0xc4a35a);
        c.material.emissiveIntensity = pulse * 0.25;
      }
    });
  }

  controls.update();
  renderer.render(scene, camera);
}
