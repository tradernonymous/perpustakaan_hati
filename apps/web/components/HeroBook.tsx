"use client";

import { useState } from "react";

/**
 * First creation: imported by Hero and covered by premium-experience tests.
 * Affected API: HeroBook accepts an optional display name; no data changes.
 * Data schemas: none; page content is a local display array.
 * User instruction: "just build it and please give me you best advanced,
 * futuristic, 3d, premium and educational design system and website design".
 */
export function HeroBook({ name = "Edisi Poket" }: { name?: string }) {
  const [page, setPage] = useState(0);
  const pages = [
    { title: "Kad Refleksi", text: "Namakan satu red flag dan satu green flag tanpa menghukum diri." },
    { title: "7 Hari Reset", text: "Satu langkah kecil hari ini. Baca 60 saat, kemudian tulis satu ayat." },
    { title: "Skrip untuk hari ini", text: "“Saya perlukan jeda 10 minit, kemudian kita sambung dengan tenang.”" },
  ];
  const active = pages[page];
  return (
    <div className="ph-book-scene" aria-label={`Buku interaktif ${name}`}>
      <div className="ph-book-shadow" aria-hidden="true" />
      <div className="ph-book-3d" data-page={page}>
        <div className="ph-book-spine" aria-hidden="true" />
        <div className="ph-book-pages" aria-hidden="true" />
        <div className="ph-book-cover">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/emblem-book-heart.svg" alt="" width={150} height={105} className="ph-book-emblem" />
          <p className="ph-book-kicker">Perpustakaan Hati</p>
          <p className="ph-book-title">{name}</p>
          <p className="ph-book-subtitle">Karya untuk jiwa yang pernah terluka</p>
          <p className="ph-book-serial">Baca · Renung · Pulih</p>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/seal-edisi-poket.svg" alt="" width={64} height={64} className="ph-book-seal" />
          <div className="ph-book-sheen" aria-hidden="true" />
        </div>
        <div className="ph-book-open" key={page} aria-live="polite">
          <p className="ph-book-page-no">Muka surat {page + 1} / {pages.length}</p>
          <h3>{active.title}</h3>
          <p>{active.text}</p>
        </div>
      </div>
      <div className="ph-book-controls">
        <button type="button" onClick={() => setPage((v) => (v + pages.length - 1) % pages.length)} aria-label="Muka surat sebelumnya">‹</button>
        <button type="button" onClick={() => setPage((v) => (v + 1) % pages.length)} aria-label="Buka muka surat seterusnya">Buka muka surat seterusnya</button>
        <button type="button" onClick={() => setPage((v) => (v + 1) % pages.length)} aria-label="Muka surat seterusnya">›</button>
      </div>
    </div>
  );
}
