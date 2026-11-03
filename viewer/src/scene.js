import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { planetaryMotion } from './kinematics.js';

const colors = {}

export class RobotViewer {
  constructor(host) {
    this.host = host;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(36, 1, 0.1, 4000);
    this.camera.up.set(0, 0, 1);
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    this.renderer.setClearColor(0x000000, 0);
    this.renderer.domElement.setAttribute('aria-label', 'interactive 3d robot model');
    host.append(this.renderer.domElement);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.minDistance = 20;
    this.controls.maxDistance = 1600;
    this.scene.add(new THREE.HemisphereLight(0xe6efff, 0x526071, 2.7));
    for (const [position, intensity] of [[[60, -90, 160], 3.2], [[-100, 40, 60], 2.0]]) {
      const light = new THREE.DirectionalLight(0xffffff, intensity);
      light.position.set(...position);
      this.scene.add(light);
    }
    this.root = new THREE.Group();
    this.scene.add(this.root);
    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(host);
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    this.view = 'drive';
    this.parts = new Map();
    this.driveGeometries = new Set();
  }

  async load() {
    const [gltf, details, manifest] = await Promise.all([
      new GLTFLoader().loadAsync(`${import.meta.env.BASE_URL}models/ria.glb`),
      new GLTFLoader().loadAsync(`${import.meta.env.BASE_URL}models/drive-details.glb`),
      fetch(`${import.meta.env.BASE_URL}models/manifest.json`).then(r => r.json()),
    ]);
    this.model = gltf.scene;
    this.manifest = manifest;
    this.meshes = new Map();
    this.model.traverse(node => {
      if (node.isMesh && node.userData.side === 'right') this.meshes.set(node.userData.part, node);
      if (node.userData.cadName === 'right_leg/upper_leg') this.leg = node;
    });
    details.scene.traverse(node => {
      if (node.isMesh) this.meshes.set(node.userData.part, node);
    });
    this.setView('drive');
  }

  material(color) {
    return new THREE.MeshStandardMaterial({ color, metalness: 0.18, roughness: 0.48, side: THREE.DoubleSide });
  }

  addPart(key, object, color, label = key.replaceAll('_', ' ')) {
    object.traverse(node => {
      if (!node.isMesh) return;
      node.material = this.material(color);
      node.userData.partKey = key;
    });
    this.parts.set(key, { object, color, label });
    return object;
  }

  driveMesh(name, key, color, offset = new THREE.Vector3()) {
    const geometry = this.meshes.get(name).geometry.clone();
    geometry.translate(offset.x, offset.y, offset.z);
    this.driveGeometries.add(geometry);
    const mesh = new THREE.Mesh(geometry, this.material(color));
    mesh.name = name;
    mesh.userData.partKey = key;
    return mesh;
  }

  buildDrive() {
    const p = this.manifest.planetary;
    const kneeOffset = new THREE.Vector3(...this.manifest.knee).negate();
    const ring = this.driveMesh('ring', 'ring', colors.ring, kneeOffset);
    this.ringGeometries = { closed: ring.geometry, open: this.meshes.get('ring_open').geometry.clone() };
    this.driveGeometries.add(this.ringGeometries.open);
    this.root.add(this.addPart('ring', ring, colors.ring, 'fixed ring'));
    const sun = this.driveMesh('sun', 'sun', colors.sun, kneeOffset);
    this.root.add(this.addPart('sun', sun, colors.sun, 'sun · input'));
    const pulley = this.driveMesh('pulley', 'pulley', colors.pulley, kneeOffset);
    this.root.add(this.addPart('pulley', pulley, colors.pulley, 'input sprocket'));
    pulley.visible = false;
    const carrier = this.driveMesh('carrier_detail', 'carrier', colors.carrier);
    this.root.add(this.addPart('carrier', carrier, colors.carrier, 'carrier · output'));
    const planets = new THREE.Group();
    this.planetNodes = Array.from({ length: p.count }, (_, i) => {
      const phase = i * Math.PI * 2 / p.count;
      const origin = new THREE.Vector3(p.orbitRadius * Math.cos(phase), p.orbitRadius * Math.sin(phase), 0);
      const mesh = this.driveMesh(`planet_${i}`, 'planets', colors.planets, origin.clone().negate());
      mesh.position.copy(origin);
      planets.add(mesh);
      return mesh;
    });
    this.root.add(this.addPart('planets', planets, colors.planets, 'planet gears'));
    const hardware = new THREE.Group();
    this.hardwareNodes = [];
    for (let i = 0; i < p.count; i++) {
      for (const prefix of ['planet_screw', 'planet_bearing']) {
        const mesh = this.driveMesh(`${prefix}_${i}`, 'hardware', colors.hardware);
        hardware.add(mesh);
        this.hardwareNodes.push(mesh);
      }
    }
    this.root.add(this.addPart('hardware', hardware, colors.hardware, 'bearings & screws'));
    this.drive = { ring, sun, pulley, carrier, planets, hardware };
  }

  buildAssembly(view) {
    const object = view === 'robot' ? this.model.clone(true) : this.leg.clone(true);
    // gltf uses metres at the ria root; the isolated leg is already millimetres.
    if (view === 'robot') object.scale.setScalar(1000);
    object.traverse(node => {
      if (!node.isMesh) return;
      const { part, side } = node.userData;
      const key = view === 'robot' && side !== 'head' ? `${side}/${part}` : part;
      const role = part === 'ring' ? 'ring' : part === 'sun' ? 'sun' : /^planet_\d/.test(part) ? 'planets' : part === 'lower_leg' ? 'carrier' : part === 'pulley' ? 'pulley' : 'other';
      const color = part === 'tire' || part.includes('belt') ? '#333b47' : colors[role];
      this.addPart(key, node, color, key.replaceAll('_', ' ').replace('/', ' · '));
    });
    this.root.add(object);
  }

  setView(view) {
    this.root.traverse(node => {
      if (node.isMesh) {
        node.material.dispose();
      }
    });
    this.driveGeometries.forEach(geometry => geometry.dispose());
    this.driveGeometries.clear();
    this.root.clear();
    this.parts.clear();
    this.view = view;
    if (view === 'drive') this.buildDrive();
    else this.buildAssembly(view);
    this.selected = null;
    this.update(0, 0, true);
    this.fit('perspective');
  }

  update(angle, explode, cutaway) {
    if (this.view !== 'drive') return;
    const p = this.manifest.planetary;
    const motion = planetaryMotion(angle, p);
    const { ring, sun, pulley, carrier, hardware } = this.drive;
    sun.rotation.z = pulley.rotation.z = motion.sun;
    carrier.rotation.z = hardware.rotation.z = motion.carrier;
    sun.position.z = explode * 6;
    pulley.position.z = explode * 38;
    ring.position.z = explode * 20;
    carrier.position.z = hardware.position.z = -explode * 16;
    this.planetNodes.forEach((mesh, i) => {
      const orbit = i * Math.PI * 2 / p.count + motion.carrier;
      mesh.position.set(p.orbitRadius * Math.cos(orbit), p.orbitRadius * Math.sin(orbit), 0);
      mesh.rotation.z = motion.planet;
    });
    ring.geometry = cutaway ? this.ringGeometries.open : this.ringGeometries.closed;
  }

  fit(direction = 'perspective') {
    const bounds = this.view === 'drive'
      ? new THREE.Box3(new THREE.Vector3(-28, -28, -6), new THREE.Vector3(28, 28, 36))
      : new THREE.Box3().setFromObject(this.root);
    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    const margin = this.view === 'drive' ? 0.9 : 1.2;
    const distance = size.length() / (2 * Math.tan(THREE.MathUtils.degToRad(this.camera.fov / 2))) * margin / Math.min(1, this.camera.aspect);
    const vectors = { perspective: new THREE.Vector3(0.8, -1.3, 1.7), top: new THREE.Vector3(0, -0.001, 1), side: new THREE.Vector3(0, -1, 0.001) };
    if (this.view === 'robot') vectors.perspective.set(1.2, -1.8, 0.7);
    this.camera.position.copy(center).add(vectors[direction === 'fit' ? 'perspective' : direction].normalize().multiplyScalar(distance));
    this.controls.target.copy(center);
    this.controls.update();
  }

  select(key) {
    this.selected = key;
    for (const [name, part] of this.parts) part.object.traverse(mesh => {
      if (mesh.isMesh) mesh.material.emissive.set(name === key ? part.color : 0x000000).multiplyScalar(0.22);
    });
  }

  focusSelected() {
    if (this.view === 'drive') return this.fit();
    const bounds = new THREE.Box3().setFromObject(this.parts.get(this.selected).object);
    const center = bounds.getCenter(new THREE.Vector3());
    const distance = bounds.getSize(new THREE.Vector3()).length() / (2 * Math.tan(THREE.MathUtils.degToRad(this.camera.fov / 2))) / Math.min(1, this.camera.aspect);
    const direction = this.camera.position.clone().sub(this.controls.target).normalize();
    this.controls.target.copy(center);
    this.camera.position.copy(center).addScaledVector(direction, distance);
    this.controls.update();
  }

  pick(event) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.pointer.set((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1);
    this.raycaster.setFromCamera(this.pointer, this.camera);
    const hits = this.raycaster.intersectObject(this.root, true);
    return hits.find(hit => {
      let node = hit.object;
      while (node && node !== this.root) {
        if (!node.visible) return false;
        node = node.parent;
      }
      return true;
    })?.object.userData.partKey;
  }

  getMotion() {
    return {
      sun: this.drive.sun.rotation.z,
      carrier: this.drive.carrier.rotation.z,
      ring: this.drive.ring.rotation.z,
      planets: this.planetNodes.map(mesh => ({ angle: mesh.rotation.z, position: mesh.position.toArray() })),
    };
  }

  resize() {
    this.camera.aspect = this.host.clientWidth / this.host.clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(this.host.clientWidth, this.host.clientHeight);
  }

  render() {
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}
