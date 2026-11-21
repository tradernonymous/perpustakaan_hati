"use client";

import { useState } from "react";

type BookPage = { title: string; text: string };

const DEFAULT_PAGES: BookPage[] = [
  { title: "Kad Refleksi", text: "Apa yang kamu rasa bila dia belum balas?" },
  { title: "Tujuh Hari Reset", text: "Hari 1 — Namakan perasaan. Satu perkataan: kecewa, takut, marah, rindu." },
  { title: "Skrip Bincang Hati ke Hati", text: "“Aku perlukan masa untuk fikir.”" },
];

type Props = {
  name?: string;
  cover?: string;
  seal?: string;
  pages?: BookPage[];
};

/**
 * 3D interactive preview book in the Hero section.
 * Fixes screen-reader layering (aria-hidden on covered faces) and eliminates
 * duplicate next-page controls.
 */
export function HeroBook({
  name = "Edisi Poket",
  cover = "/ebooks/cover-poket.png",
  seal,
  pages = DEFAULT_PAGES,
}: Props) {
  const [page, setPage] = useState(0);
  const [open, setOpen] = useState(false);
  const active = pages[page];

  return (
    <div className="ph-book-scene mx-auto max-w-[340px]" aria-label={`Buku interaktif ${name}`}>
      <div className="ph-book-shadow" aria-hidden="true" />
      {seal && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={seal} alt="" width={96} height={96} className="ph-book-seal ph-coin" />
      )}
      <div className="ph-book-3d" data-page={page}>
        <div className="ph-book-spine" aria-hidden="true" />
        <div className="ph-book-pages" aria-hidden="true" />
        <div className="ph-book-cover" aria-hidden={open}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={cover} alt={`Kulit ${name}`} width={599} height={902} className="ph-book-art" />
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
