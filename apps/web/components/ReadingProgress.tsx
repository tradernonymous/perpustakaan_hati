"use client";

import { useEffect, useState } from "react";

/**
 * First creation: imported by Home and covered by premium-experience tests.
 * Affected API: ReadingProgress takes no props and exposes a labelled ARIA progressbar.
 * Data schemas: none; scroll percentage is ephemeral browser state.
 * User instruction: "just build it and please give me you best advanced,
 * futuristic, 3d, premium and educational design system and website design".
 */
export function ReadingProgress() {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const update = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(max > 0 ? Math.round((window.scrollY / max) * 100) : 0);
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
  }, []);
  return (
    <div className="ph-progress" role="progressbar" aria-label="Kemajuan bacaan" aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress}>
      <span style={{ width: `${progress}%` }} />
      <span className="ph-progress-label">Kemajuan bacaan · {progress}%</span>
    </div>
  );
}
