"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import pages from "@/src/tips-reader.json";
import { TIPS_PATH } from "@/src/tips";
import styles from "./TipsFlipbook.module.css";

export function TipsFlipbook({ initialPage = 1, artwork, signup, signedIn = false }: {
  initialPage?: number;
  artwork: boolean;
  signup?: ReactNode;
  signedIn?: boolean;
}) {
  const [page, setPage] = useState(initialPage);
  const [wide, setWide] = useState(false);
  const [textMode, setTextMode] = useState(false);
  const [fullscreenSupported, setFullscreenSupported] = useState(false);
  const viewer = useRef<HTMLElement>(null);
  const touch = useRef<{ x: number; y: number } | null>(null);

  useEffect(() => {
    setFullscreenSupported(Boolean(document.fullscreenEnabled));
    const view = window.matchMedia("(min-width: 720px)");
    const sync = () => setWide(view.matches);
    sync();
    view.addEventListener("change", sync);
    return () => view.removeEventListener("change", sync);
  }, []);

  const spread = wide && page > 1 && page < pages.length;
  const last = spread ? page + 1 : page;
  const next = Math.min(pages.length, last + 1);
  const previous = Math.max(1, page - (wide ? 2 : 1));
  const current = spread ? [page, last] : [page];

  return (
    <div className="mx-auto grid max-w-grid gap-5">
      <section ref={viewer} className={`ph-card ${styles.viewer}`} aria-label="Buku selak Tips Psikologi Suami Isteri"
        onKeyDown={(event) => {
          if (event.altKey || event.ctrlKey || event.metaKey || event.defaultPrevented) return;
          if (event.key === "ArrowLeft" && page > 1) { event.preventDefault(); setPage(previous); }
          if (event.key === "ArrowRight" && last < pages.length) { event.preventDefault(); setPage(next); }
        }}>
        <div className="mb-3 grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-2">
          <button type="button" disabled={page === 1} className="btn-ghost justify-self-start px-2 py-1 text-xs disabled:opacity-40 sm:px-6 sm:text-base" onClick={() => setPage(previous)}>Sebelumnya</button>
          <span className="text-center text-sm tabular-nums" aria-live="polite">
            <span className="sr-only sm:not-sr-only">Halaman </span>
            {page}{spread ? `–${last}` : ""}
            <span className="sr-only sm:not-sr-only"> daripada </span>
            <span className="sm:hidden" aria-hidden="true"> / </span>{pages.length}
          </span>
          <button type="button" disabled={last === pages.length} className="btn-ghost justify-self-end px-2 py-1 text-xs disabled:opacity-40 sm:px-6 sm:text-base" onClick={() => setPage(next)}>Seterusnya</button>
        </div>
        <div className={styles.spread} data-spread={spread}
          onTouchStart={(event) => {
            const point = event.touches[0];
            touch.current = point && event.touches.length === 1 ? { x: point.clientX, y: point.clientY } : null;
          }}
          onTouchCancel={() => { touch.current = null; }}
          onTouchEnd={(event) => {
            const point = event.changedTouches[0];
            const start = touch.current;
            touch.current = null;
            if (!start || !point) return;
            const x = point.clientX - start.x;
            const y = Math.abs(point.clientY - start.y);
            if (Math.abs(x) < 50 || Math.abs(x) < y * 1.5) return;
            if (x < 0 && last < pages.length) setPage(next);
            if (x > 0 && page > 1) setPage(previous);
          }}>
          {current.map((number, slot) => (
            <article key={number} className={`${styles.sheet} ${slot ? styles.second : ""}`} aria-label={`Halaman ${number}`}>
              {artwork && !textMode ? (
                <div className={styles.art} role="img" aria-label={`Reka letak asal halaman ${number}`}
                  style={{ backgroundPosition: `${((number - 1) % 5) * 25}% ${number > 5 ? 100 : 0}%` }} />
              ) : (
                <div className={styles.text}>
                  {number === 1 && <img src="/ebooks/tips-psikologi-suami-isteri-a4.webp" alt="" width={560} height={792} className="mx-auto mb-4 w-40 rounded" />}
                  {pages[number - 1]}
                </div>
              )}
            </article>
          ))}
        </div>
        <div className="mt-1 flex flex-wrap items-center gap-x-4">
          {fullscreenSupported && <button type="button" className="min-h-tap text-sm text-fg-healing underline" onClick={() => {
            if (document.fullscreenElement) void document.exitFullscreen().catch(() => {});
            else void viewer.current?.requestFullscreen?.().catch(() => {});
          }}>Togol skrin penuh</button>}
          {artwork && <button type="button" className="min-h-tap text-sm text-fg-healing underline" onClick={() => setTextMode((value) => !value)}>{textMode ? "Lihat reka letak asal" : "Baca versi teks"}</button>}
        </div>
        {signedIn && <form action="/api/pustaka/bookmark" method="post" className="mt-3">
          <input type="hidden" name="halaman" value={page} />
          <button className="btn-ghost min-h-tap">Simpan halaman ini</button>
        </form>}
      </section>
      {signup ?? (!signedIn && <a href={`/pustaka?halaman=${page}`} className="ph-cta min-h-tap justify-center">Daftar &amp; buka Edisi Poket</a>)}
      {signup && <a href={`${TIPS_PATH}?halaman=${page}`} className="inline-flex min-h-tap items-center justify-center text-sm text-fg-healing underline">Buka pembaca penuh</a>}
    </div>
  );
}
