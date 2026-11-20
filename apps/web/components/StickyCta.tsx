"use client";

import { useEffect, useState } from "react";

const INLINE_ACTION_SECTIONS = ["atas", "percuma", "edisi", "katalog", "penutup", "kaki-laman"];

export function StickyCta() {
  const [hidden, setHidden] = useState(true);

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return;
    const sections = INLINE_ACTION_SECTIONS.map((id) => document.getElementById(id)).filter((section) => section !== null);
    const inView = new Set<Element>();
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) inView.add(entry.target);
        else inView.delete(entry.target);
      }
      setHidden(inView.size > 0);
    });
    for (const section of sections) observer.observe(section);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      data-sticky-cta
      data-hidden={hidden}
      aria-hidden={hidden || undefined}
      className="ph-sticky-cta fixed inset-x-0 bottom-0 z-sticky border-t border-line bg-surface px-3 pb-[calc(0.5rem+env(safe-area-inset-bottom))] pt-2 md:hidden"
    >
      <a href="#percuma" tabIndex={hidden ? -1 : undefined} className="ph-cta mx-auto flex min-h-tap w-full max-w-xs justify-center px-3 py-2 text-center text-sm">
        Edisi Poket percuma
      </a>
    </div>
  );
}
