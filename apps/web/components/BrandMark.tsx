"use client";

import { useId } from "react";

type Props = { size?: number; className?: string };

/**
 * Perpustakaan Hati mark — the ORIGINAL book-heart emblem
 * (docs/brand/assets/emblem-book-heart.svg, built by build-logos.py with the
 * lit bevel, extruded cover board and gilt page block), framed by the
 * animated layer: a soft emerald glow pulse, a slow dashed gold orbit and
 * staggered lantern twinkles. All motion is CSS keyframes; the base layer
 * zeroes it under prefers-reduced-motion.
 *
 * Brand rule: the emblem's detail needs >= 48px. Below that use
 * /brand/monogram-stamp.svg instead (the favicon already does).
 */
export function BrandMark({ size = 48, className = "" }: Props) {
  const uid = useId().replace(/[^a-zA-Z0-9]/g, "");
  const glowId = `phm-glow-${uid}`;

  return (
    <svg viewBox="0 0 100 100" width={size} height={size} className={className} role="img" aria-label="Perpustakaan Hati">
      <defs>
        <radialGradient id={glowId} cx="0.5" cy="0.45" r="0.55">
          <stop offset="0" stopColor="#3f9167" stopOpacity="0.55" />
          <stop offset="0.6" stopColor="#2d7954" stopOpacity="0.22" />
          <stop offset="1" stopColor="#2d7954" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx="50" cy="50" r="46" fill={`url(#${glowId})`} className="ph-mark-glow" />
      <circle
        cx="50"
        cy="50"
        r="47"
        fill="none"
        stroke="#c9a86a"
        strokeWidth="1.2"
        strokeDasharray="2.5 7"
        className="ph-mark-orbit"
      />
      {/* emblem is 600x420: fit 90 wide, centred, nudged up for optical balance */}
      <image href="/brand/emblem-book-heart.svg" x="5" y="17" width="90" height="63" preserveAspectRatio="xMidYMid meet" />
      <circle cx="84" cy="22" r="2" fill="#f2b85c" className="ph-mark-twinkle" style={{ animationDelay: "0.4s" }} />
      <circle cx="14" cy="34" r="1.6" fill="#7db895" className="ph-mark-twinkle" style={{ animationDelay: "1.6s" }} />
      <circle cx="78" cy="84" r="1.5" fill="#e9cea2" className="ph-mark-twinkle" style={{ animationDelay: "2.4s" }} />
    </svg>
  );
}
