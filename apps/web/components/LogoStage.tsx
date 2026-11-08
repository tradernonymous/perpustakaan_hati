"use client";

import { useCallback, useRef, type ReactNode } from "react";

/**
 * 3D stage for the hero lockup: the already-extruded SVG lockup tilts toward
 * the pointer (max 7deg) on a perspective plane, its cast shadow shifts the
 * other way and a lantern spotlight follows. Not focusable (it is decoration
 * around the h1). Mouse/pen only; static under reduced motion.
 */
export function LogoStage({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);

  const set = useCallback((x: number, y: number) => {
    const el = ref.current;
    if (!el) return;
    el.style.setProperty("--lx", `${(x * 14).toFixed(2)}deg`);
    el.style.setProperty("--ly", `${(-y * 10).toFixed(2)}deg`);
    el.style.setProperty("--lsx", `${(-x * 18).toFixed(1)}px`);
    el.style.setProperty("--lsy", `${(24 - y * 10).toFixed(1)}px`);
    el.style.setProperty("--lgx", `${((x + 0.5) * 100).toFixed(1)}%`);
    el.style.setProperty("--lgy", `${((y + 0.5) * 100).toFixed(1)}%`);
  }, []);

  const onMove = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    if (e.pointerType === "touch" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const r = e.currentTarget.getBoundingClientRect();
    set((e.clientX - r.left) / r.width - 0.5, (e.clientY - r.top) / r.height - 0.5);
  }, [set]);

  return (
    <div ref={ref} className="ph-logo-stage" onPointerMove={onMove} onPointerLeave={() => set(0, 0)}>
      <div className="ph-logo-stage-inner">{children}</div>
    </div>
  );
}
