"use client";

import { useState } from "react";
import { CARDS, drawCard, scoreBingo, type CardCategory } from "@/src/games/cards";

const CATEGORY_STYLE: Record<CardCategory, { label: string; badgeClass: string; borderClass: string }> = {
  red: { label: "Red Flag", badgeClass: "bg-red-100 text-red-900 border-red-300", borderClass: "border-red-300" },
  green: { label: "Green Flag", badgeClass: "bg-sage text-green-900 border-green-700/30", borderClass: "border-green-700/40" },
  luka: { label: "Luka & Pulih", badgeClass: "bg-gold/15 text-ink-grove border-gold", borderClass: "border-gold" },
};

const BINGO_ROWS: string[][] = [
  CARDS.slice(0, 4).map((c) => c.id),
  CARDS.slice(4, 8).map((c) => c.id),
  CARDS.slice(8, 12).map((c) => c.id),
];

export function KadJujurHati() {
  const [index, setIndex] = useState(0);
  const [marked, setMarked] = useState<string[]>([]);

  const card = drawCard(index);
  const cardPosition = (((index % CARDS.length) + CARDS.length) % CARDS.length) + 1;
  const isMarked = marked.includes(card.id);
  const meta = CATEGORY_STYLE[card.category];
  const bingoLines = BINGO_ROWS.reduce((sum, row) => sum + scoreBingo(marked, row), 0);

  function toggleMark(id: string) {
    setMarked((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  }

  const threadsText = encodeURIComponent(
    `Kad Jujur Hati (${card.title}): "${card.prompt}" #JujurHati`,
  );

  return (
    <div className="ph-card mx-auto flex max-w-reading flex-col gap-5 p-6">
      <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-green-900">
        <span>Kad Jujur Hati: tarik kad, baca, dan kongsi di Threads dengan #JujurHati</span>
        <span className="font-mono text-xs text-muted-grove">
          Kad {cardPosition} / {CARDS.length}
        </span>
      </div>

      <article className={`rounded-lg border-2 bg-cream/70 p-5 ${meta.borderClass}`}>
        <div className="flex items-center justify-between gap-2">
          <span className={`inline-block rounded-full border px-2.5 py-0.5 text-xs font-medium ${meta.badgeClass}`}>
            {meta.label}
          </span>
          <span className="text-xs text-muted-grove">Kategori: {card.category}</span>
        </div>
        <h3 className="mt-3 font-display text-2xl text-green-900">{card.title}</h3>
        <p className="mt-2 text-base leading-relaxed text-ink-grove">{card.prompt}</p>
      </article>

      <div className="flex flex-wrap gap-2.5">
        <button type="button" className="btn-ghost min-h-tap" onClick={() => setIndex((i) => i - 1)}>
          Kad sebelum
        </button>
        <button type="button" className="ph-cta min-h-tap" onClick={() => setIndex((i) => i + 1)}>
          Tarik kad baru
        </button>
        <button type="button" className="btn-ghost min-h-tap" onClick={() => toggleMark(card.id)}>
          {isMarked ? "Tanda dibuang" : "Tanda untuk Bingo"}
        </button>
        <a
          href={`https://www.threads.net/intent/post?text=${threadsText}`}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-ghost min-h-tap"
        >
          Kongsi kad di Threads
        </a>
      </div>

      <div className="border-t border-daylight-edge pt-4">
        <div className="mb-2 flex items-center justify-between text-sm text-muted-grove">
          <span>Papan Bingo Hati: {marked.length} / {CARDS.length} sudah ditanda</span>
          {bingoLines > 0 && <span className="font-medium text-green-900">Bingo! {bingoLines} baris lengkap</span>}
        </div>
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
          {CARDS.map((c, i) => {
            const selected = marked.includes(c.id);
            const active = i === cardPosition - 1;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => {
                  setIndex(i);
                  toggleMark(c.id);
                }}
                aria-pressed={selected}
                className={
                  selected
                    ? "min-h-tap rounded border border-green-700 bg-green-700 px-2 py-1.5 text-xs font-medium text-cream"
                    : active
                      ? "min-h-tap rounded border border-gold bg-sage px-2 py-1.5 text-xs text-green-900"
                      : "min-h-tap rounded border border-daylight-edge bg-cream/60 px-2 py-1.5 text-xs text-ink-grove hover:border-green-700/50"
                }
              >
                {c.title}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
