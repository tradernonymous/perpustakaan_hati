"use client";

import { useEffect, useRef, useState } from "react";
import { TESTIMONIALS } from "@/src/content";

const ROTATION_MS = 9000;
const COUNT = TESTIMONIALS.length;

export function Testimonials() {
  const carousel = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(0);
  const [motionAllowed, setMotionAllowed] = useState(false);
  const [inView, setInView] = useState(false);
  const [pageVisible, setPageVisible] = useState(false);
  const [rotation, setRotation] = useState<"auto" | "paused" | "playing">("auto");
  const [hovered, setHovered] = useState(false);
  const [focused, setFocused] = useState(false);
  const playing = motionAllowed && inView && pageVisible && (
    rotation === "playing" || (rotation === "auto" && !hovered && !focused)
  );

  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const syncMotion = () => setMotionAllowed(!preference.matches);
    const syncVisibility = () => setPageVisible(document.visibilityState === "visible");
    syncMotion();
    syncVisibility();
    preference.addEventListener("change", syncMotion);
    document.addEventListener("visibilitychange", syncVisibility);
    const observer = typeof IntersectionObserver === "undefined" ? null : new IntersectionObserver(([entry]) => {
      setInView(entry.isIntersecting && entry.intersectionRatio >= 0.25);
    }, { threshold: 0.25 });
    if (carousel.current) observer?.observe(carousel.current);
    return () => {
      preference.removeEventListener("change", syncMotion);
      document.removeEventListener("visibilitychange", syncVisibility);
      observer?.disconnect();
    };
  }, []);

  useEffect(() => {
    if (!playing) return;
    const timer = window.setTimeout(() => setActive((current) => (current + 1) % COUNT), ROTATION_MS);
    return () => window.clearTimeout(timer);
  }, [active, playing]);

  function move(direction: number) {
    setRotation("paused");
    setActive((current) => (current + direction + COUNT) % COUNT);
  }

  function holdRotation() {
    setRotation((mode) => mode === "playing" ? "auto" : mode);
  }

  return (
    <div ref={carousel} role="region" aria-label="Maklum balas di Threads" aria-roledescription="karusel"
      className="mx-auto max-w-reading"
      onPointerEnter={(event) => {
        if (event.pointerType !== "mouse") return;
        setHovered(true);
        holdRotation();
      }}
      onPointerLeave={() => setHovered(false)}
      onFocus={() => { setFocused(true); holdRotation(); }}
      onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setFocused(false); }}>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
        <div className="flex items-center gap-2">
          <button type="button" className="btn-ghost min-w-tap px-0 py-0" aria-label="Maklum balas sebelumnya" onClick={() => move(-1)}>
            <span aria-hidden="true">‹</span>
          </button>
          <p className="px-1 text-sm tabular-nums text-fg-muted" aria-live={playing ? "off" : "polite"}>
            <span className="sr-only">Maklum balas </span>{active + 1} / {COUNT}
          </p>
          <button type="button" className="btn-ghost min-w-tap px-0 py-0" aria-label="Maklum balas seterusnya" onClick={() => move(1)}>
            <span aria-hidden="true">›</span>
          </button>
        </div>
        {motionAllowed && (
          <button type="button" className="min-h-tap px-2 text-sm text-fg-healing underline underline-offset-4"
            onClick={() => setRotation((mode) => mode === "paused" ? "playing" : "paused")}>
            {rotation === "paused" ? "Sambung putaran" : "Jeda putaran"}
          </button>
        )}
      </div>
      <div className="ph-card grid border-l-2 border-l-gold-deep">
        {TESTIMONIALS.map((item, index) => (
          <a key={item.url} href={item.url} target="_blank" rel="noopener noreferrer"
            aria-hidden={index !== active || undefined} tabIndex={index === active ? undefined : -1}
            className={`col-start-1 row-start-1 flex min-w-0 rounded p-5 sm:p-7 ${index === active ? "" : "invisible pointer-events-none"}`}>
            <figure className="flex w-full flex-col justify-between gap-5">
              <blockquote className="break-words font-reading text-lg leading-relaxed text-fg sm:text-xl">“{item.quote}”</blockquote>
              <figcaption className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-sm">
                <span className="break-all font-medium text-fg-muted">{item.who}</span>
                <span className="text-fg-healing underline underline-offset-4">Baca di Threads <span aria-hidden="true">↗</span></span>
              </figcaption>
            </figure>
          </a>
        ))}
      </div>
    </div>
  );
}
