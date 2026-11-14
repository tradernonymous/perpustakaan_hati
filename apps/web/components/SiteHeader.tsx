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
    <header className="sticky top-0 z-header border-b border-daylight-edge bg-daylight/90 backdrop-blur">
      {/* First tab stop on every page: jumps the sticky header entirely. */}
      <a
        href={`${base}#utama`}
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-2 focus:z-toast focus:rounded focus:bg-daylight-raised focus:px-4 focus:py-2 focus:text-green-900"
      >
        Lompat ke kandungan
      </a>
      <div className="mx-auto flex max-w-grid items-center justify-between gap-4 px-5 py-2">
        <a href={homeHref} className="flex min-h-tap items-center gap-3 font-display text-lg text-green-900">
          <BrandMark size={48} className="h-12 w-12 shrink-0" />
          <span>Perpustakaan Hati</span>
        </a>

        <nav aria-label="Utama" className="hidden items-center gap-1 lg:flex">
          {NAV.map((n) => (
            <a key={n.href} href={`${base}${n.href}`} className="flex min-h-tap items-center rounded px-2.5 text-sm text-ink-grove transition-colors hover:text-green-900">
              {n.label}
            </a>
          ))}
          <a href={`${base}#interaktif`} className="flex min-h-tap items-center rounded px-2.5 text-sm text-ink-grove transition-colors hover:text-green-900">
            Interaktif
          </a>
          <a href="/pustaka" className="flex min-h-tap items-center rounded px-2.5 text-sm font-medium text-green-800 transition-colors hover:text-green-900">
            Pustaka
          </a>
          <a href={`${base}#percuma`} className="ph-cta ml-2 min-h-tap text-sm">Edisi Poket, percuma</a>
        </nav>

        <button
          type="button"
          className="flex min-h-tap min-w-tap cursor-pointer items-center justify-center rounded border border-daylight-edge text-ink-grove lg:hidden"
          aria-expanded={open}
          aria-controls="menu-mudah-alih"
          aria-label={open ? "Tutup menu" : "Buka menu"}
          onClick={() => setOpen((v) => !v)}
        >
          <span aria-hidden="true" className="text-xl leading-none">{open ? "×" : "☰"}</span>
        </button>
      </div>

      {open && (
        <nav id="menu-mudah-alih" aria-label="Menu mudah alih" className="border-t border-daylight-edge bg-daylight-raised px-5 pb-4 lg:hidden">
          <ul className="flex flex-col">
            {NAV.map((n) => (
              <li key={n.href}>
                <a href={`${base}${n.href}`} onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-daylight-edge text-ink-grove">
                  {n.label}
                </a>
              </li>
            ))}
            <li>
              <a href={`${base}#interaktif`} onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-daylight-edge text-ink-grove">
                Ruang Interaktif
              </a>
            </li>
            <li>
              <a href="/teman-hati" onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-daylight-edge text-ink-grove">
                Teman Hati AI
              </a>
            </li>
            <li>
              <a href="/kad-jujur-hati" onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-daylight-edge text-ink-grove">
                Kad Jujur Hati
              </a>
            </li>
            <li>
              <a href="/cermin-pasangan" onClick={() => setOpen(false)} className="flex min-h-tap items-center border-b border-daylight-edge text-ink-grove">
                Cermin Pasangan
              </a>
            </li>
            <li>
              <a href="/pustaka" onClick={() => setOpen(false)} className="flex min-h-tap items-center font-medium text-green-800">
                Pustaka Saya
              </a>
            </li>
          </ul>
        </nav>
      )}
    </header>
  );
}
