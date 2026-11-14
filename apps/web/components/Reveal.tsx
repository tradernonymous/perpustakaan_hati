"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

type Props = { children: ReactNode; delay?: number; className?: string };

/**
 * Fades/slides content in when it scrolls into view.
 * Immediately reveals under reduced-motion or when already inside/above the
 * viewport so tall mobile sections never stay invisible.
 */
export function Reveal({ children, delay = 0, className = "" }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [vis, setVis] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (
      typeof IntersectionObserver === "undefined" ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
      el.getBoundingClientRect().top < window.innerHeight * 0.96
    ) {
      setVis(true);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          setVis(true);
          io.disconnect();
        }
      },
      { threshold: 0.02 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      data-revealed={vis}
      className={`transition-all duration-700 ease-out will-change-transform ${vis ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"} ${className}`}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
    >
      {children}
    </div>
  );
}
