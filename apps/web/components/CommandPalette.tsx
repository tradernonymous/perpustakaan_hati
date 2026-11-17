"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";

export const PALETTE_ITEMS = [
  { label: "Edisi Poket, percuma", hint: "Bahagian", href: "#percuma" },
  { label: "Tiga edisi dan harga", hint: "Bahagian", href: "#edisi" },
  { label: "Intai beberapa bab", hint: "Bahagian", href: "#bab" },
  { label: "Suara pembaca", hint: "Bahagian", href: "#pembaca" },
  { label: "Soalan lazim", hint: "Bahagian", href: "#soalan" },
  { label: "Pustaka Saya", hint: "Halaman", href: "/pustaka" },
  { label: "Teman Hati AI", hint: "Halaman", href: "/teman-hati" },
  { label: "Cermin Pasangan (kuiz 2 minit)", hint: "Halaman", href: "/cermin-pasangan" },
  { label: "Kad Jujur Hati", hint: "Halaman", href: "/kad-jujur-hati" },
  { label: "7 Hari Cabaran Pulih Hati", hint: "Halaman", href: "/cabaran-7-hari" },
  { label: "Surat Hati", hint: "Halaman", href: "/surat-hati" },
  { label: "Booking Kaunseling", hint: "Halaman", href: "/booking" },
  { label: "Kelab Perpustakaan Hati", hint: "Halaman", href: "/kelab" },
] as const;

/** Event other components dispatch to open the palette (the header hint button). */
export const OPEN_PALETTE_EVENT = "ph:open-palette";

/**
 * Keyboard-first quick jump (Ctrl/Cmd+K), the reference site's signature.
 * ARIA combobox + listbox: focus stays in the search field, the active
 * option is announced through aria-activedescendant. Esc closes and returns
 * focus to where it was. Section hrefs are plain anchors, so they work on
 * the home page; from other pages they go through "/".
 */
export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const returnTo = useRef<HTMLElement | null>(null);
  const uid = useId();

  const items = useMemo(() => {
    const t = q.trim().toLowerCase();
    return t ? PALETTE_ITEMS.filter((i) => i.label.toLowerCase().includes(t)) : [...PALETTE_ITEMS];
  }, [q]);

  useEffect(() => {
    const show = () => {
      returnTo.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
      setQ("");
      setActive(0);
      setOpen(true);
    };
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        show();
      }
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener(OPEN_PALETTE_EVENT, show);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener(OPEN_PALETTE_EVENT, show);
    };
  }, []);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  function close() {
    setOpen(false);
    returnTo.current?.focus?.();
  }

  function go(href: string) {
    setOpen(false);
    const onHome = window.location.pathname === "/";
    window.location.assign(href.startsWith("#") && !onHome ? `/${href}` : href);
  }

  function onInputKey(e: React.KeyboardEvent) {
    if (e.key === "Escape") return close();
    if (!items.length) return;
    if (e.key === "ArrowDown") { e.preventDefault(); setActive((a) => (a + 1) % items.length); }
    if (e.key === "ArrowUp") { e.preventDefault(); setActive((a) => (a - 1 + items.length) % items.length); }
    if (e.key === "Enter") { e.preventDefault(); go(items[active].href); }
  }

  if (!open) return null;
  const listId = `${uid}-list`;
  const optId = (i: number) => `${uid}-opt-${i}`;

  return (
    <div className="ph-palette-scrim" onMouseDown={(e) => e.target === e.currentTarget && close()}>
      <div role="dialog" aria-modal="true" aria-label="Lompat ke" className="ph-palette">
        <input
          ref={inputRef}
          role="combobox"
          aria-expanded="true"
          aria-controls={listId}
          aria-activedescendant={items.length ? optId(Math.min(active, items.length - 1)) : undefined}
          aria-autocomplete="list"
          aria-label="Cari bahagian atau halaman"
          placeholder="Lompat ke bahagian atau halaman…"
          autoComplete="off"
          value={q}
          onChange={(e) => { setQ(e.target.value); setActive(0); }}
          onKeyDown={onInputKey}
          className="ph-palette-input"
        />
        <ul id={listId} role="listbox" aria-label="Hasil" className="ph-palette-list">
          {items.map((it, i) => (
            <li
              key={it.href}
              id={optId(i)}
              role="option"
              aria-selected={i === active}
              onMouseMove={() => setActive(i)}
              onClick={() => go(it.href)}
              className="ph-palette-opt"
            >
              <span>{it.label}</span>
              <span className="ph-palette-hint">{it.hint}</span>
            </li>
          ))}
        </ul>
        {!items.length && <p role="status" className="ph-palette-empty">Tiada padanan. Cuba kata lain.</p>}
        <p className="ph-palette-foot" aria-hidden="true"><kbd>↑</kbd><kbd>↓</kbd> pilih <kbd>↵</kbd> pergi <kbd>Esc</kbd> tutup</p>
      </div>
    </div>
  );
}
