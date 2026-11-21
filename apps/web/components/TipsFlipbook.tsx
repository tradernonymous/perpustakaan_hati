"use client";

import { useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
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
  const [nativeFullscreen, setNativeFullscreen] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const viewer = useRef<HTMLElement>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const inlineFullscreenButton = useRef<HTMLButtonElement>(null);
  const dialogCloseButton = useRef<HTMLButtonElement>(null);
  const touch = useRef<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const view = window.matchMedia("(min-width: 720px)");
    const sync = () => setWide(view.matches);
    const syncFullscreen = () => setNativeFullscreen(document.fullscreenElement === viewer.current);
    sync();
    view.addEventListener("change", sync);
    document.addEventListener("fullscreenchange", syncFullscreen);
    return () => {
      view.removeEventListener("change", sync);
      document.removeEventListener("fullscreenchange", syncFullscreen);
    };
  }, []);

  useEffect(() => {
    if (dialogOpen) dialogCloseButton.current?.focus();
  }, [dialogOpen]);

  const spread = wide && page > 1 && page < pages.length;
  const last = spread ? page + 1 : page;
  const next = Math.min(pages.length, last + 1);
  const previous = Math.max(1, page - (wide ? 2 : 1));
  const current = spread ? [page, last] : [page];

  const showArtwork = artwork && !textMode;

  async function openFullscreen() {
    const target = viewer.current;
    if (document.fullscreenEnabled && target?.requestFullscreen) {
      try {
        await target.requestFullscreen();
        return;
      } catch {
        // Some mobile or embedded browsers reject fullscreen for page content.
      }
    }
    const modal = dialog.current;
    if (modal && !modal.open) {
      modal.showModal();
      setDialogOpen(true);
    }
  }

  function handleReaderKeys(event: KeyboardEvent<HTMLElement>) {
    if (event.altKey || event.ctrlKey || event.metaKey || event.defaultPrevented) return;
    if (event.key === "ArrowLeft" && page > 1) { event.preventDefault(); setPage(previous); }
    if (event.key === "ArrowRight" && last < pages.length) { event.preventDefault(); setPage(next); }
  }

  function renderReader(inDialog: boolean) {
    const expanded = inDialog || nativeFullscreen;
    return (
      <>
        <div className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-2">
          <button type="button" disabled={page === 1} className="btn-ghost justify-self-start px-2 py-1 text-xs disabled:opacity-40 sm:px-6 sm:text-base" onClick={() => setPage(previous)}>Sebelumnya</button>
          <span className="text-center text-sm tabular-nums" aria-live="polite">
            <span className="sr-only sm:not-sr-only">Halaman </span>
            {page}{spread ? `–${last}` : ""}
            <span className="sr-only sm:not-sr-only"> daripada </span>
            <span className="sm:hidden" aria-hidden="true"> / </span>{pages.length}
          </span>
          <button type="button" disabled={last === pages.length} className="btn-ghost justify-self-end px-2 py-1 text-xs disabled:opacity-40 sm:px-6 sm:text-base" onClick={() => setPage(next)}>Seterusnya</button>
        </div>
        <div className={styles.stage} data-artwork={showArtwork}>
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
                {showArtwork ? (
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
        </div>
        <div className="flex flex-wrap items-center gap-x-4">
          <button ref={inDialog ? dialogCloseButton : inlineFullscreenButton} type="button"
            className="min-h-tap text-sm text-fg-healing underline" onClick={() => {
              if (inDialog) dialog.current?.close();
              else if (nativeFullscreen) void document.exitFullscreen();
              else void openFullscreen();
            }}>{expanded ? "Tutup skrin penuh" : "Buka skrin penuh"}</button>
          {artwork && <button type="button" className="min-h-tap text-sm text-fg-healing underline" onClick={() => setTextMode((value) => !value)}>{textMode ? "Lihat reka letak asal" : "Baca versi teks"}</button>}
          {signedIn && <form action="/api/pustaka/bookmark" method="post">
            <input type="hidden" name="halaman" value={page} />
            <button className="min-h-tap text-sm text-fg-healing underline">Simpan halaman ini</button>
          </form>}
        </div>
      </>
    );
  }

  return (
    <div className="mx-auto grid max-w-grid gap-5">
      <section ref={viewer} className={`ph-card ${styles.viewer}`} data-expanded={nativeFullscreen}
        aria-label="Buku selak Tips Psikologi Suami Isteri" onKeyDown={handleReaderKeys}>
        {renderReader(false)}
      </section>
      <dialog ref={dialog} className={styles.fullscreenDialog} aria-label="Pembaca skrin penuh"
        onClose={() => { setDialogOpen(false); inlineFullscreenButton.current?.focus(); }}>
        {dialogOpen && (
          <section className={styles.viewer} data-expanded="true" aria-label="Buku selak Tips Psikologi Suami Isteri" onKeyDown={handleReaderKeys}>
            {renderReader(true)}
          </section>
        )}
      </dialog>
      {signup ?? (!signedIn && <a href={`/pustaka?halaman=${page}`} className="ph-cta min-h-tap justify-center">Daftar &amp; buka Edisi Poket</a>)}
      {signup && <a href={`${TIPS_PATH}?halaman=${page}`} className="inline-flex min-h-tap items-center justify-center text-sm text-fg-healing underline">Buka pembaca penuh</a>}
    </div>
  );
}
