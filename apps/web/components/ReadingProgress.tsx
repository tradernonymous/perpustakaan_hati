"use client";

import { useEffect, useState } from "react";

/**
 * Scroll progress indicator. Keeps `.ph-progress` in the Hero for initial
 * reading orientation and adds a slim fixed hairline along the top edge so
 * progress remains visible throughout the page.
 */
export function ReadingProgress() {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const update = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(max > 0 ? Math.min(100, Math.max(0, Math.round((window.scrollY / max) * 100))) : 0);
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
  }, []);
  return (
    <>
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-x-0 top-0 z-toast h-[3px] bg-transparent"
      >
        <span
          className="block h-full bg-gradient-to-r from-green-700 via-green-400 to-lantern transition-[width] duration-150 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div
        className="ph-progress"
        role="progressbar"
        aria-label="Kemajuan bacaan"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={progress}
      >
        <span style={{ width: `${progress}%` }} />
        <span className="ph-progress-label">Kemajuan bacaan · {progress}%</span>
      </div>
    </>
  );
}
