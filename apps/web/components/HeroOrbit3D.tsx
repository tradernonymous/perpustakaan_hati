"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import styles from "./HeroOrbit3D.module.css";

export const EMBLEM_SRC = "/brand/emblem-book-heart.svg";

const TAU = Math.PI * 2;
const wave = (t: number, period: number) => 0.5 - 0.5 * Math.cos((TAU * t) / period);
const mod = (a: number, b: number) => ((a % b) + b) % b;
const clamp01 = (x: number) => Math.min(1, Math.max(0, x));
const pulseAt = (x: number, center: number, width: number) => Math.exp(-(((x - center) / width) ** 2));

const BEAT = 1.4;
const WAVE_LIFE = 1.8;
const WAVE_COUNT = 3;
const ORBIT_SPEED = 0.12;
const CLEAN_POSE_TIME = 0.8;
const MAX_PIXEL_RATIO = 1.5;
// Scene is pushed down (negative) so the emblem sits below the top-anchored text.

const COVERS = [
  { name: "Edisi Poket", src: "/ebooks/cover-poket.png", back: 0x5b9b7d, phase: 0 },
  { name: "Edisi Membangun", src: "/ebooks/cover-membangun.png", back: 0xc9a86a, phase: TAU / 3 },
  { name: "Teman Hidup", src: "/ebooks/cover-teman-hidup.png", back: 0x5c1e17, phase: (2 * TAU) / 3 },
] as const;

// Psychology glyphs — healing-journey motifs rendered as canvas textures on sprites.
// Each glyph is a simple line-art shape drawn procedurally to avoid extra asset loads.
const PSYCHE_GLYPHS = [
  { id: "awareness", color: 0xa7d3b6, x: -1.8, y: 0.9, z: -0.5, size: 0.18, speed: 0.7 },
  { id: "heal",        color: 0x9de1c1, x:  1.9, y: 0.7, z: -0.3, size: 0.16, speed: 0.9 },
  { id: "companion",   color: 0xe9cea2, x: -1.6, y:-0.8, z: -0.4, size: 0.15, speed: 0.6 },
  { id: "build",       color: 0xc9a86a, x:  1.7, y:-0.9, z: -0.6, size: 0.17, speed: 0.8 },
  { id: "voice",       color: 0x7db895, x: -2.1, y: 0.1, z: -0.7, size: 0.14, speed: 1.0 },
  { id: "talk",        color: 0xf2b85c, x:  2.0, y: 0.0, z: -0.5, size: 0.15, speed: 0.75 },
  { id: "fence",       color: 0xa7d3b6, x: -0.8, y: 1.3, z: -0.8, size: 0.13, speed: 0.65 },
  { id: "links",       color: 0xe9cea2, x:  0.9, y:-1.3, z: -0.6, size: 0.14, speed: 0.85 },
] as const;

function drawGlyph(ctx: CanvasRenderingContext2D, id: string, s: number) {
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = s * 0.08;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  const h = s / 2;
  ctx.beginPath();
  switch (id) {
    case "awareness": // eye
      ctx.moveTo(-h, 0); ctx.quadraticCurveTo(0, -h * 0.8, h, 0);
      ctx.quadraticCurveTo(0, h * 0.8, -h, 0);
      ctx.moveTo(h * 0.22, 0); ctx.arc(0, 0, h * 0.22, 0, TAU);
      break;
    case "heal": // sprout
      ctx.moveTo(0, h); ctx.lineTo(0, -h * 0.2);
      ctx.moveTo(0, -h * 0.2); ctx.quadraticCurveTo(h * 0.6, -h * 0.8, h * 0.5, -h * 0.1);
      ctx.moveTo(0, -h * 0.2); ctx.quadraticCurveTo(-h * 0.6, -h * 0.8, -h * 0.5, -h * 0.1);
      break;
    case "companion": // heart
      ctx.moveTo(0, h * 0.7);
      ctx.bezierCurveTo(-h, h * 0.1, -h, -h * 0.6, 0, -h * 0.3);
      ctx.bezierCurveTo(h, -h * 0.6, h, h * 0.1, 0, h * 0.7);
      break;
    case "build": // steps
      ctx.rect(-h * 0.7, h * 0.2, h * 0.4, h * 0.6);
      ctx.rect(-h * 0.15, -h * 0.3, h * 0.4, h * 1.1);
      ctx.rect(h * 0.4, -h * 0.8, h * 0.4, h * 1.6);
      break;
    case "voice": // sound bars
      for (let i = -2; i <= 2; i++) {
        const bh = h * (0.4 + 0.3 * Math.abs(Math.sin(i * 1.2)));
        ctx.moveTo(i * h * 0.3, -bh); ctx.lineTo(i * h * 0.3, bh);
      }
      break;
    case "talk": // speech bubble
      ctx.moveTo(-h * 0.6, -h * 0.5); ctx.lineTo(h * 0.6, -h * 0.5);
      ctx.quadraticCurveTo(h * 0.8, -h * 0.5, h * 0.8, -h * 0.2);
      ctx.lineTo(h * 0.8, h * 0.2);
      ctx.quadraticCurveTo(h * 0.8, h * 0.5, h * 0.6, h * 0.5);
      ctx.lineTo(-h * 0.1, h * 0.5); ctx.lineTo(-h * 0.5, h * 0.8);
      ctx.lineTo(-h * 0.5, h * 0.5); ctx.lineTo(-h * 0.6, h * 0.5);
      ctx.quadraticCurveTo(-h * 0.8, h * 0.5, -h * 0.8, h * 0.2);
      ctx.lineTo(-h * 0.8, -h * 0.2);
      ctx.quadraticCurveTo(-h * 0.8, -h * 0.5, -h * 0.6, -h * 0.5);
      break;
    case "fence": // picket fence
      for (let i = -1.5; i <= 1.5; i += 1) {
        ctx.moveTo(i * h * 0.35, -h * 0.7); ctx.lineTo(i * h * 0.35, h * 0.7);
      }
      ctx.moveTo(-h * 0.8, -h * 0.2); ctx.lineTo(h * 0.8, -h * 0.2);
      ctx.moveTo(-h * 0.8, h * 0.3); ctx.lineTo(h * 0.8, h * 0.3);
      break;
    case "links": // two interlocking circles
      ctx.arc(-h * 0.25, 0, h * 0.4, 0, TAU);
      ctx.moveTo(h * 0.65, 0); ctx.arc(h * 0.25, 0, h * 0.4, 0, TAU);
      break;
    default:
      ctx.arc(0, 0, h * 0.5, 0, TAU);
  }
  ctx.stroke();
}

function makeGlyphTexture(id: string, color: number): [THREE.CanvasTexture, number] {
  const size = 128;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d")!;
  ctx.clearRect(0, 0, size, size);
  drawGlyph(ctx, id, size * 0.7);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return [texture, color];
}

function makeHalo(): [THREE.Mesh, THREE.CanvasTexture] {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext("2d")!;
  const gradient = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
  gradient.addColorStop(0, "rgba(201, 168, 106, 0.34)");
  gradient.addColorStop(1, "rgba(201, 168, 106, 0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 256, 256);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const material = new THREE.MeshBasicMaterial({ map: texture, transparent: true, depthWrite: false, opacity: 0.6 });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 2.2), material);
  return [mesh, texture];
}

function makeGlowTexture(hex: number): THREE.CanvasTexture {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext("2d")!;
  const r = (hex >> 16) & 255, g = (hex >> 8) & 255, b = hex & 255;
  const gradient = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  gradient.addColorStop(0, `rgba(${r},${g},${b},0.9)`);
  gradient.addColorStop(0.35, `rgba(${r},${g},${b},0.35)`);
  gradient.addColorStop(1, `rgba(${r},${g},${b},0)`);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 128, 128);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function makeGlowSprite(hex: number, size: number, opacity: number): [THREE.Sprite, THREE.CanvasTexture] {
  const tex = makeGlowTexture(hex);
  const material = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false });
  const sprite = new THREE.Sprite(material);
  sprite.scale.setScalar(size);
  return [sprite, tex];
}

export function HeroOrbit3D() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pausedRef = useRef(false);
  const refreshRef = useRef<() => void>(() => {});
  const [paused, setPaused] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setReducedMotion(reduced);

    let renderer: THREE.WebGLRenderer | null = null;
    try {
      renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    } catch {
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, MAX_PIXEL_RATIO));
    renderer.setClearColor(0x000000, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, 0.01, 100);
    camera.position.set(0, 0.15, 3.0);

    const rig = new THREE.Group();
    scene.add(rig);

    const disposables: { dispose: () => void }[] = [];
    let disposed = false;
    const loader = new THREE.TextureLoader();

    const loadTex = (url: string): Promise<THREE.Texture> => new Promise((resolve) => {
      loader.load(url, (tex) => {
        if (disposed) { tex.dispose(); return; }
        tex.colorSpace = THREE.SRGBColorSpace;
        disposables.push(tex);
        resolve(tex);
      }, undefined, () => resolve(null as unknown as THREE.Texture));
    });

    // Halo
    const [halo, haloTex] = makeHalo();
    halo.position.z = -0.12;
    rig.add(halo);
    disposables.push(halo.geometry, halo.material as THREE.Material, haloTex);

    // Polar grid
    const grid = new THREE.PolarGridHelper(1.6, 16, 6, 64, 0xc9a86a, 0x7db895);
    grid.position.y = -0.62;
    (grid.material as THREE.Material).transparent = true;
    (grid.material as THREE.Material).opacity = 0.14;
    (grid.material as THREE.Material).depthWrite = false;
    rig.add(grid);
    disposables.push(grid.geometry, grid.material as THREE.Material);

    // Heartbeat waves
    const waves = Array.from({ length: WAVE_COUNT }, () => {
      const geo = new THREE.RingGeometry(0.9, 0.93, 96);
      const mat = new THREE.MeshBasicMaterial({ color: 0x9de1c1, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.z = -0.05;
      rig.add(mesh);
      disposables.push(geo, mat);
      return mesh;
    });

    const pointer = { x: 0, y: 0 };
    const smoothPointer = { x: 0, y: 0 };
    let smoothScroll = 0;
    let emblemPivot: THREE.Group | null = null;
    let coverItems: { group: THREE.Group; frontMat: THREE.MeshBasicMaterial; phase: number; index: number }[] = [];
    let glyphSprites: { sprite: THREE.Sprite; baseX: number; baseY: number; baseZ: number; speed: number; baseOpacity: number; baseSize: number }[] = [];

    // Psychology glyph sprites
    const glyphGroup = new THREE.Group();
    rig.add(glyphGroup);
    for (const g of PSYCHE_GLYPHS) {
      const [tex] = makeGlyphTexture(g.id, g.color);
      disposables.push(tex);
      const mat = new THREE.SpriteMaterial({
        map: tex,
        color: g.color,
        transparent: true,
        opacity: 0.35,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      });
      disposables.push(mat);
      const sprite = new THREE.Sprite(mat);
      sprite.scale.setScalar(g.size);
      sprite.position.set(g.x, g.y, g.z);
      glyphGroup.add(sprite);
      glyphSprites.push({ sprite, baseX: g.x, baseY: g.y, baseZ: g.z, speed: g.speed, baseOpacity: 0.35, baseSize: g.size });
    }

    const init = async () => {
      const [emblemTex, ...coverTextures] = await Promise.all([
        loadTex(EMBLEM_SRC),
        ...COVERS.map((c) => loadTex(c.src)),
      ]);
      if (disposed || !emblemTex) return;

      // Emblem
      const ew = 1.2;
      const eh = ew * (emblemTex.image.height / emblemTex.image.width);
      const emblemGeo = new THREE.PlaneGeometry(ew, eh);
      const emblemMat = new THREE.MeshBasicMaterial({ map: emblemTex, transparent: true, depthWrite: false });
      const emblem = new THREE.Mesh(emblemGeo, emblemMat);
      emblem.renderOrder = 2;
      const pivot = new THREE.Group();
      pivot.add(emblem);
      const [emblemGlow, glowTex] = makeGlowSprite(0xc9a86a, 1.6, 0.4);
      emblemGlow.position.z = -0.08;
      pivot.add(emblemGlow);
      rig.add(pivot);
      emblemPivot = pivot;
      disposables.push(emblemGeo, emblemMat, glowTex, emblemGlow.material as THREE.Material);

      // Covers
      coverItems = COVERS.map((cover, i) => {
        const tex = coverTextures[i];
        if (!tex) return null as unknown as typeof coverItems[number];
        const w = 0.42;
        const h = w * (tex.image.height / tex.image.width);
        const frontMat = new THREE.MeshBasicMaterial({ map: tex });
        const backMat = new THREE.MeshBasicMaterial({ color: cover.back });
        const group = new THREE.Group();
        const frontGeo = new THREE.PlaneGeometry(w, h);
        const backGeo = new THREE.PlaneGeometry(w, h);
        const spineGeo = new THREE.BoxGeometry(0.014, h, 0.012);
        const spineMat = new THREE.MeshBasicMaterial({ color: cover.back });
        const front = new THREE.Mesh(frontGeo, frontMat);
        front.position.z = 0.006;
        const back = new THREE.Mesh(backGeo, backMat);
        back.rotation.y = Math.PI;
        back.position.z = -0.006;
        const spine = new THREE.Mesh(spineGeo, spineMat);
        spine.position.x = -w / 2;
        group.add(front, back, spine);
        const [glow, gTex] = makeGlowSprite(cover.back, w * 2.2, 0.3);
        glow.position.z = -0.03;
        group.add(glow);
        rig.add(group);
        disposables.push(frontGeo, backGeo, spineGeo, frontMat, backMat, spineMat, gTex, glow.material as THREE.Material);
        return { group, frontMat, phase: cover.phase, index: i };
      }).filter(Boolean);

      setReady(true);
      if (reduced) pose(CLEAN_POSE_TIME, 0);
    };

    const pose = (t: number, dt: number) => {
      const follow = 1 - Math.exp(-dt * 3);
      smoothPointer.x += (pointer.x - smoothPointer.x) * follow;
      smoothPointer.y += (pointer.y - smoothPointer.y) * follow;
      const scrollTarget = clamp01(window.scrollY / Math.max(1, window.innerHeight));
      smoothScroll += (scrollTarget - smoothScroll) * follow;

      // Push the scene down so the emblem sits below the top-anchored text.
      // The tiny breathing bob rides on top.
      rig.position.y = 0.012 * wave(t, 6);
      rig.rotation.y = 0.6 * smoothScroll;

      if (emblemPivot) {
        emblemPivot.rotation.y = 0.25 * Math.sin((TAU * t) / 4.5) + 0.25 * smoothPointer.x;
        emblemPivot.rotation.x = 0.12 * smoothPointer.y;
        const beatPhase = mod(t, BEAT) / BEAT;
        const beat = pulseAt(beatPhase, 0.05, 0.05) + 0.6 * pulseAt(beatPhase, 0.25, 0.05);
        emblemPivot.scale.setScalar(1 + 0.04 * beat);

        const cycle = mod(t, BEAT);
        waves.forEach((mesh, j) => {
          const p = clamp01((cycle + j * BEAT) / WAVE_LIFE);
          const eased = 1 - (1 - p) * (1 - p);
          mesh.scale.setScalar(0.7 + 1.3 * eased);
          (mesh.material as THREE.MeshBasicMaterial).opacity = 0.7 * (1 - p) * (1 - p);
        });

        halo.scale.setScalar(0.92 + 0.14 * wave(t, 4) + 0.12 * beat);
        (halo.material as THREE.MeshBasicMaterial).opacity = 0.25 + 0.15 * wave(t, 4);
      }

      grid.rotation.y = t * 0.04;

      for (const item of coverItems) {
        const a = item.phase + t * ORBIT_SPEED + 0.25 * smoothPointer.x;
        item.group.position.x = 0.85 * Math.sin(a);
        item.group.position.z = 0.5 * Math.cos(a);
        item.group.position.y = 0.24 * Math.sin(a) - 0.12 * Math.cos(a);
        item.group.rotation.y = -0.45 * Math.sin(a);
        item.frontMat.color.setScalar(0.88 + 0.12 * wave(t, 4));
      }

      // Psychology glyphs: float gently, react to pointer proximity
      for (const g of glyphSprites) {
        const floatY = 0.06 * Math.sin(t * g.speed + g.baseX * 2);
        const floatX = 0.03 * Math.cos(t * g.speed * 0.7 + g.baseY * 3);
        g.sprite.position.x = g.baseX + floatX + smoothPointer.x * 0.15 * g.speed;
        g.sprite.position.y = g.baseY + floatY + smoothPointer.y * 0.1 * g.speed;
        g.sprite.position.z = g.baseZ;

        // Hover sensitivity: brighten when pointer is near
        const dx = smoothPointer.x - g.baseX * 0.3;
        const dy = smoothPointer.y - g.baseY * 0.3;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const hover = Math.max(0, 1 - dist * 1.5);
        const targetOpacity = g.baseOpacity + hover * 0.5;
        const mat = g.sprite.material as THREE.SpriteMaterial;
        mat.opacity += (targetOpacity - mat.opacity) * follow;
        const scaleBoost = 1 + hover * 0.3;
        g.sprite.scale.setScalar(g.baseSize * scaleBoost);
      }
    };

    let time = reduced ? CLEAN_POSE_TIME : 0;
    let lastFrame = performance.now();
    let rafId: number | null = null;
    let inView = true;
    const canAnimate = () => !reduced && inView && !pausedRef.current && !document.hidden;

    const renderAt = (t: number, dt: number) => { pose(t, dt); renderer!.render(scene, camera); };
    const frame = (now: number) => {
      rafId = null;
      if (!canAnimate()) return;
      const dt = Math.min((now - lastFrame) / 1000, 0.1);
      lastFrame = now;
      time += dt;
      renderAt(time, dt);
      rafId = requestAnimationFrame(frame);
    };
    const refresh = () => {
      if (disposed) return;
      if (canAnimate()) { if (rafId === null) { lastFrame = performance.now(); rafId = requestAnimationFrame(frame); } return; }
      if (rafId !== null) { cancelAnimationFrame(rafId); rafId = null; }
      renderAt(time, 0);
    };
    refreshRef.current = refresh;

    const resize = () => {
      const w = Math.max(1, container.clientWidth);
      const h = Math.max(1, container.clientHeight);
      renderer!.setSize(w, h, false);
      camera.aspect = w / h;
      camera.position.z = Math.max(2.9, 3.9 / camera.aspect);
      camera.position.y = 0;
      camera.updateProjectionMatrix();
      refresh();
    };

    const onPointerMove = (e: PointerEvent) => {
      const r = container.getBoundingClientRect();
      if (!r.width || !r.height) return;
      pointer.x = Math.max(-1, Math.min(1, ((e.clientX - r.left) / r.width) * 2 - 1));
      pointer.y = Math.max(-1, Math.min(1, ((e.clientY - r.top) / r.height) * 2 - 1));
    };
    const onPointerLeave = () => { pointer.x = 0; pointer.y = 0; };

    const ro = new ResizeObserver(resize);
    ro.observe(container);
    const io = new IntersectionObserver(([entry]) => { inView = entry.isIntersecting; refresh(); });
    io.observe(container);
    document.addEventListener("visibilitychange", refresh);
    container.addEventListener("pointermove", onPointerMove);
    container.addEventListener("pointerleave", onPointerLeave);

    resize();
    init();

    return () => {
      disposed = true;
      if (rafId !== null) cancelAnimationFrame(rafId);
      ro.disconnect(); io.disconnect();
      document.removeEventListener("visibilitychange", refresh);
      container.removeEventListener("pointermove", onPointerMove);
      container.removeEventListener("pointerleave", onPointerLeave);
      refreshRef.current = () => {};
      for (const d of disposables) d.dispose();
      renderer!.dispose();
    };
  }, []);

  const togglePause = () => {
    pausedRef.current = !pausedRef.current;
    setPaused(pausedRef.current);
    refreshRef.current();
  };

  return (
    <div className={styles.orbit} ref={containerRef}>
      <img
        className={ready ? `${styles.poster} ${styles.posterHidden}` : styles.poster}
        src={EMBLEM_SRC}
        alt=""
        width={600}
        height={420}
        fetchPriority="high"
      />
      <canvas ref={canvasRef} className={styles.canvas} aria-hidden="true" />
      <p className={styles.srOnly}>
        Perpustakaan Hati emblem, orbited by the Edisi Poket, Edisi Membangun and Teman Hati covers.
      </p>
      {ready && !reducedMotion && (
        <button type="button" className={styles.toggle} aria-pressed={paused} onClick={togglePause}>
          Pause animation
        </button>
      )}
    </div>
  );
}
