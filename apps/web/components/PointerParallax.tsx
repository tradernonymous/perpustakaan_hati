"use client";

import { useRef, type PointerEvent, type ReactNode } from "react";

/**
 * Pointer parallax. Writes --ph-px and --ph-py (-1 to 1) on the wrapper; children
 * with .ph-parallax-layer shift by their own depth in CSS (motion-upgrade.css).
 * Touch, small screens and reduced motion never move: the CSS is gated the same way.
 */
export function PointerParallax({ children, className = "" }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);

  const reset = () => {
    const el = ref.current;
    if (!el) return;
    el.style.setProperty("--ph-px", "0");
    el.style.setProperty("--ph-py", "0");
  };

  const onPointerMove = (e: PointerEvent<HTMLDivElement>) => {
    const el = ref.current;
    if (!el || e.pointerType === "touch") return;
    if (!window.matchMedia("(hover: hover) and (pointer: fine) and (min-width: 640px) and (prefers-reduced-motion: no-preference)").matches) return;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const x = Math.max(-1, Math.min(1, ((e.clientX - r.left) / r.width) * 2 - 1));
    const y = Math.max(-1, Math.min(1, ((e.clientY - r.top) / r.height) * 2 - 1));
    el.style.setProperty("--ph-px", x.toFixed(3));
    el.style.setProperty("--ph-py", y.toFixed(3));
  };

  return (
    <div ref={ref} className={`ph-parallax-3d ${className}`.trim()} onPointerMove={onPointerMove} onPointerLeave={reset}>
      {children}
    </div>
  );
}
