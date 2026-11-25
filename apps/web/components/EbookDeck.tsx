"use client";

import { useCallback, useRef, useState } from "react";
import { TIERS } from "@/src/content";
import { ProductCover } from "./ProductCover";
import { PsycheBadge } from "./PsycheIcon";
import { TIER_PSYCHE } from "@/src/psyche";

const LAUNCH_NOTE: Record<string, string> = {
  poket: "Percuma sepenuhnya",
  membangun: "Harga pelancaran sekarang: RM 29.00",
  "teman-hidup": "Harga pelancaran sekarang: RM 79.00",
};

/**
 * 3D ebook deck — the tiers of Perpustakaan Hati as a coverflow carousel.
 * Keyboard Left/Right is scoped to the carousel region (never global window)
 * so typing in forms is never interrupted, and off-screen slide CTAs are
 * removed from tab order until active.
 */
export function EbookDeck() {
  const [index, setIndex] = useState(0);
  const touchX = useRef<number | null>(null);

  const go = useCallback((dir: number) => {
    setIndex((i) => (i + dir + TIERS.length) % TIERS.length);
  }, []);

  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      go(-1);
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      go(1);
    }
  };

  const onTouchStart = (e: React.TouchEvent) => {
    touchX.current = e.touches[0].clientX;
  };
  const onTouchEnd = (e: React.TouchEvent) => {
    if (touchX.current == null) return;
    const dx = e.changedTouches[0].clientX - touchX.current;
    touchX.current = null;
    if (Math.abs(dx) > 40) go(dx < 0 ? 1 : -1);
  };

  const tier = TIERS[index];

  return (
    <div
      className="ph-coverflow mx-auto max-w-grid focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700"
      role="group"
      aria-roledescription="carousel"
      aria-label="Edisi Perpustakaan Hati"
      tabIndex={0}
      onKeyDown={onKeyDown}
      onTouchStart={onTouchStart}
      onTouchEnd={onTouchEnd}
    >
      <div className="relative mx-auto max-w-[460px]">
        <div className="relative aspect-[3/4] w-full" style={{ perspective: "1400px" }}>
          <div
            className="absolute inset-0 will-change-transform"
            style={{
              transform: `translateX(calc(${-100}% * ${index}))`,
              transition: "transform 650ms cubic-bezier(0.16, 1, 0.3, 1)",
            }}
          >
            {TIERS.map((t, i) => {
              const d = i - index;
              const dist = Math.abs(d);
              const scale = 1 - dist * dist * 0.09;
              const opacity = 1 - dist * 0.3;
              const ry = d * -16;
              const z = -160 * dist * dist;
              const active = i === index;
              return (
                <div
                  key={t.id}
                  role="group"
                  aria-roledescription="slide"
                  aria-label={`${i + 1} of ${TIERS.length}`}
                  aria-hidden={!active}
                  data-active={active}
                  data-tier={t.id}
                  className={`ph-coverflow-card absolute inset-0 rounded bg-surface-raised ${active ? "ph-beam" : "overflow-hidden"}`}
                  style={{
                    transform: `translateX(${i * 100}%) scale(${scale}) rotateY(${ry}deg) translateZ(${z}px)`,
                    opacity,
                    filter: dist ? `blur(${(dist * 1.5).toFixed(1)}px)` : "none",
                    transition: "transform 650ms cubic-bezier(0.16, 1, 0.3, 1), opacity 400ms ease-out, filter 400ms ease-out",
                  }}
                >
                  <span className="ph-spine" aria-hidden="true" />
                  <ProductCover
                    name={t.name}
                    src={t.cover}
                    seal={t.seal.replace("/brand/", "/brand/animated/")}
                    tier={t.id}
                    className="h-full w-full rounded-none border-0"
                  />
                  <span className="ph-ribbon ph-tier-ribbon absolute left-1/2 top-4 -translate-x-1/2 whitespace-nowrap" data-tier={t.id}>
                    {t.price}
                  </span>
                  <a
                    href={t.id === "poket" ? "#percuma" : `/beli/${t.id}`}
                    tabIndex={active ? 0 : -1}
                    className="ph-cta absolute inset-x-0 bottom-0 my-3 inline-flex min-h-tap items-center justify-center"
                  >
                    {t.id === "poket" ? "Dapatkan percuma" : `Beli ${t.name}`}
                  </a>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="mt-5 flex items-center justify-center gap-2">
        <button
          type="button"
          onClick={() => go(-1)}
          aria-label="Edisi sebelumnya"
          className="flex min-h-tap min-w-tap cursor-pointer items-center justify-center rounded-pill border border-line bg-surface-raised text-xl text-fg transition-colors hover:border-gold-deep"
        >
          <span aria-hidden="true">‹</span>
        </button>
        <div className="flex" role="tablist" aria-label="Pilih edisi">
          {TIERS.map((t, i) => (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={i === index}
              aria-label={`Edisi ${t.name}`}
              onClick={() => setIndex(i)}
              className="flex min-h-tap min-w-tap cursor-pointer items-center justify-center"
            >
              <span
                aria-hidden="true"
                data-tier={t.id}
                className={`block h-2 rounded-pill transition-[width] duration-300 ${i === index ? "w-6" : "w-2 bg-line"}`}
                style={i === index ? { background: "var(--tier-fill)" } : undefined}
              />
            </button>
          ))}
        </div>
        <button
          type="button"
          onClick={() => go(1)}
          aria-label="Edisi seterusnya"
          className="flex min-h-tap min-w-tap cursor-pointer items-center justify-center rounded-pill border border-line bg-surface-raised text-xl text-fg transition-colors hover:border-gold-deep"
        >
          <span aria-hidden="true">Seterusnya</span>
        </button>
      </div>

      <div className="ph-tier-card ph-lux mx-auto mt-6 max-w-reading p-5 text-center" data-tier={tier.id}>
        <div className="flex items-center justify-center gap-2.5">
          <PsycheBadge id={TIER_PSYCHE[tier.id]} tier={tier.id} />
          <h3 className="ph-title text-2xl ph-tier-ink">{tier.name}</h3>
        </div>
        <p className="mt-1 font-display text-3xl ph-tier-ink">{tier.price}</p>
        <p className="mt-1 text-xs font-semibold ph-tier-ink">{LAUNCH_NOTE[tier.id]}</p>
        <p className="mt-2 text-sm text-fg-muted">{tier.size}</p>
        <p className="mt-2 font-display italic text-fg">{tier.subcopy}</p>
        <ul className="mx-auto mt-4 flex max-w-[460px] flex-col gap-1.5 text-left text-sm text-fg">
          {tier.includes.map((item) => (
            <li key={item} className="flex items-start gap-2">
              <span aria-hidden="true" className="ph-tier-ink">◆</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
