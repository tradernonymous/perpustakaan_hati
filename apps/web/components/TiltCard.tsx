"use client";

import { useCallback, useRef, type ReactNode } from "react";

/**
 * First creation: importers are Hero, EbookDeck, and premium homepage sections.
 * Affected API: one new TiltCard component with children/className only.
 * Data schemas: none; the card stores no personal data.
 * User instruction: "just build it and please give me you best advanced,
 * futuristic, 3d, premium and educational design system and website design".
 */
export function TiltCard({ children, className = "" }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const set = useCallback((x: number, y: number) => {
    const el = ref.current;
    if (!el) return;
    el.style.setProperty("--tilt-x", `${x.toFixed(2)}deg`);
    el.style.setProperty("--tilt-y", `${y.toFixed(2)}deg`);
    el.style.setProperty("--tilt-glow-x", `${((y / 12) + 0.5) * 100}%`);
    el.style.setProperty("--tilt-glow-y", `${((x / -10) + 0.5) * 100}%`);
  }, []);
  const onMove = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    const el = ref.current;
    if (!el || e.pointerType === "touch" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const r = el.getBoundingClientRect();
    set(-((e.clientY - r.top) / r.height - 0.5) * 10, ((e.clientX - r.left) / r.width - 0.5) * 12);
  }, [set]);
  const onLeave = useCallback(() => set(0, 0), [set]);
  return (
    <div ref={ref} tabIndex={0} onPointerMove={onMove} onPointerLeave={onLeave} className={`ph-tilt-card ${className}`}>
      {children}
    </div>
  );
}
