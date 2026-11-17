"use client";

import { useEffect, useState } from "react";

/**
 * Mobile sticky CTA: steps aside while the opt-in form (#percuma) is on screen,
 * and respects bottom safe-area insets in mobile in-app webviews (Threads / iOS).
 */
export function StickyCta() {
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    const target = document.getElementById("percuma");
    if (!target || typeof IntersectionObserver === "undefined") return;
    const io = new IntersectionObserver(([e]) => setHidden(Boolean(e?.isIntersecting)), { threshold: 0.15 });
    io.observe(target);
    return () => io.disconnect();
  }, []);

  return (
    <div
      data-sticky-cta
      data-hidden={hidden}
      aria-hidden={hidden || undefined}
      className="ph-sticky-cta fixed inset-x-0 bottom-0 z-sticky border-t border-line bg-surface px-3 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur md:hidden"
    >
      <a href="#percuma" tabIndex={hidden ? -1 : undefined} className="ph-cta flex min-h-cta-mobile w-full items-center justify-center">
        Dapatkan Edisi Poket, percuma
      </a>
    </div>
  );
}
