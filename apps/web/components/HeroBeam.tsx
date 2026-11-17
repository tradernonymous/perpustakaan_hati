"use client";

import { useEffect, useRef } from "react";

/**
 * Hero light: one beam falling from the top edge (fades in once, then
 * breathes by opacity only) and one soft spotlight that follows a real
 * pointer. Decorative, aria-hidden, no layout work: the pointer writes two
 * custom properties at most once per frame. Touch and reduced motion do
 * nothing.
 */
export function HeroBeam() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;
    let raf = 0;
    let last: PointerEvent | null = null;
    const apply = () => {
      raf = 0;
      const el = ref.current;
      const e = last;
      if (!el || !e) return;
      const r = el.getBoundingClientRect();
      el.style.setProperty("--hx", `${(e.clientX - r.left).toFixed(0)}px`);
      el.style.setProperty("--hy", `${(e.clientY - r.top).toFixed(0)}px`);
    };
    const onMove = (e: PointerEvent) => {
      if (e.pointerType === "touch") return;
      last = e;
      if (!raf) raf = requestAnimationFrame(apply);
    };
    window.addEventListener("pointermove", onMove, { passive: true });
    return () => {
      window.removeEventListener("pointermove", onMove);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <div ref={ref} className="ph-hero-fx" aria-hidden="true">
      <span className="ph-hero-beam" />
      <span className="ph-hero-spot" />
    </div>
  );
}
