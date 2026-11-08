"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { TIERS } from "@/src/content";
import { ProductCover } from "./ProductCover";

/**
 * 3D ebook deck — the tiers of Perpustakaan Hati as a coverflow carousel.
 * The free tier (Edisi Poket) rides along with the paid ones, so visitors can
 * preview the family's shape before committing. The active edition is raised
 * toward the reader; neighbours fan back and dim. Arrow keys + touch swipe
 * + dots, with full aria carousel wiring.
 */
export function EbookDeck() {
  const [index, setIndex] = useState(0);
  const touchX = useRef<number | null>(null);

  const go = useCallback((dir: number) => {
    setIndex((i) => (i + dir + TIERS.length) % TIERS.length);
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") go(-1);
      if (e.key === "ArrowRight") go(1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [go]);

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
    <div className="ph-coverflow mx-auto max-w-grid" role="group" aria-roledescription="carousel" aria-label="Edisi Perpustakaan Hati" onTouchStart={onTouchStart} onTouchEnd={onTouchEnd}>
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
              return (
                <div
                  key={t.id}
                  role="group"
                  aria-roledescription="slide"
                  aria-label={`${i + 1} of ${TIERS.length}`}
                  data-active={i === index}
                  className={`ph-coverflow-card absolute inset-0 rounded bg-forest-raised ${i === index ? "ph-beam" : "overflow-hidden"}`}
                  style={{
                    transform: `translateX(${i * 100}%) scale(${scale}) rotateY(${ry}deg) translateZ(${z}px)`,
                    opacity,
                    filter: dist ? `blur(${(dist * 1.5).toFixed(1)}px)` : "none",
                    transition: "transform 650ms cubic-bezier(0.16, 1, 0.3, 1), opacity 400ms ease-out, filter 400ms ease-out",
                  }}
                >
                  <span className="ph-spine" aria-hidden="true" />
                  <ProductCover name={t.name} src={t.cover} seal={t.seal.replace("/brand/", "/brand/animated/")} className="h-full w-full rounded-none border-0" />
                  <span className="ph-ribbon absolute left-1/2 top-4 -translate-x-1/2 whitespace-nowrap text-sm">{t.price}</span>
                  <a
                    href={t.id === "poket" ? "#percuma" : `/beli/${t.id}`}
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
          className="flex min-h-tap min-w-tap items-center justify-center rounded-pill border border-forest-edge bg-forest-raised text-xl text-gold-light transition-colors hover:border-gold-deep"
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
              className="flex min-h-tap min-w-tap items-center justify-center"
            >
              <span aria-hidden="true" className={`block h-2 rounded-pill transition-all duration-300 ${i === index ? "w-6 bg-green-400" : "w-2 bg-forest-edge"}`} />
            </button>
          ))}
        </div>
        <button
          type="button"
          onClick={() => go(1)}
          aria-label="Edisi seterusnya"
          className="flex min-h-tap min-w-tap items-center justify-center rounded-pill border border-forest-edge bg-forest-raised text-xl text-gold-light transition-colors hover:border-gold-deep"
        >
          <span aria-hidden="true">›</span>
        </button>
      </div>

      <div className="mt-6 text-center">
        <h3 className="ph-title text-2xl text-gold-light">{tier.name}</h3>
        <p className="mt-1 font-display text-3xl text-cream">{tier.price}</p>
        <p className="mt-2 text-sm text-on-dark-muted">{tier.size}</p>
      </div>
    </div>
  );
}
