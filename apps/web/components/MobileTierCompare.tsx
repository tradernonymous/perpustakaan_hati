"use client";

import { useState } from "react";

type Edition = { id: string; name: string; price: string; cover: string | null; href: string };
type Row = { label: string; values: Record<string, string> };

export function MobileTierCompare({ editions, rows }: { editions: Edition[]; rows: Row[] }) {
  const [pair, setPair] = useState([1, 2]);
  const [differences, setDifferences] = useState(false);
  const chosen = pair.map((index) => editions[index]);
  return (
    <section className="grid gap-4 md:hidden" aria-labelledby="mobile-compare">
      <h3 id="mobile-compare" className="font-display text-xl">Bandingkan dua edisi</h3>
      <div className="grid grid-cols-2 gap-2">
        {pair.map((selected, slot) => (
          <label key={slot} className="grid min-w-0 gap-1 text-sm">
            Edisi {slot + 1}
            <select className="min-h-tap w-full rounded border border-line bg-surface-raised px-1"
              value={selected} onChange={(event) => {
                const index = Number(event.target.value);
                setPair((current) => current.map((value, position) => position === slot ? index : value));
              }}>
              {editions.map((edition, index) => (
                <option key={edition.id} value={index} disabled={index === pair[1 - slot]}>{edition.name}</option>
              ))}
            </select>
          </label>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-2">
        {chosen.map((edition) => (
          <article key={edition.id} className="ph-card grid min-w-0 content-start gap-2 p-2 text-center">
            {edition.cover && <img src={edition.cover} alt="" width={88} height={124} className="mx-auto h-auto w-[72px] rounded" loading="lazy" />}
            <h4 className="font-display text-sm">{edition.name}</h4>
            <p className="text-sm font-semibold text-fg-healing">{edition.price}</p>
            <a href={edition.href} className="btn-ghost min-h-tap text-sm">{edition.id === "poket" ? "Dapatkan percuma" : "Lihat edisi"}</a>
          </article>
        ))}
      </div>
      <label className="flex min-h-tap items-center gap-2">
        <input type="checkbox" checked={differences} onChange={(event) => setDifferences(event.target.checked)} />
        Tunjuk perbezaan sahaja
      </label>
      <dl className="grid gap-3">
        {rows.filter(({ values }) => !differences || values[chosen[0].id] !== values[chosen[1].id]).map(({ label, values }) => (
          <div key={label} className="ph-card grid grid-cols-2 gap-3 p-3 text-sm">
            <dt className="col-span-2 font-semibold">{label}</dt>
            {chosen.map((edition) => <dd key={edition.id}><span className="sr-only">{edition.name}: </span>{values[edition.id]}</dd>)}
          </div>
        ))}
      </dl>
      <div className="grid grid-cols-2 gap-2">
        {chosen.map((edition) => <a key={edition.id} href={edition.href} className="btn-ghost min-h-tap text-center text-sm">{edition.name}</a>)}
      </div>
    </section>
  );
}
