"use client";

import { temanHatiEnabled } from "@/src/feature-flags";
import { useEffect, useRef, useState } from "react";
import { NAV } from "@/src/content";
import { BrandMark } from "@/components/BrandMark";
import { OPEN_PALETTE_EVENT } from "@/components/CommandPalette";

/** Sections the desktop nav can point at, in page order. */
const SPY_IDS = NAV.map((n) => n.href.replace(/^#/, ""));

export function SiteHeader({ base = "" }: { base?: string }) {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState<string>("");
  const menuButton = useRef<HTMLButtonElement>(null);
  const progressFill = useRef<HTMLSpanElement>(null);
  const firstMenuLink = useRef<HTMLAnchorElement>(null);

  // Reading progress hairline + scrolled elevation. Writes straight to the
  // DOM so a scroll never re-renders the header.
  useEffect(() => {
    let raf = 0;
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        const el = document.documentElement;
        const max = el.scrollHeight - el.clientHeight;
        const top = el.scrollTop;
        if (progressFill.current) {
          progressFill.current.style.transform = `scaleX(${max > 0 ? Math.min(1, top / max) : 0})`;
        }
        setScrolled(top > 8);
      });
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      cancelAnimationFrame(raf);
    };
  }, []);

  // Scroll-spy for the same-page section links (home page only).
  useEffect(() => {
    if (base || typeof IntersectionObserver === "undefined") return;
    const sections = SPY_IDS.map((id) => document.getElementById(id)).filter((el): el is HTMLElement => el !== null);
    if (sections.length === 0) return;
    const visible = new Map<Element, number>();
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) visible.set(entry.target, entry.intersectionRatio);
          else visible.delete(entry.target);
        }
        let best: Element | null = null;
        let bestRatio = 0;
        for (const [el, ratio] of visible) {
          if (ratio > bestRatio) { best = el; bestRatio = ratio; }
        }
        setActive(best ? `#${best.id}` : "");
      },
      { rootMargin: "-30% 0px -55% 0px", threshold: [0, 0.1, 0.5] }
    );
    for (const el of sections) io.observe(el);
    return () => io.disconnect();
  }, [base]);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape" || event.defaultPrevented) return;
      setOpen(false);
      menuButton.current?.focus();
    };
    window.addEventListener("keydown", onKey);
    firstMenuLink.current?.focus();
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const homeHref = base ? "/" : "#atas";
  const close = () => setOpen(false);

  return (
    <header className="ph-header sticky top-0 z-header border-b border-line" data-scrolled={scrolled || undefined}>
      {/* First tab stop on every page: jumps the sticky header entirely. */}
      <a
        href="#utama"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-2 focus:z-toast focus:rounded focus:bg-surface-raised focus:px-4 focus:py-2 focus:text-fg"
      >
        Lompat ke kandungan
      </a>

      {/* Reading progress hairline along the header's bottom edge. */}
      <div className="ph-scroll-progress" aria-hidden="true">
        <span ref={progressFill} />
      </div>

      {open && (
        <button
          type="button"
          aria-hidden="true"
          onClick={close}
          className="ph-menu-backdrop fixed inset-0 lg:hidden"
          tabIndex={-1}
        />
      )}

      <div className="relative mx-auto flex max-w-grid items-center justify-between gap-3 px-4 py-2 sm:px-5 lg:gap-4">
        <a href={homeHref} onClick={close} className="flex min-h-tap min-w-0 items-center gap-2 font-display text-base leading-tight text-fg sm:gap-3 sm:text-lg">
          <BrandMark size={48} className="h-9 w-9 shrink-0 sm:h-12 sm:w-12" />
          <span>Perpustakaan Hati</span>
        </a>

        <nav aria-label="Utama" className="hidden items-center gap-1 lg:flex">
          {NAV.map((n) => {
            const href = `${base}${n.href}`;
            const isActive = !base && active === n.href;
            return (
              <a
                key={n.href}
                href={href}
                aria-current={isActive ? "location" : undefined}
                className={`ph-nav-link flex min-h-tap items-center rounded px-2.5 text-sm transition-colors ${
                  isActive ? "font-semibold text-fg" : "text-fg-muted hover:text-fg"
                }`}
              >
                {n.label}
              </a>
            );
          })}
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
          className="ph-burger-btn flex min-h-tap min-w-tap shrink-0 cursor-pointer items-center justify-center rounded border border-line text-fg lg:hidden"
          aria-expanded={open}
          aria-controls="menu-mudah-alih"
          aria-label={open ? "Tutup menu" : "Buka menu"}
          onClick={() => setOpen((v) => !v)}
        >
          <span className="ph-burger" data-open={open} aria-hidden="true"><i /><i /><i /></span>
        </button>
      </div>

      {open && (
        <nav id="menu-mudah-alih" aria-label="Menu mudah alih" className="ph-mobile-menu relative max-h-[calc(100dvh-4rem)] overflow-y-auto overscroll-contain border-t border-line bg-surface-raised px-4 pb-4 sm:px-5 lg:hidden">
          <ul className="flex flex-col">
            {NAV.map((n, i) => (
              <li key={n.href} className="ph-mobile-menu-item" style={{ animationDelay: `${40 + i * 45}ms` }}>
                <a ref={i === 0 ? firstMenuLink : undefined} href={`${base}${n.href}`} onClick={close} className="flex min-h-tap items-center border-b border-line text-fg">
                  {n.label}
                </a>
              </li>
            ))}
            {temanHatiEnabled && <li className="ph-mobile-menu-item" style={{ animationDelay: `${40 + NAV.length * 45}ms` }}>
              <a href="/teman-hati" onClick={close} className="flex min-h-tap items-center border-b border-line text-fg">
                Teman Hati AI
              </a>
            </li>}
            <li className="ph-mobile-menu-item" style={{ animationDelay: `${40 + (NAV.length + (temanHatiEnabled ? 1 : 0)) * 45}ms` }}>
              <a href="/kad-jujur-hati" onClick={close} className="flex min-h-tap items-center border-b border-line text-fg">
                Kad Jujur Hati
              </a>
            </li>
            <li className="ph-mobile-menu-item" style={{ animationDelay: `${40 + (NAV.length + (temanHatiEnabled ? 2 : 1)) * 45}ms` }}>
              <a href="/cermin-pasangan" onClick={close} className="flex min-h-tap items-center border-b border-line text-fg">
                Cermin Pasangan
              </a>
            </li>
            <li className="ph-mobile-menu-item" style={{ animationDelay: `${40 + (NAV.length + (temanHatiEnabled ? 3 : 2)) * 45}ms` }}>
              <a href="/pustaka" onClick={close} className="flex min-h-tap items-center font-medium text-fg-healing">
                Pustaka Saya
              </a>
            </li>
          </ul>
        </nav>
      )}
    </header>
  );
}
