"use client";

import { useState } from "react";
import { CARDS, drawCard } from "@/src/games/cards";

export function KadJujurHati() {
  const [index, setIndex] = useState(0);
  const [marked, setMarked] = useState<string[]>([]);
  const card = drawCard(index);

  return (
    <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-5">
      <p className="text-sm text-green-900">Kad Jujur Hati: tarik kad, baca, dan kongsi di Threads dengan #JujurHati</p>
      <article className="rounded border border-gold p-4">
        <h3 className="font-display text-xl text-green-900">{card.title}</h3>
        <p className="mt-2 text-ink-grove">{card.prompt}</p>
        <p className="mt-1 text-xs text-muted-grove">Kategori: {card.category}</p>
      </article>
      <div className="flex gap-3">
        <button className="ph-cta min-h-tap" onClick={() => setIndex(index + 1)}>Tarik kad baru</button>
        <button
          className="ph-cta min-h-tap"
          onClick={() => setMarked(marked.includes(card.id) ? marked.filter((id) => id !== card.id) : [...marked, card.id])}
        >
          {marked.includes(card.id) ? "Tanda dibuang" : "Tanda untuk Bingo"}
        </button>
      </div>
      <p className="text-sm text-muted-grove">{marked.length} / {CARDS.length} sudah ditanda</p>
    </div>
  );
}
