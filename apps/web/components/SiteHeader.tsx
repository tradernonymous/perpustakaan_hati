"use client";

import { useEffect, useState } from "react";
import { NAV } from "@/src/content";
import { BrandMark } from "@/components/BrandMark";

export function SiteHeader({ base = "" }: { base?: string }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const homeHref = base ? "/" : "#atas";

  return (
    <header className="ph-header sticky top-0 z-header border-b border-line">
      {/* First tab stop on every page: jumps the sticky header entirely. */}
      <a
        href={`${base}#utama`}
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-2 focus:z-toast focus:rounded focus:bg-surface-raised focus:px-4 focus:py-2 focus:text-fg"
      >
        Lompat ke kandungan
      </a>
      <div className="mx-auto flex max-w-grid items-center justify-between gap-4 px-5 py-2">
        <a href={homeHref} className="flex min-h-tap items-center gap-3 font-display text-lg text-fg">
          <BrandMark size={48} className="h-12 w-12 shrink-0" />
          <span>Perpustakaan Hati</span>
        </a>

        <nav aria-label="Utama" className="hidden items-center gap-1 lg:flex">
          {NAV.map((n) => (
            <a key={n.href} href={`${base}${n.href}`} className="flex min-h-tap items-center rounded px-2.5 text-sm text-fg transition-colors hover:text-fg">
              {n.label}
            </a>
          ))}
          <a href={`${base}#interaktif`} className="flex min-h-tap items-center rounded px-2.5 text-sm text-fg transition-colors hover:text-fg">
            Interaktif
          </a>
          <a href="/pustaka" className="flex min-h-tap items-center rounded px-2.5 text-sm font-medium text-fg-healing transition-colors hover:text-fg">
            Pustaka
          </a>
          <a href={`${base}#percuma`} className="ph-cta ml-2 min-h-tap text-sm">Edisi Poket, percuma</a>
        </nav>

        <button
          type="button"
          className="flex min-h-tap min-w-tap cursor-pointer items-center justify-center rounded border border-line text-fg lg:hidden"
          aria-expanded={open}
          aria-controls="menu-mudah-alih"
          aria-label={open ? "Tutup menu" : "Buka menu"}
          onClick={() => setOpen((v) => !v)}
        >
          <span aria-hidden="true" className="text-xl leading-none">{open ? "×" : "☰"}</span>
        </button>
      </div>

      {open && (
        <nav id="menu-mudah-alih" aria-label="Menu mudah alih" className="border-t border-line bg-surface-raised px-5 pb-4 lg:hidden">
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
            <li>
              <a href="/teman-hati" onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-line text-fg">
                Teman Hati AI
              </a>
            </li>
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
