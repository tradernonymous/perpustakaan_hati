"use client";

import { useState } from "react";

type Excerpt = {
  id: string;
  label: string;
  source: string;
  quote: string;
  reflection: string;
};

const EXCERPTS: Excerpt[] = [
  {
    id: "diam",
    label: "Ruang vs Hukuman",
    source: "Edisi Poket · Ruang atau Hukuman",
    quote: "“Saya perlukan masa, nanti kita bincang.”",
    reflection: "Ayat yang sama boleh menjadi ruang yang matang, atau pintu yang ditutup tanpa tarikh pulang.",
  },
  {
    id: "perkara-kecil",
    label: "Perkara Kecil",
    source: "Edisi Poket · Hati Kenyang",
    quote: "Kasih sayang jarang jatuh dari langit.",
    reflection: "Ia turun setiap hari dalam perkara kecil: nada suara yang lembut dan kehadiran yang benar-benar mendengar.",
  },
  {
    id: "suara",
    label: "Pulang Kepada Diri",
    source: "Edisi Poket · Suara Sendiri",
    quote: "Suara sendiri tidak hilang.",
    reflection: "Ia cuma terlalu lama ditahan demi menjaga hati orang lain. Kali ini, beri ruang untuk mendengar diri sendiri.",
  },
];

/**
 * Interactive 60-second excerpt reader on the Hero collector plinth.
 * Gives visitors an immediate tactile "look inside" the actual Malay editions
 * before scrolling or subscribing.
 */
export function HeroExcerptPreview() {
  const [activeId, setActiveId] = useState(EXCERPTS[0].id);
  const current = EXCERPTS.find((e) => e.id === activeId) ?? EXCERPTS[0];

  return (
    <div className="flex flex-col gap-3 text-left">
      <div className="flex items-center justify-between gap-2">
        <span className="ph-caps text-[0.65rem] text-gold-light">Intai 60 saat</span>
        <span className="text-[11px] text-green-300">{current.source}</span>
      </div>

      <div className="flex flex-wrap gap-1.5" role="tablist" aria-label="Pilih petikan bacaan">
        {EXCERPTS.map((item) => {
          const selected = item.id === current.id;
          return (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => setActiveId(item.id)}
              className={`min-h-[34px] rounded-pill border px-2.5 py-1 text-xs transition ${
                selected
                  ? "border-gold-light/70 bg-gold-light/15 font-semibold text-cream"
                  : "border-forest-edge bg-forest-night/40 text-green-300 hover:border-gold-light/40"
              }`}
            >
              {item.label}
            </button>
          );
        })}
      </div>

      <blockquote className="rounded border border-forest-edge/80 bg-forest-night/55 p-3.5">
        <p className="font-display text-lg leading-snug text-gold-light">{current.quote}</p>
        <p className="mt-1.5 text-sm leading-relaxed text-on-dark-muted">{current.reflection}</p>
      </blockquote>

      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-green-300">
        <span>Baca 1 kad sehari · Percuma</span>
        <a href="#katalog" className="font-semibold text-gold-light underline decoration-gold-light/40 underline-offset-4 hover:text-cream">
          Lihat semua koleksi A4
        </a>
      </div>
    </div>
  );
}
