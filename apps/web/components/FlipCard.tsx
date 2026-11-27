"use client";

import { useState, type ReactNode } from "react";

/**
 * Two-sided card. Hover flips it through CSS (.ph-flip in motion-upgrade.css).
 * The button is the touch and keyboard path: it toggles data-flipped.
 */
export function FlipCard({
  front,
  back,
  label = "Balik kad",
  className = "",
}: {
  front: ReactNode;
  back: ReactNode;
  label?: string;
  className?: string;
}) {
  const [flipped, setFlipped] = useState(false);

  return (
    <div className={`ph-flip ${className}`.trim()} data-flipped={flipped ? "true" : "false"}>
      <div className="ph-flip__inner">
        <div className="ph-flip__face">{front}</div>
        <div className="ph-flip__face ph-flip__back">{back}</div>
      </div>
      <button
        type="button"
        className="ph-flip__toggle"
        aria-pressed={flipped}
        onClick={() => setFlipped((v) => !v)}
      >
        {label}
      </button>
    </div>
  );
}
