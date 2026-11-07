"use client";

import { useId } from "react";

type Props = { size?: number; className?: string };

/**
 * Animated Perpustakaan Hati mark — Design System 3.1 "Gilded Grove" remix.
 *
 * Flat treatment (no 3D, header-safe): an emerald heart rising out of an
 * open book, wrapped in a slow-dashed gold orbit ring with a soft emerald
 * glow pulse underneath and staggered twinkling sparks. All motion is CSS
 * keyframes; the base layer zeroes them under prefers-reduced-motion.
 */
export function BrandMark({ size = 32, className = "" }: Props) {
  const uid = useId().replace(/[^a-zA-Z0-9]/g, "");
  const glowId = `phm-glow-${uid}`;
  const heartId = `phm-heart-${uid}`;

  return (
    <svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      className={className}
      role="img"
      aria-label="Perpustakaan Hati"
    >
      <defs>
        <radialGradient id={glowId} cx="0.5" cy="0.45" r="0.55">
          <stop offset="0" stopColor="#3f9167" stopOpacity="0.55" />
          <stop offset="0.6" stopColor="#2d7954" stopOpacity="0.25" />
          <stop offset="1" stopColor="#2d7954" stopOpacity="0" />
        </radialGradient>
        <linearGradient id={heartId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#e9cea2" />
          <stop offset="0.5" stopColor="#5b9b7d" />
          <stop offset="1" stopColor="#2d7954" />
        </linearGradient>
      </defs>

      <circle cx="50" cy="50" r="34" fill={`url(#${glowId})`} className="ph-mark-glow" />
      <circle
        cx="50"
        cy="50"
        r="36.5"
        fill="none"
        stroke="#c9a86a"
        strokeWidth="1.4"
        strokeDasharray="2.5 7"
        className="ph-mark-orbit"
      />
      <path
        d="M50 84 C31 61 18 47 18 31 C18 16 26 9 35 9 C40.5 9 45 12.6 50 18.6 C55 12.6 60.5 9 66 9 C75 9 82 16 82 31 C82 47 69 61 50 84 Z"
        fill={`url(#${heartId})`}
      />
      <circle cx="78" cy="24" r="2.2" fill="#f2b85c" className="ph-mark-twinkle" style={{ animationDelay: "0.4s" }} />
      <circle cx="24" cy="30" r="1.8" fill="#7db895" className="ph-mark-twinkle" style={{ animationDelay: "1.6s" }} />
      <circle cx="70" cy="74" r="1.6" fill="#e9cea2" className="ph-mark-twinkle" style={{ animationDelay: "2.4s" }} />
    </svg>
  );
}
