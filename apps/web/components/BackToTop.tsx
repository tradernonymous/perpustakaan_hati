"use client";

import { useEffect, useState } from "react";

/**
 * Floating return-to-top control. Appears only after the reader has scrolled
 * meaningfully, sits above the mobile sticky CTA, and respects reduced motion
 * (the base CSS layer already collapses scroll-behavior to auto).
 */
export function BackToTop() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    let raf = 0;
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        setShow(window.scrollY > 640);
      });
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <button
      type="button"
      className="ph-back-top"
      data-show={show}
      aria-hidden={!show || undefined}
      tabIndex={show ? undefined : -1}
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      aria-label="Kembali ke atas"
    >
      <svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
        <path d="M8 13V3M4 7l4-4 4 4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </button>
  );
}
