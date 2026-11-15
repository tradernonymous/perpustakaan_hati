"use client";

import { useState } from "react";

/**
 * 3D interactive preview book in the Hero section.
 * Fixes screen-reader layering (aria-hidden on covered faces) and eliminates
 * duplicate next-page controls.
 */
export function HeroBook({ name = "Edisi Poket" }: { name?: string }) {
  const [page, setPage] = useState(0);
  const [open, setOpen] = useState(false);
  const pages = [
    { title: "Kad Refleksi", text: "Namakan satu red flag dan satu green flag tanpa menghukum diri." },
    { title: "7 Hari Reset", text: "Satu langkah kecil hari ini. Baca 60 saat, kemudian tulis satu ayat." },
    { title: "Skrip untuk hari ini", text: "“Saya perlukan jeda 10 minit, kemudian kita sambung dengan tenang.”" },
  ];
  const active = pages[page];

  return (
    <div className="ph-book-scene mx-auto max-w-[340px]" aria-label={`Buku interaktif ${name}`}>
      <div className="ph-book-shadow" aria-hidden="true" />
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/brand/animated/seal-edisi-poket.svg" alt="" width={96} height={96} className="ph-book-seal ph-coin" />
      <div className="ph-book-3d" data-page={page}>
        <div className="ph-book-spine" aria-hidden="true" />
        <div className="ph-book-pages" aria-hidden="true" />
        <div className="ph-book-cover" aria-hidden={open}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/animated/emblem-book-heart.svg" alt="" width={150} height={105} className="ph-book-emblem" />
          <p className="ph-book-kicker">Perpustakaan Hati</p>
          <p className="ph-book-title">{name}</p>
          <p className="ph-book-subtitle">Karya untuk jiwa yang pernah terluka</p>
          <p className="ph-book-serial">Baca · Renung · Pulih</p>
          <div className="ph-book-sheen" aria-hidden="true" />
        </div>
        <div className="ph-book-open" key={page} data-open={open} aria-hidden={!open} aria-live="polite">
          <p className="ph-book-page-no">Muka surat {page + 1} / {pages.length}</p>
          <p className="ph-book-page-title">{active.title}</p>
          <p>{active.text}</p>
        </div>
      </div>
      <div className="ph-book-controls">
        <button
          type="button"
          onClick={() => {
            setOpen(true);
            setPage((v) => (v + pages.length - 1) % pages.length);
          }}
          aria-label="Muka surat sebelumnya"
        >
          ‹
        </button>
        {!open ? (
          <button
            type="button"
            onClick={() => setOpen(true)}
            aria-label="Buka muka surat seterusnya"
          >
            Buka muka surat seterusnya
          </button>
        ) : (
          <button
            type="button"
            onClick={() => setOpen(false)}
            aria-label="Kembali ke kulit buku"
          >
            Kulit buku
          </button>
        )}
        <button
          type="button"
          onClick={() => {
            setOpen(true);
            setPage((v) => (v + 1) % pages.length);
          }}
          aria-label="Muka surat seterusnya"
        >
          ›
        </button>
      </div>
    </div>
  );
}
