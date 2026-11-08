"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Educational stats strip with count-up numbers (ported from website_sam
 * AnimatedNumber: ease-out cubic). Every number is real and comes from the
 * edition contents in src/content.ts. The server renders the FINAL value, so
 * no-JS readers, crawlers and reduced-motion users see the true number; the
 * count-up only runs in the browser when the strip scrolls into view.
 */
const STATS = [
  { value: 7, label: "bab panduan", note: "Edisi Membangun" },
  { value: 30, label: "soalan refleksi", note: "Kit Refleksi" },
  { value: 60, label: "saat sehari", note: "7 Hari Reset" },
  { value: 12, label: "kad refleksi", note: "Teman Hidup" },
];

function CountUp({ to }: { to: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const [n, setN] = useState(to);

  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let raf = 0;
    const io = new IntersectionObserver(([entry]) => {
      if (!entry?.isIntersecting) return;
      io.disconnect();
      const start = performance.now();
      const tick = (t: number) => {
        const p = Math.min(1, (t - start) / 1400);
        setN(Math.round(to * (1 - Math.pow(1 - p, 3))));
        if (p < 1) raf = requestAnimationFrame(tick);
      };
      setN(0);
      raf = requestAnimationFrame(tick);
    }, { threshold: 0.6 });
    io.observe(el);
    return () => { io.disconnect(); cancelAnimationFrame(raf); };
  }, [to]);

  return <span ref={ref}>{n}</span>;
}

export function StatsStrip() {
  return (
    <section aria-label="Apa yang ada di dalam" className="ph-stats ph-section-warm bg-daylight px-5 py-10">
      <dl className="mx-auto grid max-w-grid grid-cols-2 gap-4 md:grid-cols-4">
        {STATS.map((s) => (
          <div key={s.label} className="ph-lux ph-card flex flex-col items-center gap-1 p-5 text-center">
            <dt className="order-2 text-sm text-ink-grove">{s.label}</dt>
            <dd className="ph-stat-num ph-foil-gold order-1 font-display text-5xl tabular-nums">
              <CountUp to={s.value} />
            </dd>
            <dd className="order-3 text-xs uppercase tracking-kicker text-muted-grove">{s.note}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
