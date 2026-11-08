"use client";

import { useCallback, useEffect, useRef } from "react";

/**
 * First creation: imported by Hero only. No API or data schema change;
 * a pointer-events-none decorative field of floating glyphs.
 * User instruction: "don't forget movable glyphs on mouse hover on
 * the hero page as well as mobile first optimization".
 */
const GLYPHS = [
  { char: "❖", x: 8, y: 18, size: 34, delay: "0s" },
  { char: "✦", x: 82, y: 14, size: 28, delay: "0.8s" },
  { char: "◆", x: 90, y: 55, size: 22, delay: "1.4s" },
  { char: "❀", x: 4, y: 68, size: 26, delay: "0.4s" },
  { char: "✧", x: 70, y: 82, size: 24, delay: "1.9s" },
  { char: "❖", x: 28, y: 88, size: 20, delay: "2.3s" },
];

export function HeroGlyphs() {
  const ref = useRef<HTMLDivElement>(null);

  const onPointerMove = useCallback((e: PointerEvent) => {
    const el = ref.current;
    if (!el || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const r = el.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    el.style.setProperty("--glyph-x", `${(x * 18).toFixed(1)}px`);
    el.style.setProperty("--glyph-y", `${(y * 14).toFixed(1)}px`);
  }, []);

  useEffect(() => {
    window.addEventListener("pointermove", onPointerMove, { passive: true });
    return () => window.removeEventListener("pointermove", onPointerMove);
  }, [onPointerMove]);

  return (
    <div ref={ref} className="ph-glyphs" aria-hidden="true">
      {GLYPHS.map((g, i) => (
        <span
          key={i}
          className="ph-glyph"
          style={{ left: `${g.x}%`, top: `${g.y}%`, fontSize: g.size, animationDelay: g.delay }}
        >
          {g.char}
        </span>
      ))}
    </div>
  );
}
