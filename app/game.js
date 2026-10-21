/* Rail Rush — endless 3-lane runner using the maps and models in ../models (three.js r160) */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const $ = (id) => document.getElementById(id);
if (location.protocol === 'file:') throw new Error('Rail Rush must be served over http (see start_game.bat)');

// ======================================================================
// Constants (match models/DESIGN.md: lanes ±2.6 m, train roof ≈ 3.7 m, 10 m segments)
// ======================================================================
const MODELS = '../models';
const LANE_W = 2.6;
const LANES = [-LANE_W, 0, LANE_W];
const TRAIN_H = 3.7, TRAIN_HW = 1.35, CAR_LEN = 12.275, CAR_STEP = 12.6, TRAIN_FRONT = 6.275;
const MODEL_Y = -0.1;                       // trains / ramps sit 0.1 m below the running surface
const RAMP_LEN = 6.05, RAMP_TOP = 3.34, RAMP_HW = 1.2, RAMP_TO_TRAIN = 2.75;
const BARRIER_HW = 1.3, LOW_MAX = 1.5, HIGH_Y0 = 1.45;
const PLAYER_H = 1.8, ROLL_H = 0.8, PLAYER_HW = 0.4, PLAYER_HD = 0.35;
const GRAVITY = -62, JUMP_V = 17.5, SNEAKER_JUMP_V = 24.5, FAST_FALL_V = -45;
const ROLL_TIME = 0.7, JET_Y = 4.9;
const BASE_SPEED = 16, MAX_SPEED = 36;
const AHEAD = 260, BEHIND = 15;
const CHUNK = 50, PERIOD = 300, NCHUNK = PERIOD / CHUNK;
const COIN_Y = 0.75, POWER_Y = 1.1, COIN_CAP = 1500;
const STUMBLE_WINDOW = 5, MAX_LIVES = 3;
const DECOR_KINDS = new Set(['segment', 'prop', 'backdrop', 'landmark']);

// Per-map look (same values as models/preview)
const MAPS = [
  { n: 1,  name: 'Enchanted Jungle Temple',    top: '#6fb8ff', hor: '#ffe3f0', surf: 0.44, fog: [60, 240] },
  { n: 2,  name: 'Romantic City Subway',       top: '#7cc0ff', hor: '#ffe0ea', surf: 0.56, fog: [90, 320], bright: true, exposure: 0.92 },
  { n: 3,  name: 'Sunset Desert Kingdom',      top: '#8a6fd8', hor: '#ffb38a', surf: 0.44, fog: [60, 260], sun: '#ffc48a' },
  { n: 4,  name: 'Snowy Fairytale Railway',    top: '#2a2470', hor: '#8a6ac8', surf: 0.56, night: true, fog: [60, 240], bright: true, exposure: 0.85 },
  { n: 5,  name: 'Romantic Neon City',         top: '#1a0838', hor: '#8a2a8a', surf: 0.56, night: true, fog: [60, 240], exposure: 0.9 },
  { n: 6,  name: 'Tropical Flower Island',     top: '#4fb4ff', hor: '#e6fbff', surf: 0.32, fog: [70, 260] },
  { n: 7,  name: 'Red Canyon Railway',         top: '#5a3a8a', hor: '#ff9a5a', surf: 0.56, fog: [60, 280], sun: '#ffb070' },
  { n: 8,  name: 'Cherry Blossom Kingdom',     top: '#9ac8ff', hor: '#ffd6ec', surf: 0.44, fog: [80, 280], bright: true, exposure: 0.9 },
  { n: 9,  name: 'Magical Underwater Railway', top: '#0a3a8a', hor: '#3ab8f0', surf: 0.56, fog: [30, 150], sun: '#c8f0ff', exposure: 0.95 },
  { n: 10, name: 'Heavenly Sky Temple',        top: '#7ab4ff', hor: '#ffe6f4', surf: 0.44, fog: [90, 320], bright: true, exposure: 0.85 },
];
// Power-up models that exist in glb/ but are not listed in the manifests
const EXTRA_POWERUPS = { 4: ['sf_powerup_snowflake'], 5: ['rn_powerup_bolt'], 9: ['mu_powerup_shell'], 10: ['hs_powerup_wings'] };

const DUR = { magnet: 12, jetpack: 8, sneakers: 12, mult: 15, board: 30, shield: 15, boost: 5, slowmo: 6 };
const BASE_POWERS = {
  magnet:   { icon: '🧲', name: 'COIN MAGNET!',    color: '#ff4757', w: 24 },
  jetpack:  { icon: '🚀', name: 'JETPACK!',        color: '#ffa502', w: 13 },
  sneakers: { icon: '👟', name: 'SUPER SNEAKERS!', color: '#2ed573', w: 18 },
  mult:     { icon: '2X', name: 'SCORE x2!',       color: '#1e90ff', w: 17 },
  board:    { icon: '🛹', name: 'HOVERBOARD!',     color: '#e056fd', w: 13 },
  heart:    { icon: '💖', name: 'EXTRA LIFE!',     color: '#ff6b9d', w: 11 },
  shield:   { icon: '🛡️', name: 'SHIELD!',         color: '#48dbfb', w: 15, mapOnly: true },
  boost:    { icon: '⚡', name: 'SPEED BOOST!',    color: '#feca57', w: 13, mapOnly: true },
  slowmo:   { icon: '❄️', name: 'SLOW-MO!',        color: '#c8d6e5', w: 13, mapOnly: true },
};
// Which model keyword drives which power-up (plus label overrides)
const MODEL_POWERS = [
  { key: 'magnet', power: 'magnet' },
  { key: 'heart', power: 'heart' },
  { key: 'wings', power: 'jetpack', icon: '🕊️', name: 'ANGEL WINGS!' },
  { key: 'shell', power: 'mult', icon: '🐚', name: 'PEARL SCORE x2!' },
  { key: 'shield', power: 'shield' },
  { key: 'bubble', power: 'shield', icon: '🫧', name: 'BUBBLE SHIELD!' },
  { key: 'bolt', power: 'boost' },
  { key: 'flame', power: 'boost', icon: '🔥', name: 'FIRE BOOST!' },
  { key: 'snowflake', power: 'slowmo' },
];

// ======================================================================
// Utils
// ======================================================================
const rand = (a, b) => a + Math.random() * (b - a);
const randInt = (a, b) => Math.floor(rand(a, b + 1));
const pick = (a) => a[Math.floor(Math.random() * a.length)];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const damp = (k, dt) => Math.min(1, k * dt);
const Y_AXIS = new THREE.Vector3(0, 1, 0);

const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } },
};

// ======================================================================
// Audio (tiny synth, no assets)
// ======================================================================
let actx = null;
let muted = store.get('rr_muted', false);
function initAudio() {
  if (!actx) { try { actx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { actx = null; } }
  if (actx && actx.state === 'suspended') actx.resume();
}
function tone(f, dur, type, vol, f2, delay) {
  if (muted || !actx) return;
  const t = actx.currentTime + (delay || 0);
  const o = actx.createOscillator(), g = actx.createGain();
  o.type = type || 'square';
  o.frequency.setValueAtTime(f, t);
  if (f2) o.frequency.exponentialRampToValueAtTime(f2, t + dur);
  g.gain.setValueAtTime(vol || 0.05, t);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g); g.connect(actx.destination);
  o.start(t); o.stop(t + dur + 0.02);
}
let lastCoinSfx = 0;
const sfx = {
  coin() {
    const now = performance.now();
    if (now - lastCoinSfx < 45) return;
    lastCoinSfx = now;
    tone(1046, 0.06, 'square', 0.03); tone(1568, 0.1, 'square', 0.03, null, 0.05);
  },
  jump() { tone(320, 0.18, 'triangle', 0.08, 720); },
  bigJump() { tone(260, 0.3, 'triangle', 0.09, 1000); },
  roll() { tone(260, 0.15, 'sawtooth', 0.035, 110); },
  lane() { tone(520, 0.05, 'sine', 0.03, 680); },
  power() { [523, 659, 784, 1046].forEach((f, i) => tone(f, 0.12, 'square', 0.045, null, i * 0.07)); },
  stumble() { tone(200, 0.25, 'sawtooth', 0.08, 90); },
  crash() { tone(130, 0.5, 'sawtooth', 0.12, 40); tone(80, 0.6, 'square', 0.07, 30); },
  shield() { tone(900, 0.35, 'triangle', 0.09, 180); tone(300, 0.3, 'sawtooth', 0.05, 80, 0.05); },
  smash() { tone(160, 0.25, 'square', 0.07, 50); },
  jet() { tone(110, 0.6, 'sawtooth', 0.05, 300); },
  end() { tone(440, 0.2, 'triangle', 0.05, 220); },
};

// ======================================================================
// Renderer / scene / post
// ======================================================================
let quality = store.get('rr_quality', 'high');
const canvas = $('game');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(64, 1, 0.1, 900);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

const hemi = new THREE.HemisphereLight(0xffffff, 0x445533, 1.0);
const sun = new THREE.DirectionalLight(0xffffff, 2.4);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -26, right: 26, top: 45, bottom: -45, near: 1, far: 160 });
sun.shadow.bias = -0.0006;
scene.add(hemi, sun, sun.target);

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(256, 256), 0.25, 0.35, 0.92);
composer.addPass(bloom);
composer.addPass(new OutputPass());

function applyQuality() {
  const high = quality === 'high';
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, high ? 1.75 : 1));
  renderer.shadowMap.enabled = high;
  scene.traverse((o) => {
    if (!o.material) return;
    (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => { m.needsUpdate = true; });
  });
  $('qualityBtn').textContent = 'QUALITY: ' + (high ? 'HIGH' : 'LOW');
  resize();
  applyGlow();
}

function resize() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setSize(w, h, false);
  composer.setPixelRatio(renderer.getPixelRatio());
  composer.setSize(w, h);
  camera.aspect = w / h;
  camera.fov = w / h < 0.8 ? 80 : 64;   // portrait screens: keep all lanes in view
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);

function skyTexture(top, hor) {
  const c = document.createElement('canvas'); c.width = 2; c.height = 512;
  const g = c.getContext('2d'); const gr = g.createLinearGradient(0, 0, 0, 512);
  gr.addColorStop(0, top); gr.addColorStop(0.55, hor); gr.addColorStop(1, hor);
  g.fillStyle = gr; g.fillRect(0, 0, 2, 512);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
scene.background = skyTexture(MAPS[0].top, MAPS[0].hor);

// Exported Blender materials: calmer reflections and capped glow (same treatment as the preview)
let tamed = [];
function tameMaterial(mt) {
  if (!mt || mt.userData.tamed) return;
  mt.userData.tamed = true;
  if ('metalness' in mt) {
    mt.metalness = Math.min(mt.metalness, 0.55);
    mt.roughness = Math.max(mt.roughness, mt.metalness > 0.3 ? 0.4 : 0.3);
    mt.envMapIntensity = mt.metalness > 0.3 ? 0.25 : 0.15;
  }
  if (mt.emissive && (mt.emissive.r + mt.emissive.g + mt.emissive.b) > 0) {
    mt.userData.baseGlow = Math.min(mt.emissiveIntensity, 2.0);
    tamed.push(mt);
  }
}
function applyGlow() {
  const on = quality === 'high';
  const night = theme && theme.info.night;
  const nightCut = night ? 0.7 : 1.0;
  for (const mt of tamed) mt.emissiveIntensity = mt.userData.baseGlow * nightCut * (on ? 1 : 0.6);
  bloom.enabled = on;
  bloom.strength = night ? 0.35 : 0.22;
  bloom.threshold = night ? 0.82 : 0.92;
  bloom.radius = 0.35;
}

// ======================================================================
// Procedural textures & small shared meshes
// ======================================================================
function canvasTex(w, h, draw) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
const MAT = {};
function std(color, opts) {
  const key = color + '|' + JSON.stringify(opts || {});
  if (!MAT[key]) MAT[key] = new THREE.MeshStandardMaterial(Object.assign({ color, roughness: 0.6 }, opts || {}));
  return MAT[key];
}
function basic(color) {
  const key = 'b' + color;
  if (!MAT[key]) MAT[key] = new THREE.MeshBasicMaterial({ color });
  return MAT[key];
}
const particleGeo = new THREE.BoxGeometry(0.18, 0.18, 0.18);

function boxMesh(w, h, d, mat) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.castShadow = true;
  return m;
}

// Humanoid rig shared by the runner and the guard
function makeHumanoid(c) {
  const root = new THREE.Group();
  const rig = new THREE.Group();
  root.add(rig);
  const skin = std(0xf1c27d);
  const torso = boxMesh(0.74, 0.8, 0.42, std(c.shirt)); torso.position.y = 1.18;
  const head = boxMesh(0.5, 0.5, 0.5, skin); head.position.y = 1.86;
  const hat = boxMesh(0.55, 0.18, 0.56, std(c.hat)); hat.position.y = 2.18;
  const brim = boxMesh(0.46, 0.05, 0.3, std(c.hat)); brim.position.set(0, 2.11, c.brimZ);
  rig.add(torso, head, hat, brim);
  const limbs = {};
  for (const [name, x] of [['armL', -0.48], ['armR', 0.48]]) {
    const pivot = new THREE.Group(); pivot.position.set(x, 1.54, 0);
    const arm = boxMesh(0.2, 0.68, 0.2, std(c.shirt)); arm.position.y = -0.31;
    const hand = boxMesh(0.18, 0.16, 0.18, skin); hand.position.y = -0.72;
    pivot.add(arm, hand); rig.add(pivot); limbs[name] = pivot;
  }
  const shoeMat = new THREE.MeshStandardMaterial({ color: c.shoe, roughness: 0.5 });
  for (const [name, x] of [['legL', -0.18], ['legR', 0.18]]) {
    const pivot = new THREE.Group(); pivot.position.set(x, 0.78, 0);
    const leg = boxMesh(0.28, 0.66, 0.3, std(c.pants)); leg.position.y = -0.33;
    const shoe = boxMesh(0.32, 0.15, 0.46, shoeMat); shoe.position.set(0, -0.7, -0.06);
    pivot.add(leg, shoe); rig.add(pivot); limbs[name] = pivot;
  }
  return { root, rig, limbs, shoeMat };
}
function animateRun(h, phase, amp) {
  const s = Math.sin(phase) * amp;
  h.limbs.legL.rotation.x = s; h.limbs.legR.rotation.x = -s;
  h.limbs.armL.rotation.x = -s * 0.9; h.limbs.armR.rotation.x = s * 0.9;
}

// ---------- Player ----------
const hero = makeHumanoid({ shirt: 0xff5a36, pants: 0x2b4c9b, hat: 0x1e90ff, shoe: 0xffffff, brimZ: 0.38 });
const backpack = boxMesh(0.56, 0.58, 0.24, std(0xffd32a));
backpack.position.set(0, 1.22, 0.31);
hero.rig.add(backpack);

const jetpackModel = new THREE.Group();
for (const s of [-0.21, 0.21]) {
  const tank = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.85, 12), std(0xc0c6cc, { metalness: 0.5, roughness: 0.35 }));
  tank.position.set(s, 1.28, 0.52);
  const flame = new THREE.Mesh(new THREE.ConeGeometry(0.15, 0.65, 10), basic(0xff8c1a));
  flame.rotation.x = Math.PI;
  flame.position.set(s, 0.5, 0.52);
  flame.name = 'flame';
  jetpackModel.add(tank, flame);
}
jetpackModel.visible = false;
hero.rig.add(jetpackModel);
const wingsHolder = new THREE.Group();   // filled with the map's wings model when it has one
wingsHolder.position.set(0, 1.35, 0.45);
wingsHolder.visible = false;
hero.rig.add(wingsHolder);

const boardModel = new THREE.Group();
const deck = boxMesh(0.9, 0.12, 2.0, std(0xe056fd, { emissive: 0x3a0a44 }));
const glow = new THREE.Mesh(new THREE.BoxGeometry(0.66, 0.04, 1.7), basic(0x7efff5));
glow.position.y = -0.09;
boardModel.add(deck, glow);
boardModel.position.y = 0.06;
boardModel.visible = false;
hero.root.add(boardModel);

const bubble = new THREE.Mesh(new THREE.SphereGeometry(1.25, 24, 16),
  new THREE.MeshStandardMaterial({ color: 0x9be7ff, emissive: 0x2a8cff, emissiveIntensity: 0.4, transparent: true, opacity: 0.28, depthWrite: false }));
bubble.position.y = 0.95;
bubble.visible = false;
hero.root.add(bubble);
scene.add(hero.root);

// ---------- Guard (chaser) ----------
const guard = makeHumanoid({ shirt: 0x34495e, pants: 0x2c3e50, hat: 0x1b2631, shoe: 0x111111, brimZ: -0.38 });
scene.add(guard.root);

// ======================================================================
// Map loading → theme
// ======================================================================
const loader = new GLTFLoader();
let theme = null;

async function getJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url} (${r.status})`);
  return r.json();
}

function makeAsset(gltf, kind) {
  const root = gltf.scene;
  root.updateMatrixWorld(true);
  const parts = [];
  root.traverse((o) => {
    if (!o.isMesh) return;
    (Array.isArray(o.material) ? o.material : [o.material]).forEach(tameMaterial);
    o.castShadow = true; o.receiveShadow = true;
    parts.push({ geometry: o.geometry, material: o.material, matrix: o.matrixWorld.clone() });
  });
  return { root, parts, kind, box: new THREE.Box3().setFromObject(root) };
}

function disposeTheme(t) {
  if (!t) return;
  const seen = new Set();
  for (const name in t.assets) {
    t.assets[name].root.traverse((o) => {
      if (!o.isMesh) return;
      o.geometry.dispose();
      (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => {
        if (seen.has(m)) return;
        seen.add(m);
        for (const k in m) if (m[k] && m[k].isTexture) m[k].dispose();
        m.dispose();
      });
    });
  }
}

async function loadTheme(n, onProgress) {
  const info = MAPS[n - 1];
  const base = `${MODELS}/map${n}/`;
  const [manifest, level] = await Promise.all([
    getJSON(base + 'manifest.json'),
    getJSON(`${MODELS}/sample_map${n}/level.json`),
  ]);
  const kinds = {};
  manifest.assets.forEach((a) => { kinds[a.name] = a.kind; });
  (EXTRA_POWERUPS[n] || []).forEach((a) => { kinds[a] = 'powerup'; });
  level.placements.forEach((p) => { if (!kinds[p.asset]) kinds[p.asset] = p.kind; });

  // Load every GLB with a few requests in flight at once
  const names = Object.keys(kinds);
  const assets = {};
  let done = 0;
  const queue = names.slice();
  const worker = async () => {
    while (queue.length) {
      const name = queue.shift();
      try {
        const gltf = await loader.loadAsync(`${base}glb/${name}.glb`);
        assets[name] = makeAsset(gltf, kinds[name]);
      } catch (e) {
        console.warn('Could not load', name, e);
      }
      done++;
      onProgress(done / names.length, name);
    }
  };
  await Promise.all(Array.from({ length: 6 }, worker));

  const byKind = (k) => names.filter((nm) => kinds[nm] === k && assets[nm]);
  const t = {
    n, info, surf: info.surf, assets,
    lows: byKind('obstacle_low'),
    highs: byKind('obstacle_high'),
    train: byKind('obstacle_train')[0] || null,
    ramp: byKind('ramp')[0] || null,
    coin: manifest.coin && assets[manifest.coin] ? manifest.coin : byKind('coin')[0],
    powers: {},
    chunks: Array.from({ length: NCHUNK }, () => new Map()),
  };
  if (!t.train || !t.ramp) { t.train = null; t.ramp = null; }
  if (!t.lows.length || !t.highs.length || !t.coin) throw new Error('This map is missing obstacle or coin models.');

  // Power-ups: base set + anything the map has a model for (model replaces the icon)
  for (const k in BASE_POWERS) if (!BASE_POWERS[k].mapOnly) t.powers[k] = Object.assign({ model: null }, BASE_POWERS[k]);
  for (const nm of byKind('powerup')) {
    const mp = MODEL_POWERS.find((m) => nm.includes(m.key));
    if (!mp) continue;
    t.powers[mp.power] = Object.assign({}, BASE_POWERS[mp.power], t.powers[mp.power] || {},
      { model: nm }, mp.icon ? { icon: mp.icon } : {}, mp.name ? { name: mp.name } : {});
  }

  // Scenery template: the sample level's decoration, cut into 50 m chunks of one 300 m period
  const q = new THREE.Quaternion(), s = new THREE.Vector3(), v = new THREE.Vector3();
  for (const p of level.placements) {
    if (!DECOR_KINDS.has(p.kind) || !assets[p.asset]) continue;
    const yb = p.pos[1];
    if (yb < 0 || yb >= PERIOD) continue;
    const c = Math.floor(yb / CHUNK);
    q.setFromAxisAngle(Y_AXIS, (p.rot_z_deg || 0) * Math.PI / 180);
    s.setScalar(p.scale || 1);
    v.set(p.pos[0], p.pos[2] - info.surf, -(yb - c * CHUNK));
    const m = new THREE.Matrix4().compose(v, q, s);
    const list = t.chunks[c].get(p.asset) || [];
    list.push(m);
    t.chunks[c].set(p.asset, list);
  }
  return t;
}

// ======================================================================
// Scenery chunks (GPU-instanced)
// ======================================================================
const liveChunks = new Map();
const tmpM = new THREE.Matrix4();
function buildChunk(g) {
  const c = ((g % NCHUNK) + NCHUNK) % NCHUNK;
  const group = new THREE.Group();
  group.position.z = -g * CHUNK;
  for (const [name, mats] of theme.chunks[c]) {
    const a = theme.assets[name];
    const cast = a.kind !== 'segment' && a.kind !== 'backdrop';
    for (const part of a.parts) {
      const im = new THREE.InstancedMesh(part.geometry, part.material, mats.length);
      for (let i = 0; i < mats.length; i++) im.setMatrixAt(i, tmpM.multiplyMatrices(mats[i], part.matrix));
      im.castShadow = cast;
      im.receiveShadow = true;
      im.computeBoundingSphere();
      group.add(im);
    }
  }
  scene.add(group);
  return group;
}
function updateChunks(force) {
  if (!theme) return;
  const d = -player.z;
  const g0 = Math.floor((d - 30) / CHUNK);
  const g1 = Math.floor((d + Math.min(theme.info.fog[1], 330) + 20) / CHUNK);
  for (const [g, grp] of liveChunks) {
    if (force || g < g0 || g > g1) {
      grp.children.forEach((im) => im.dispose());
      scene.remove(grp);
      liveChunks.delete(g);
    }
  }
  for (let g = g0; g <= g1; g++) if (!liveChunks.has(g)) liveChunks.set(g, buildChunk(g));
}

// ======================================================================
// Coins (one instanced mesh per coin sub-mesh)
// ======================================================================
let coinMeshes = [];
const coins = [];
function setupCoinMeshes() {
  coinMeshes.forEach((c) => { scene.remove(c.im); c.im.dispose(); });
  coinMeshes = theme.assets[theme.coin].parts.map((part) => {
    const im = new THREE.InstancedMesh(part.geometry, part.material, COIN_CAP);
    im.count = 0;
    im.frustumCulled = false;
    im.castShadow = false;
    scene.add(im);
    return { im, matrix: part.matrix };
  });
}
const coinQ = new THREE.Quaternion(), coinS = new THREE.Vector3(1, 1, 1), coinM = new THREE.Matrix4();
function syncCoins(t) {
  coinQ.setFromAxisAngle(Y_AXIS, t * 3);
  const n = Math.min(coins.length, COIN_CAP);
  for (let i = 0; i < n; i++) {
    coinM.compose(coins[i].pos, coinQ, coinS);
    for (const cm of coinMeshes) cm.im.setMatrixAt(i, tmpM.multiplyMatrices(coinM, cm.matrix));
  }
  for (const cm of coinMeshes) { cm.im.count = n; cm.im.instanceMatrix.needsUpdate = true; }
}

// ======================================================================
// Game state
// ======================================================================
const player = {};
const state = { mode: 'menu', power: {}, time: 0, guardUntil: 0, speed: BASE_SPEED };
const obstacles = [], powerups = [], particles = [];
const gen = { busy: [0, 0, 0] };
let best = store.get('rr_best', 0);
let totalCoins = store.get('rr_coins', 0);
let selectedMap = store.get('rr_map', 1);
let shakeT = 0;

function invulnerable() {
  return state.invT > 0 || state.power.boost > 0 || state.power.jetpack > 0;
}

function clearWorld() {
  for (const o of obstacles) scene.remove(o.mesh);
  for (const p of powerups) scene.remove(p.mesh);
  for (const p of particles) scene.remove(p.mesh);
  obstacles.length = 0; powerups.length = 0; particles.length = 0; coins.length = 0;
}

function resetGame() {
  clearWorld();
  Object.assign(player, {
    lane: 1, fromLane: 1, x: 0, y: 0, z: 0, vy: 0,
    grounded: true, coyote: 0, jumpBuf: 0, rolling: false, rollT: 0, anim: 0,
  });
  Object.assign(state, {
    time: 0, speed: BASE_SPEED, dist: 0, score: 0, coins: 0, lives: 0,
    stumbleT: -99, guardUntil: 2.5, invT: 0, dieT: 0, deathReason: '',
    power: { magnet: 0, jetpack: 0, sneakers: 0, mult: 0, board: 0, shield: 0, boost: 0, slowmo: 0 },
  });
  gen.d = 40; gen.safe = 1; gen.busy = [0, 0, 0]; gen.nextPower = rand(90, 150);
  guard.dist = 3;
  hero.rig.rotation.set(0, 0, 0);
  hero.rig.scale.set(1, 1, 1);
  hero.shoeMat.color.set(0xffffff);
  jetpackModel.visible = false;
  wingsHolder.visible = false;
  boardModel.visible = false;
  bubble.visible = false;
  camera.position.set(0, 5.2, 8.5);
  updateChunks(true);
  generateWorld();
  updateHUD(true);
}

// ======================================================================
// Procedural generation
// ======================================================================
// Fairness rules:
//  * A "safe lane" only holds passable things (barriers, ramped trains).
//  * Any lane-blocking obstacle needs an adjacent lane that is open at that point and stays
//    reserved for that row, so the player can always dodge.
//  * Row spacing scales with speed so reaction time stays constant.

function addCoin(x, y, z) {
  if (coins.length < COIN_CAP) coins.push({ pos: new THREE.Vector3(x, y, z), attracted: false });
}
function coinLine(l, d0, d1, y) {
  for (let d = d0; d <= d1; d += 2.3) addCoin(LANES[l], y, -d);
}
function coinArc(l, dc, half, y, peak) {
  for (let d = dc - half; d <= dc + half + 0.01; d += 1.5) {
    const t = (d - dc) / half;
    addCoin(LANES[l], y + peak * (1 - t * t), -d);
  }
}

function cloneAsset(name) {
  const m = theme.assets[name].root.clone();
  return m;
}

function addObstacle(o) {
  o.x = LANES[o.lane];
  o.mesh.position.x = o.x;
  scene.add(o.mesh);
  obstacles.push(o);
  return o;
}

function obstacleDims(name) {
  const b = theme.assets[name].box;
  return { hw: Math.min(BARRIER_HW, (b.max.x - b.min.x) / 2), zMax: b.max.z, zMin: b.min.z, top: b.max.y };
}

function placeBarrier(type, l, d) {
  const name = pick(type === 'low' ? theme.lows : theme.highs);
  const dims = obstacleDims(name);
  const mesh = cloneAsset(name);
  mesh.position.set(0, -0.02, -d);
  addObstacle({
    type, lane: l, hw: dims.hw, zNear: -d + dims.zMax, zFar: -d + dims.zMin, mesh, vz: 0,
    h: Math.min(dims.top, LOW_MAX), y0: HIGH_Y0, y1: dims.top,
  });
  gen.busy[l] = d + 3;
  if (type === 'low' && Math.random() < 0.55) coinArc(l, d, 4.5, COIN_Y, 2.0);
  if (type === 'high' && Math.random() < 0.5) coinLine(l, d - 3, d + 3, 0.5);
}

// Lane-blocking wall for maps without trains: a low obstacle under a high one
function placeBlock(l, d) {
  const lo = pick(theme.lows), hi = pick(theme.highs);
  const a = obstacleDims(lo), b = obstacleDims(hi);
  const mesh = new THREE.Group();
  const m1 = cloneAsset(lo), m2 = cloneAsset(hi);
  m1.position.y = m2.position.y = -0.02;
  mesh.add(m1, m2);
  mesh.position.z = -d;
  addObstacle({
    type: 'block', lane: l, hw: BARRIER_HW, zNear: -d + Math.max(a.zMax, b.zMax), zFar: -d + Math.min(a.zMin, b.zMin),
    mesh, vz: 0, y1: Math.max(b.top, a.top),
  });
  gen.busy[l] = d + 4;
}

function makeTrainMesh(cars, moving) {
  const g = new THREE.Group();
  for (let k = 0; k < cars; k++) {
    const car = cloneAsset(theme.train);
    car.position.set(0, MODEL_Y, -(TRAIN_FRONT + k * CAR_STEP));
    g.add(car);
  }
  if (moving) {
    const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.22, 12, 8), basic(0xff2020));
    beacon.position.set(0, TRAIN_H - 0.3, 0.1);
    beacon.name = 'beacon';
    g.add(beacon);
  }
  return g;
}
const trainLen = (cars) => CAR_LEN + (cars - 1) * CAR_STEP;

function placeTrain(l, d, ramp, diff) {
  const cars = randInt(1, diff > 0.35 ? 3 : 2);
  const len = trainLen(cars);
  let front = d;
  if (ramp) {
    const r = new THREE.Group();
    const rm = cloneAsset(theme.ramp);
    rm.position.set(0, MODEL_Y, -RAMP_LEN / 2);
    r.add(rm);
    r.position.z = -d;
    addObstacle({ type: 'ramp', lane: l, hw: RAMP_HW, zNear: -d, zFar: -d - RAMP_LEN, mesh: r, vz: 0 });
    front = d + RAMP_TO_TRAIN;
  }
  const t = makeTrainMesh(cars, false);
  t.position.z = -front;
  addObstacle({ type: 'train', lane: l, hw: TRAIN_HW, zNear: -front, zFar: -front - len, mesh: t, vz: 0, ramped: ramp });
  if (ramp && Math.random() < 0.75) {
    for (let s = 0.5; s < RAMP_LEN; s += 1.6) addCoin(LANES[l], (s / RAMP_LEN) * RAMP_TOP + COIN_Y, -(d + s));
    coinLine(l, d + RAMP_LEN + 0.5, front + len - 1.5, TRAIN_H + COIN_Y);
  } else if (!ramp && Math.random() < 0.25) {
    coinLine(l, front + 2, front + len - 2, TRAIN_H + COIN_Y);
  }
  gen.busy[l] = front + len + Math.max(10, state.speed * 0.7);
}

function placeMovingTrain(l, d) {
  const cars = randInt(1, 2);
  const len = trainLen(cars);
  const vz = rand(7, 12);
  // Spawn so it meets the player around distance d
  const t = Math.max(0, (d - (-player.z)) / state.speed);
  const zNear = -d - vz * t;
  const mesh = makeTrainMesh(cars, true);
  mesh.position.z = zNear;
  addObstacle({ type: 'train', lane: l, hw: TRAIN_HW, zNear, zFar: zNear - len, mesh, vz, moving: true });
  gen.busy[l] = d + vz * t + len + 15;
}

const powerTexCache = {};
function powerSpriteTex(type) {
  const info = theme.powers[type];
  const key = type + info.icon;
  if (powerTexCache[key]) return powerTexCache[key];
  return (powerTexCache[key] = canvasTex(128, 128, (g) => {
    const grd = g.createRadialGradient(54, 50, 10, 64, 64, 60);
    grd.addColorStop(0, '#ffffff'); grd.addColorStop(0.35, info.color); grd.addColorStop(1, 'rgba(0,0,0,0.5)');
    g.fillStyle = grd; g.beginPath(); g.arc(64, 64, 58, 0, Math.PI * 2); g.fill();
    g.lineWidth = 6; g.strokeStyle = '#fff'; g.stroke();
    g.textAlign = 'center'; g.textBaseline = 'middle';
    if (info.icon === '2X') { g.font = 'bold 56px Arial Black, Arial'; g.fillStyle = '#fff'; g.fillText('2X', 64, 68); }
    else { g.font = '60px "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif'; g.fillText(info.icon, 64, 70); }
  }));
}
function placePowerup(type, l, d) {
  const info = theme.powers[type];
  const g = new THREE.Group();
  if (info.model) {
    const m = cloneAsset(info.model);
    m.name = 'spin';
    g.add(m);
  } else {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: powerSpriteTex(type) }));
    sp.scale.set(1.4, 1.4, 1);
    g.add(sp);
  }
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.95, 0.06, 8, 32), basic(new THREE.Color(info.color).getHex()));
  ring.name = 'ring';
  g.add(ring);
  g.position.set(LANES[l], POWER_Y, -d);
  scene.add(g);
  powerups.push({ mesh: g, type, baseY: POWER_Y });
}

function randomPowerType() {
  const keys = Object.keys(theme.powers);
  let total = 0;
  for (const k of keys) total += theme.powers[k].w;
  let r = Math.random() * total;
  for (const k of keys) { r -= theme.powers[k].w; if (r <= 0) return k; }
  return 'magnet';
}

function genRow() {
  const d = gen.d;
  const diff = clamp((d - 40) / 2200, 0, 1);
  const v = state.speed;
  const spacing = rand(Math.max(15, v * 0.85), Math.max(24, v * 1.25));
  const trains = !!theme.train;

  // Occasionally move the safe lane to a neighbour (both must be clear here)
  let newSafe = gen.safe;
  if (Math.random() < 0.2 && gen.busy[gen.safe] <= d) {
    const c = [gen.safe - 1, gen.safe + 1].filter((l) => l >= 0 && l < 3 && gen.busy[l] <= d);
    if (c.length) newSafe = pick(c);
  }
  const switching = newSafe !== gen.safe;

  const reserved = [false, false, false];
  const empty = [];
  const order = [gen.safe].concat([0, 1, 2].filter((l) => l !== gen.safe).sort(() => Math.random() - 0.5));

  const canBlock = (l) => {
    for (const a of [l - 1, l + 1]) {
      if (a < 0 || a > 2) continue;
      if ((gen.busy[a] <= d && !reserved[a]) || reserved[a] === 'open') { reserved[a] = 'open'; return true; }
    }
    return false;
  };

  for (const l of order) {
    if (gen.busy[l] > d) continue;
    if (switching && (l === gen.safe || l === newSafe)) { empty.push(l); reserved[l] = 'open'; continue; }
    const safeLike = l === gen.safe || reserved[l] === 'open';
    const r = Math.random();
    if (safeLike) {
      if (r < 0.38) empty.push(l);
      else if (r < 0.58) placeBarrier('low', l, d);
      else if (r < 0.78 || !trains) placeBarrier(r < 0.88 || !trains ? 'high' : 'low', l, d);
      else placeTrain(l, d, true, diff);
      if (l === gen.safe && gen.busy[l] <= d + 3) reserved[l] = 'open';
    } else {
      const pEmpty = 0.42 - 0.2 * diff;
      if (r < pEmpty) empty.push(l);
      else if (r < pEmpty + 0.14) placeBarrier('low', l, d);
      else if (r < pEmpty + 0.28) placeBarrier('high', l, d);
      else if (trains && Math.random() < 0.35) placeTrain(l, d, true, diff);
      else if (canBlock(l)) {
        if (!trains) placeBlock(l, d);
        else if (diff > 0.08 && Math.random() < 0.12 + 0.18 * diff) placeMovingTrain(l, d);
        else placeTrain(l, d, false, diff);
        reserved[l] = 'blocked';
      } else if (trains) placeTrain(l, d, true, diff);
      else placeBarrier(Math.random() < 0.5 ? 'low' : 'high', l, d);
    }
  }

  // Coins & power-ups in free lanes
  const coinFree = [];
  for (const l of empty) {
    if (Math.random() < (l === gen.safe ? 0.6 : 0.3)) coinLine(l, d + 1, d + spacing - 5, COIN_Y);
    else coinFree.push(l);
  }
  if (d >= gen.nextPower && coinFree.length) {
    placePowerup(randomPowerType(), pick(coinFree), d + spacing * 0.5);
    gen.nextPower = d + rand(220, 400);
  }

  gen.safe = newSafe;
  gen.d = d + spacing;
}

function generateWorld() {
  const front = -player.z + AHEAD;
  while (gen.d < front) genRow();
}

// ======================================================================
// Particles & feedback
// ======================================================================
function burst(x, y, z, color, n, spd, size) {
  for (let i = 0; i < n; i++) {
    const m = new THREE.Mesh(particleGeo, basic(color));
    m.position.set(x, y, z);
    m.scale.setScalar(size || 1);
    scene.add(m);
    particles.push({
      mesh: m, life: rand(0.4, 0.8),
      v: new THREE.Vector3(rand(-1, 1) * spd, rand(0.3, 1.2) * spd, rand(-1, 1) * spd),
    });
  }
}

let toastTimer = 0;
function toast(text, color) {
  const el = $('toast');
  el.textContent = text;
  el.style.color = color || '#fff';
  el.classList.remove('show');
  void el.offsetWidth; // restart animation
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 1500);
}

// ======================================================================
// Player actions
// ======================================================================
function moveLane(dir) {
  if (state.mode !== 'play') return;
  const nl = player.lane + dir;
  if (nl < 0 || nl > 2) return;
  player.fromLane = player.lane;
  player.lane = nl;
  sfx.lane();
}
function jump() {
  if (state.mode !== 'play' || state.power.jetpack > 0) return;
  if (player.grounded || player.coyote > 0) {
    const big = state.power.sneakers > 0;
    player.vy = big ? SNEAKER_JUMP_V : JUMP_V;
    player.grounded = false; player.coyote = 0; player.jumpBuf = 0;
    player.rolling = false; player.rollT = 0;
    big ? sfx.bigJump() : sfx.jump();
  } else {
    player.jumpBuf = 0.15;
  }
}
function roll() {
  if (state.mode !== 'play' || state.power.jetpack > 0) return;
  if (!player.grounded) player.vy = Math.min(player.vy, FAST_FALL_V);
  player.rolling = true;
  player.rollT = ROLL_TIME;
  player.jumpBuf = 0;
  sfx.roll();
}

function activatePower(type) {
  const info = theme.powers[type] || BASE_POWERS[type];
  sfx.power();
  toast(info.name, info.color);
  if (type === 'heart') {
    state.lives = Math.min(MAX_LIVES, state.lives + 1);
    return;
  }
  state.power[type] = DUR[type];
  if (type === 'jetpack') {
    sfx.jet();
    const wings = info.model && wingsHolder.children.length;
    jetpackModel.visible = !wings;
    wingsHolder.visible = !!wings;
    player.rolling = false; player.rollT = 0;
    // Trail of sky coins
    let lane = player.lane, d = -player.z + 18, n = 0;
    const end = -player.z + state.speed * DUR.jetpack * 1.05;
    while (d < end) {
      addCoin(LANES[lane], JET_Y + 0.9, -d);
      d += 2.5;
      if (++n % 9 === 0 && Math.random() < 0.75) lane = clamp(lane + pick([-1, 1]), 0, 2);
    }
  }
  if (type === 'sneakers') hero.shoeMat.color.set(0x39ff14);
  if (type === 'board') boardModel.visible = true;
  if (type === 'shield') bubble.visible = true;
}

function endPower(type) {
  if (type === 'jetpack') {
    jetpackModel.visible = false;
    wingsHolder.visible = false;
    state.invT = Math.max(state.invT, 1.6);
    player.vy = 0;
  }
  if (type === 'boost') state.invT = Math.max(state.invT, 1.0);
  if (type === 'sneakers') hero.shoeMat.color.set(0xffffff);
  if (type === 'board') boardModel.visible = false;
  if (type === 'shield') bubble.visible = false;
  if (state.mode === 'play') sfx.end();
}

function stumble() {
  if (invulnerable()) return;
  sfx.stumble();
  shakeT = 0.25;
  if (state.time - state.stumbleT < STUMBLE_WINDOW) {
    die('caught');
    return;
  }
  state.stumbleT = state.time;
  state.guardUntil = state.time + STUMBLE_WINDOW;
  toast('CAREFUL!', '#ff6b6b');
}

function destroyObstacle(o) {
  const i = obstacles.indexOf(o);
  if (i >= 0) obstacles.splice(i, 1);
  scene.remove(o.mesh);
  burst(player.x, player.y + 1, player.z - 1, o.type === 'train' ? 0xdddddd : 0xffb36b, 18, 9, 1.6);
  sfx.smash();
}

function frontalHit(o) {
  if (invulnerable()) { destroyObstacle(o); return; }
  let saved = '';
  if (state.power.shield > 0) { state.power.shield = 0; endPower('shield'); saved = 'SHIELD SAVED YOU!'; }
  else if (state.power.board > 0) { state.power.board = 0; endPower('board'); saved = 'HOVERBOARD SAVED YOU!'; }
  else if (state.lives > 0) { state.lives--; saved = 'EXTRA LIFE USED!'; }
  if (saved) {
    state.invT = 1.8;
    destroyObstacle(o);
    sfx.shield();
    shakeT = 0.3;
    toast(saved, '#ff9ff3');
    return;
  }
  state.killedBy = o.type + (o.moving ? ' (moving)' : o.ramped ? ' (ramped)' : '');
  die('crash');
}

function die(reason) {
  if (state.mode !== 'play') return;
  state.mode = 'dying';
  state.dieT = 0;
  state.deathReason = reason;
  state.guardUntil = state.time + 99;
  shakeT = 0.5;
  sfx.crash();
  for (const k in state.power) if (state.power[k] > 0) { state.power[k] = 0; endPower(k); }
  updateHUD(true);
}

// ======================================================================
// Physics / collision
// ======================================================================
function rampH(o, z) { return clamp((o.zNear - z) / RAMP_LEN, 0, 1) * RAMP_TOP; }

function groundAt() {
  let g = 0;
  for (const o of obstacles) {
    if (o.type !== 'train' && o.type !== 'ramp') continue;
    if (Math.abs(player.x - o.x) > o.hw + 0.15) continue;
    if (player.z - PLAYER_HD >= o.zNear || player.z + PLAYER_HD <= o.zFar) continue;
    if (o.type === 'train') {
      if (player.y >= TRAIN_H - 0.7) g = Math.max(g, TRAIN_H);
    } else {
      const h = rampH(o, player.z);
      if (player.y >= h - 0.9) g = Math.max(g, h);
    }
  }
  return g;
}

function collide(prevX) {
  if (state.power.jetpack > 0) return;
  const h = player.rolling ? ROLL_H : PLAYER_H;
  for (let i = obstacles.length - 1; i >= 0; i--) {
    const o = obstacles[i];
    if (player.z - PLAYER_HD >= o.zNear || player.z + PLAYER_HD <= o.zFar) continue;
    if (Math.abs(player.x - o.x) >= o.hw + PLAYER_HW) continue;
    const wasBeside = Math.abs(prevX - o.x) >= o.hw + PLAYER_HW;
    let hit = false;
    if (o.type === 'train') hit = player.y < TRAIN_H - 0.7 && (wasBeside || !o.ramped);
    else if (o.type === 'low') hit = player.y < o.h - 0.1;
    else if (o.type === 'high') hit = player.y + h > o.y0 && player.y < o.y1;
    else if (o.type === 'block') hit = player.y < o.y1 - 0.2;
    else if (o.type === 'ramp') hit = player.y < rampH(o, player.z) - 0.9;
    if (!hit) continue;

    if (wasBeside || o.type === 'ramp') {
      // Side impact: bounce back to the lane we came from
      player.lane = player.fromLane;
      player.x = prevX;
      stumble();
    } else {
      frontalHit(o);
    }
    return;
  }
}

// ======================================================================
// Update
// ======================================================================
function effectiveSpeed() {
  return state.speed * (state.power.boost > 0 ? 1.6 : 1) * (state.power.slowmo > 0 ? 0.6 : 1);
}

function updatePlay(dt) {
  state.time += dt;
  state.speed = Math.min(MAX_SPEED, BASE_SPEED + state.dist / 120);
  const v = effectiveSpeed();

  for (const k in state.power) {
    if (state.power[k] > 0) {
      state.power[k] -= dt;
      if (state.power[k] <= 0) { state.power[k] = 0; endPower(k); }
    }
  }
  state.invT = Math.max(0, state.invT - dt);

  // Moving trains
  for (const o of obstacles) if (o.vz) {
    o.zNear += o.vz * dt; o.zFar += o.vz * dt; o.mesh.position.z = o.zNear;
    const b = o.mesh.getObjectByName('beacon');
    if (b) b.visible = Math.floor(state.time * 6) % 2 === 0;
  }

  // Player motion
  const prevX = player.x;
  player.z -= v * dt;
  state.dist = -player.z;
  player.x += (LANES[player.lane] - player.x) * damp(16, dt);
  if (Math.abs(LANES[player.lane] - player.x) < 0.02) player.x = LANES[player.lane];

  if (player.rollT > 0) { player.rollT -= dt; if (player.rollT <= 0) player.rolling = false; }
  player.coyote = Math.max(0, player.coyote - dt);
  player.jumpBuf = Math.max(0, player.jumpBuf - dt);

  if (state.power.jetpack > 0) {
    player.y += (JET_Y - player.y) * damp(3, dt);
    player.vy = 0;
    player.grounded = false;
  } else {
    const wasGrounded = player.grounded;
    player.vy += GRAVITY * dt;
    player.y += player.vy * dt;
    const g = groundAt();
    if (player.y <= g) {
      player.y = g; player.vy = 0; player.grounded = true;
      if (player.jumpBuf > 0) jump();
    } else {
      player.grounded = false;
      if (wasGrounded && player.vy <= 0) player.coyote = 0.1;
    }
  }

  collide(prevX);
  if (state.mode !== 'play') return;

  updateCoins(dt, v);
  updatePowerups(dt);
  if (state.power.boost > 0 && Math.random() < 0.6) burst(player.x, player.y + 0.6, player.z + 0.6, 0xffd166, 1, 2, 0.8);

  state.score += v * dt * 0.6 * (state.power.mult > 0 ? 2 : 1);
  cleanup();
  generateWorld();
  updateChunks(false);
}

function playerCenterY() { return player.y + (player.rolling ? ROLL_H : PLAYER_H) / 2; }

const tmpV = new THREE.Vector3();
function updateCoins(dt, v) {
  const cy = playerCenterY();
  const magnet = state.power.magnet > 0;
  for (let i = coins.length - 1; i >= 0; i--) {
    const c = coins[i], p = c.pos;
    const dz = p.z - player.z;
    if (magnet && !c.attracted && dz > -22 && dz < 2) c.attracted = true;
    let take = false;
    if (c.attracted) {
      tmpV.set(player.x - p.x, cy - p.y, player.z - p.z);
      const dist = tmpV.length();
      const step = (v + 45) * dt;
      if (dist <= step + 0.5) take = true;
      else p.addScaledVector(tmpV, step / dist);
    } else if (Math.abs(p.x - player.x) < 1.0 && Math.abs(p.y - cy) < 1.3 && Math.abs(dz) < 1.0) {
      take = true;
    }
    if (take) {
      state.coins++;
      state.score += 5 * (state.power.mult > 0 ? 2 : 1);
      sfx.coin();
      burst(p.x, p.y, p.z, 0xffe066, 3, 3, 0.6);
      coins.splice(i, 1);
    }
  }
}

function updatePowerups(dt) {
  const cy = playerCenterY();
  for (let i = powerups.length - 1; i >= 0; i--) {
    const pu = powerups[i], p = pu.mesh.position;
    p.y = pu.baseY + Math.sin(state.time * 3 + p.z) * 0.2;
    pu.mesh.getObjectByName('ring').rotation.y += dt * 3;
    const spin = pu.mesh.getObjectByName('spin');
    if (spin) spin.rotation.y += dt * 2;
    if (Math.abs(p.x - player.x) < 1.2 && Math.abs(p.y - cy) < 1.6 && Math.abs(p.z - player.z) < 1.2) {
      burst(p.x, p.y, p.z, new THREE.Color(theme.powers[pu.type].color).getHex(), 14, 6, 1);
      scene.remove(pu.mesh);
      powerups.splice(i, 1);
      activatePower(pu.type);
    }
  }
}

function cleanup() {
  const limit = player.z + BEHIND;
  for (let i = obstacles.length - 1; i >= 0; i--) {
    if (obstacles[i].zFar > limit) { scene.remove(obstacles[i].mesh); obstacles.splice(i, 1); }
  }
  for (let i = coins.length - 1; i >= 0; i--) if (coins[i].pos.z > limit) coins.splice(i, 1);
  for (let i = powerups.length - 1; i >= 0; i--) {
    if (powerups[i].mesh.position.z > limit) { scene.remove(powerups[i].mesh); powerups.splice(i, 1); }
  }
}

function updateParticles(dt) {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.life -= dt;
    p.v.y -= 25 * dt;
    p.mesh.position.addScaledVector(p.v, dt);
    p.mesh.rotation.x += dt * 8;
    if (p.life <= 0) { scene.remove(p.mesh); particles.splice(i, 1); }
  }
}

function updateDying(dt) {
  state.dieT += dt;
  if (state.deathReason === 'crash') {
    hero.rig.rotation.x += (1.45 - hero.rig.rotation.x) * damp(6, dt);
    player.z += Math.max(0, 4 - state.dieT * 8) * dt; // small knock-back
  }
  const g = groundAt();
  if (player.y > g) { player.vy += GRAVITY * dt; player.y = Math.max(g, player.y + player.vy * dt); }
  if (state.dieT > 1.3 && state.mode === 'dying') showGameOver();
}

// ======================================================================
// Visual sync (model, camera, guard)
// ======================================================================
function syncVisuals(dt) {
  const t = performance.now() / 1000;
  const p = player;

  hero.root.position.set(p.x, p.y, p.z);
  hero.root.rotation.z = (LANES[p.lane] - p.x) * -0.07;
  const onBoard = boardModel.visible;
  if (state.mode === 'play') {
    p.anim += dt * effectiveSpeed() * 0.6;
    if (state.power.jetpack > 0) {
      hero.limbs.legL.rotation.x = 0.25; hero.limbs.legR.rotation.x = 0.1;
      hero.limbs.armL.rotation.x = -0.4; hero.limbs.armR.rotation.x = -0.4;
      hero.rig.position.y = Math.sin(t * 5) * 0.1;
      jetpackModel.children.forEach((c) => { if (c.name === 'flame') c.scale.y = rand(0.7, 1.4); });
      wingsHolder.rotation.y = Math.sin(t * 10) * 0.25;
    } else if (!p.grounded) {
      hero.limbs.legL.rotation.x = -0.9; hero.limbs.legR.rotation.x = 0.5;
      hero.limbs.armL.rotation.x = -2.6; hero.limbs.armR.rotation.x = -2.3;
      hero.rig.position.y = onBoard ? 0.15 : 0;
    } else if (onBoard) {
      hero.limbs.legL.rotation.x = 0.3; hero.limbs.legR.rotation.x = -0.3;
      hero.limbs.armL.rotation.x = -0.5 + Math.sin(p.anim) * 0.15; hero.limbs.armR.rotation.x = 0.4;
      hero.rig.position.y = 0.15;
    } else {
      animateRun(hero, p.anim, 1.0);
      hero.rig.position.y = Math.abs(Math.cos(p.anim)) * 0.1;
    }
    const sy = p.rolling ? 0.45 : 1;
    hero.rig.scale.y += (sy - hero.rig.scale.y) * damp(20, dt);
    if (p.rolling) { hero.limbs.legL.rotation.x = -1.4; hero.limbs.legR.rotation.x = -1.4; }
    boardModel.rotation.z = Math.sin(t * 3) * 0.05;
    bubble.scale.setScalar(1 + Math.sin(t * 6) * 0.03);
    hero.rig.visible = state.invT > 0 ? Math.floor(t * 14) % 2 === 0 : true;
  } else if (state.mode === 'menu') {
    hero.rig.visible = true;
    hero.limbs.armL.rotation.x = Math.sin(t * 2) * 0.1;
    hero.limbs.armR.rotation.x = -Math.sin(t * 2) * 0.1;
    hero.limbs.legL.rotation.x = 0; hero.limbs.legR.rotation.x = 0;
    hero.rig.position.y = Math.sin(t * 2) * 0.03;
  } else {
    hero.rig.visible = true;
    hero.rig.scale.y += (1 - hero.rig.scale.y) * damp(10, dt);
  }

  // Guard
  const chasing = state.mode !== 'menu' && state.time < state.guardUntil;
  const caught = state.mode === 'dying' || state.mode === 'over';
  const target = caught ? 1.6 : chasing ? 3.4 : 18;
  guard.dist += (target - guard.dist) * damp(caught ? 3 : 1.5, dt);
  guard.root.visible = guard.dist < 15;
  guard.root.position.set(guard.root.position.x + (p.x - guard.root.position.x) * damp(5, dt), 0, p.z + guard.dist);
  if (state.mode === 'play') animateRun(guard, p.anim * 1.05, 1.0);
  else if (caught) {
    guard.limbs.armL.rotation.x = -1.5; guard.limbs.armR.rotation.x = -1.5;
    guard.limbs.legL.rotation.x = 0; guard.limbs.legR.rotation.x = 0;
  }

  // Sun follows the player for shadows
  sun.position.set(p.x + 25, 60, p.z + 30);
  sun.target.position.set(p.x, 0, p.z - 15);

  // Camera
  const jet = state.power.jetpack > 0;
  const camY = jet ? p.y + 3 : 4.6 + p.y * 0.7;
  camera.position.x += (p.x * 0.75 - camera.position.x) * damp(8, dt);
  camera.position.y += (camY - camera.position.y) * damp(5, dt);
  camera.position.z = p.z + 7.8;
  const lookY = (jet ? p.y : p.y * 0.6) + 1.1;
  camera.lookAt(p.x * 0.55, lookY, p.z - 14);
  if (shakeT > 0) {
    shakeT -= dt;
    camera.position.x += rand(-0.22, 0.22);
    camera.position.y += rand(-0.22, 0.22);
  }
}

// ======================================================================
// HUD
// ======================================================================
let powerEls = {};
function buildPowerHUD() {
  const box = $('powers');
  box.innerHTML = '';
  powerEls = {};
  for (const k in theme.powers) {
    if (k === 'heart') continue;
    const info = theme.powers[k];
    const el = document.createElement('div');
    el.className = 'pw hidden';
    el.style.setProperty('--c', info.color);
    el.innerHTML = `<span class="pw-icon">${info.icon}</span><div class="pw-bar"><div class="pw-fill"></div></div>`;
    box.appendChild(el);
    powerEls[k] = { el, fill: el.querySelector('.pw-fill') };
  }
}
let shownScore = -1, shownCoins = -1, shownLives = -1;
function updateHUD(force) {
  const s = Math.floor(state.score);
  if (force || s !== shownScore) { $('score').textContent = s; shownScore = s; }
  if (force || state.coins !== shownCoins) { $('coins').textContent = state.coins; shownCoins = state.coins; }
  if (force || state.lives !== shownLives) {
    $('lives').textContent = state.lives;
    $('livesPill').classList.toggle('hidden', !state.lives);
    shownLives = state.lives;
  }
  $('multBadge').classList.toggle('hidden', !(state.power.mult > 0));
  for (const k in powerEls) {
    const on = state.power[k] > 0;
    powerEls[k].el.classList.toggle('hidden', !on);
    if (on) powerEls[k].fill.style.width = (100 * state.power[k] / DUR[k]).toFixed(1) + '%';
  }
}

function showOnly(id) {
  for (const o of ['menu', 'pauseOv', 'overOv', 'loadingOv']) $(o).classList.toggle('hidden', o !== id);
  $('hud').classList.toggle('hidden', id === 'menu' || id === 'loadingOv');
}

// ---------- Map select ----------
function buildMenu() {
  const grid = $('mapGrid');
  grid.innerHTML = '';
  for (const m of MAPS) {
    const b = document.createElement('button');
    b.className = 'map-card' + (m.n === selectedMap ? ' sel' : '');
    b.innerHTML = `<img src="${MODELS}/map${m.n}/card.png" alt="" loading="lazy"><span class="num">${m.n}</span><span>${m.name}</span>`;
    b.onclick = () => { selectedMap = m.n; store.set('rr_map', m.n); buildMenu(); };
    b.ondblclick = () => play(m.n);
    grid.appendChild(b);
  }
  $('legend').innerHTML = Object.values(BASE_POWERS).map((p) => `<span>${p.icon} ${p.name.replace('!', '').toLowerCase()}</span>`).join('');
  $('menuBest').textContent = best;
  $('menuCoins').textContent = totalCoins;
}

// ======================================================================
// Game flow
// ======================================================================
let loading = false;
async function play(n) {
  initAudio();
  if (loading) return;
  if (!theme || theme.n !== n) {
    loading = true;
    showOnly('loadingOv');
    $('loadTitle').textContent = 'LOADING MAP ' + n;
    $('loadText').textContent = MAPS[n - 1].name;
    $('progress').firstElementChild.style.width = '0%';
    try {
      const old = theme;
      tamed = [];
      const t = await loadTheme(n, (f, name) => {
        $('progress').firstElementChild.style.width = (f * 100).toFixed(0) + '%';
        $('loadText').textContent = `${MAPS[n - 1].name} · ${name}`;
      });
      clearWorld();
      for (const [g, grp] of liveChunks) { grp.children.forEach((im) => im.dispose()); scene.remove(grp); liveChunks.delete(g); }
      disposeTheme(old);
      theme = t;
      applyTheme();
    } catch (e) {
      console.error(e);
      loading = false;
      showOnly('menu');
      toast('Could not load map ' + n, '#ff6b6b');
      return;
    }
    loading = false;
  }
  startGame();
}

function applyTheme() {
  const m = theme.info;
  scene.background = skyTexture(m.top, m.hor);
  scene.fog = new THREE.Fog(m.hor, m.fog[0], m.fog[1]);
  hemi.color.set(m.night ? 0x7080c0 : m.top);
  hemi.groundColor.set(m.night ? 0x151020 : 0x6b5a40);
  hemi.intensity = m.night ? 0.9 : (m.bright ? 0.85 : 1.1);
  sun.color.set(m.sun || (m.night ? 0x9fb6ff : 0xfff1d6));
  sun.intensity = m.night ? 0.7 : (m.bright ? 1.9 : 2.3);
  renderer.toneMappingExposure = m.exposure || 1.0;
  setupCoinMeshes();
  buildPowerHUD();
  // Wings power-up model doubles as the flying gear on the runner's back
  wingsHolder.clear();
  if (theme.powers.jetpack.model) {
    const w = cloneAsset(theme.powers.jetpack.model);
    w.scale.setScalar(1.3);
    wingsHolder.add(w);
  }
  applyGlow();
}

function startGame() {
  resetGame();
  state.mode = 'play';
  showOnly(null);
  toast(theme.info.name.toUpperCase(), '#ffd32a');
  last = performance.now();
}

function pauseGame() {
  if (state.mode !== 'play') return;
  state.mode = 'paused';
  showOnly('pauseOv');
}
function resumeGame() {
  if (state.mode !== 'paused') return;
  state.mode = 'play';
  showOnly(null);
  last = performance.now();
}
function togglePause() { state.mode === 'play' ? pauseGame() : resumeGame(); }

function showGameOver() {
  state.mode = 'over';
  const score = Math.floor(state.score);
  const isBest = score > best;
  if (isBest) { best = score; store.set('rr_best', best); }
  totalCoins += state.coins;
  store.set('rr_coins', totalCoins);
  $('overTitle').textContent = state.deathReason === 'caught' ? 'CAUGHT!' : 'BUSTED!';
  $('overScore').textContent = score;
  $('overCoins').textContent = state.coins;
  $('overBest').textContent = best;
  $('newBest').classList.toggle('hidden', !isBest);
  showOnly('overOv');
}

function goMenu() {
  if (theme) resetGame();
  state.mode = 'menu';
  buildMenu();
  showOnly('menu');
}

// ======================================================================
// Input
// ======================================================================
window.addEventListener('keydown', (e) => {
  const k = e.key.toLowerCase();
  if (['arrowleft', 'arrowright', 'arrowup', 'arrowdown', ' '].includes(k)) e.preventDefault();
  if (e.repeat) return;
  initAudio();
  if (state.mode === 'play') {
    if (k === 'arrowleft' || k === 'a') moveLane(-1);
    else if (k === 'arrowright' || k === 'd') moveLane(1);
    else if (k === 'arrowup' || k === 'w' || k === ' ') jump();
    else if (k === 'arrowdown' || k === 's') roll();
  }
  if (k === 'p' || k === 'escape') togglePause();
  if (k === 'm') toggleMute();
  if (k === 'enter' && state.mode === 'menu') play(selectedMap);
  if ((k === 'enter' || k === ' ') && state.mode === 'over') startGame();
});

let ptr = null;
canvas.addEventListener('pointerdown', (e) => {
  initAudio();
  ptr = { x: e.clientX, y: e.clientY, done: false };
});
canvas.addEventListener('pointermove', (e) => {
  if (!ptr || ptr.done) return;
  const dx = e.clientX - ptr.x, dy = e.clientY - ptr.y;
  if (Math.max(Math.abs(dx), Math.abs(dy)) < 28) return;
  ptr.done = true;
  if (Math.abs(dx) > Math.abs(dy)) moveLane(dx > 0 ? 1 : -1);
  else if (dy < 0) jump();
  else roll();
});
const endPtr = () => { ptr = null; };
canvas.addEventListener('pointerup', endPtr);
canvas.addEventListener('pointercancel', endPtr);

function toggleMute() {
  muted = !muted;
  store.set('rr_muted', muted);
  $('muteBtn').textContent = muted ? '🔇' : '🔊';
}
$('muteBtn').textContent = muted ? '🔇' : '🔊';

$('playBtn').onclick = () => play(selectedMap);
$('randomBtn').onclick = () => {
  selectedMap = randInt(1, MAPS.length);
  store.set('rr_map', selectedMap);
  buildMenu();
  play(selectedMap);
};
$('qualityBtn').onclick = () => {
  quality = quality === 'high' ? 'low' : 'high';
  store.set('rr_quality', quality);
  applyQuality();
};
$('againBtn').onclick = startGame;
$('restartBtn').onclick = startGame;
$('resumeBtn').onclick = resumeGame;
$('pauseBtn').onclick = togglePause;
$('muteBtn').onclick = toggleMute;
$('menuBtn').onclick = goMenu;
$('overMenuBtn').onclick = goMenu;
window.addEventListener('blur', pauseGame);
document.addEventListener('visibilitychange', () => { if (document.hidden) pauseGame(); });

// ======================================================================
// Main loop
// ======================================================================
let last = performance.now();
function loop(now) {
  requestAnimationFrame(loop);
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;
  if (state.mode === 'play') { updatePlay(dt); updateHUD(); }
  else if (state.mode === 'dying') updateDying(dt);
  if (state.mode !== 'paused') {
    updateParticles(dt);
    if (theme) {
      syncVisuals(dt);
      syncCoins(now / 1000);
    }
  }
  if (bloom.enabled) composer.render(); else renderer.render(scene, camera);
}

// Debug handle (handy from the browser console)
window.__railRush = {
  state, player, obstacles, coins, powerups, activatePower, play, startGame, moveLane, jump, roll,
  get theme() { return theme; },
  renderer,
  // Advance the game logic without rendering (for automated testing)
  simulate(seconds, each) {
    for (let i = 0; i < seconds * 60; i++) {
      if (each) each();
      if (state.mode === 'play') updatePlay(1 / 60);
      else if (state.mode === 'dying') updateDying(1 / 60);
      else break;
    }
  },
};

Object.assign(player, { lane: 1, fromLane: 1, x: 0, y: 0, z: 0, vy: 0, grounded: true, rolling: false, anim: 0 });
camera.position.set(0, 5, 8);
camera.lookAt(0, 1.5, -14);
applyQuality();
buildMenu();
showOnly('menu');
requestAnimationFrame(loop);
