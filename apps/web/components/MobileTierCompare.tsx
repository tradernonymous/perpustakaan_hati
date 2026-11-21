"use client";

import { useState } from "react";

type Edition = { id: string; name: string; price: string; cover: string | null; href: string };
type Row = { label: string; values: Record<string, string> };

export function MobileTierCompare({ editions, rows }: { editions: Edition[]; rows: Row[] }) {
  const [pair, setPair] = useState([0, 1]);
  const [differences, setDifferences] = useState(false);
  const chosen = pair.map((index) => editions[index]);
  const visibleRows = rows.filter(({ values }) => !differences || values[chosen[0].id] !== values[chosen[1].id]);

  return (
    <section className="ph-compare-mobile mx-auto max-w-reading" aria-labelledby="mobile-compare">
      <h3 id="mobile-compare" className="mb-3 text-center font-display text-xl">Bandingkan dua edisi</h3>
      <div className="grid grid-cols-2 gap-2.5">
        {chosen.map((edition, slot) => (
          <div key={slot} className="grid min-w-0 content-start justify-items-center gap-2 rounded-lg border border-line bg-surface-raised p-2.5">
            <label className="w-full min-w-0">
              <span className="sr-only">Edisi {slot + 1}</span>
              <select className="min-h-tap w-full min-w-0 rounded border border-line bg-surface-soft px-1.5 text-base"
                value={pair[slot]} onChange={(event) => {
                  const index = Number(event.target.value);
                  setPair((current) => current.map((value, position) => position === slot ? index : value));
                }}>
                {editions.map((option, index) => (
                  <option key={option.id} value={index} disabled={index === pair[1 - slot]}>{option.name.replace(/^Edisi /, "")}</option>
                ))}
              </select>
            </label>
            {edition.cover && (
              <div className="ph-book-stage w-[72px]" data-tier={edition.id}>
                <div className="ph-book-object">
                  <img src={edition.cover} alt="" width={72} height={101} className="h-auto w-[64px] rounded" loading="lazy" />
                </div>
              </div>
            )}
            <p className="text-center text-sm font-semibold text-fg-healing">{edition.price}</p>
          </div>
        ))}
      </div>
      <label className="my-2 flex min-h-tap cursor-pointer items-center gap-2.5 px-1 text-sm text-fg">
        <input type="checkbox" className="h-5 w-5 shrink-0 accent-green-500" checked={differences} onChange={(event) => setDifferences(event.target.checked)} />
        Tunjuk perbezaan sahaja
      </label>
      <dl className="divide-y divide-line rounded-lg border border-line bg-surface-raised">
        {visibleRows.map(({ label, values }) => (
          <div key={label} className="grid grid-cols-2 gap-x-2 gap-y-1.5 px-3 py-2.5 text-sm leading-snug">
            <dt className="col-span-2 text-center font-medium text-fg">{label}</dt>
            {chosen.map((edition) => (
              <dd key={edition.id} className={`min-w-0 break-words text-center ${values[edition.id] === "Termasuk" ? "font-medium text-fg-healing" : "text-fg-muted"}`}>
                <span className="sr-only">{edition.name}: </span>{values[edition.id]}
              </dd>
            ))}
          </div>
        ))}
      </dl>
      {visibleRows.length === 0 && <p role="status" className="px-3 text-center text-sm text-fg-muted">Tiada perbezaan untuk dua edisi ini.</p>}
      <div className="mt-3 grid grid-cols-2 gap-2.5">
        {chosen.map((edition) => (
          <a key={edition.id} href={edition.href} aria-label={edition.id === "poket" ? "Dapatkan Edisi Poket percuma" : `Lihat ${edition.name}`}
            className="btn-ghost min-w-0 px-2 py-2 text-center text-sm leading-snug">
            {edition.id === "poket" ? "Dapatkan percuma" : "Lihat edisi"}
          </a>
        ))}
      </div>
    </section>
  );
}
