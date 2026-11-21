"use client";

import { temanHatiEnabled } from "@/src/feature-flags";
import { useEffect, useRef, useState } from "react";
import { NAV } from "@/src/content";
import { BrandMark } from "@/components/BrandMark";
import { OPEN_PALETTE_EVENT } from "@/components/CommandPalette";

export function SiteHeader({ base = "" }: { base?: string }) {
  const [open, setOpen] = useState(false);
  const menuButton = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape" || event.defaultPrevented) return;
      setOpen(false);
      menuButton.current?.focus();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const homeHref = base ? "/" : "#atas";

  return (
    <header className="ph-header sticky top-0 z-header border-b border-line">
      {/* First tab stop on every page: jumps the sticky header entirely. */}
      <a
        href="#utama"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-2 focus:z-toast focus:rounded focus:bg-surface-raised focus:px-4 focus:py-2 focus:text-fg"
      >
        Lompat ke kandungan
      </a>
      <div className="mx-auto flex max-w-grid items-center justify-between gap-3 px-4 py-2 sm:px-5 lg:gap-4">
        <a href={homeHref} onClick={() => setOpen(false)} className="flex min-h-tap min-w-0 items-center gap-2 font-display text-base leading-tight text-fg sm:gap-3 sm:text-lg">
          <BrandMark size={48} className="h-9 w-9 shrink-0 sm:h-12 sm:w-12" />
          <span>Perpustakaan Hati</span>
        </a>

        <nav aria-label="Utama" className="hidden items-center gap-1 lg:flex">
          {NAV.map((n) => (
            <a key={n.href} href={`${base}${n.href}`} className="flex min-h-tap items-center rounded px-2.5 text-sm text-fg-muted transition-colors hover:text-fg">
              {n.label}
            </a>
          ))}
          <a href={`${base}#interaktif`} className="flex min-h-tap items-center rounded px-2.5 text-sm text-fg-muted transition-colors hover:text-fg">
            Interaktif
          </a>
          <a href="/pustaka" className="flex min-h-tap items-center rounded px-2.5 text-sm font-medium text-fg-healing transition-colors hover:text-fg">
            Pustaka
          </a>
          <button type="button" onClick={() => window.dispatchEvent(new Event(OPEN_PALETTE_EVENT))} className="ph-kbd-hint ml-1" aria-label="Lompat ke bahagian atau halaman (Ctrl atau Cmd + K)">
            <span>Lompat ke</span><kbd aria-hidden="true">Ctrl K</kbd>
          </button>
          <a href={`${base}#percuma`} className="ph-cta ml-2 min-h-tap text-sm">Edisi Poket, percuma</a>
        </nav>

        <button
          ref={menuButton}
          type="button"
          className="flex min-h-tap min-w-tap shrink-0 cursor-pointer items-center justify-center rounded border border-line text-fg lg:hidden"
          aria-expanded={open}
          aria-controls="menu-mudah-alih"
          aria-label={open ? "Tutup menu" : "Buka menu"}
          onClick={() => setOpen((v) => !v)}
        >
          <span aria-hidden="true" className="text-xl leading-none">{open ? "×" : "☰"}</span>
        </button>
      </div>

      {open && (
        <nav id="menu-mudah-alih" aria-label="Menu mudah alih" className="max-h-[calc(100dvh-4rem)] overflow-y-auto overscroll-contain border-t border-line bg-surface-raised px-4 pb-4 sm:px-5 lg:hidden">
          <ul className="flex flex-col">
            {NAV.map((n) => (
              <li key={n.href}>
                <a href={`${base}${n.href}`} onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-line text-fg">
                  {n.label}
                </a>
              </li>
            ))}
            <li>
              <a href={`${base}#interaktif`} onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-line text-fg">
                Ruang Interaktif
              </a>
            </li>
            {temanHatiEnabled && <li>
              <a href="/teman-hati" onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-line text-fg">
                Teman Hati AI
              </a>
            </li>}
            <li>
              <a href="/kad-jujur-hati" onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-line text-fg">
                Kad Jujur Hati
              </a>
            </li>
            <li>
              <a href="/cermin-pasangan" onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-line text-fg">
                Cermin Pasangan
              </a>
            </li>
            <li>
              <a href="/pustaka" onClick={() => setOpen(false)} className="flex min-h-tap items-center font-medium text-fg-healing">
                Pustaka Saya
              </a>
            </li>
          </ul>
        </nav>
      )}
    </header>
  );
}
