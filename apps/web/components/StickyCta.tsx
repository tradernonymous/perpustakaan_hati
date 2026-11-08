"use client";

import { useEffect, useState } from "react";

/**
 * Mobile sticky CTA (ported from website_sam StickyBuyBar): it steps aside
 * while the opt-in form (#percuma) is on screen, so it never covers the form
 * it points to, and slides back once the form leaves view.
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
      className="ph-sticky-cta fixed inset-x-0 bottom-0 z-40 border-t border-forest-edge bg-forest-night/95 p-3 backdrop-blur md:hidden"
    >
      <a href="#percuma" tabIndex={hidden ? -1 : undefined} className="ph-cta flex min-h-cta-mobile w-full items-center justify-center">
        Dapatkan Edisi Poket, percuma
      </a>
    </div>
  );
}
