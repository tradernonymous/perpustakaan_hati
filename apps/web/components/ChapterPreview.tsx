import { CHAPTERS } from "@/src/content";
import { EBOOK_COVERS } from "@/src/ebook-covers";

/**
 * Real sample section: seven chapter cards with their A4 cover art.
 * The full A4 shelf lives in the catalog, so this section stays a sample
 * rather than a second product list.
 */
export function ChapterPreview() {
  return (
    <div className="mx-auto flex max-w-grid flex-col gap-6">
      <div className="ph-card flex flex-wrap items-center justify-between gap-3 p-4">
        <p className="text-sm text-fg-muted">Koleksi PDF Edisi Poket tersedia di Pustaka Saya selepas daftar.</p>
        <a href="/pustaka" className="btn-ghost min-h-tap">Buka koleksi Edisi Poket</a>
      </div>
      <div className="ph-chapter-grid">
        {CHAPTERS.map((c, i) => {
          const cover = EBOOK_COVERS[i % EBOOK_COVERS.length];
          const isTrailingOdd = CHAPTERS.length % 2 === 1 && i === CHAPTERS.length - 1;
          return (
            <article
              key={c.no}
              className={`ph-chapter-card ph-lux ph-page-in ${isTrailingOdd ? "ph-chapter-card-full" : ""}`}
              data-pending={c.pending ? "true" : "false"}
            >
              <div className="ph-book-stage">
                <div className="ph-book-object">
                  <div className="ph-chapter-art">
                    <picture>
                      <source srcSet={cover.webp} type="image/webp" />
                      <img
                        src={cover.jpg}
                        alt={`Kulit rujukan A4 ${cover.title}`}
                        width={cover.width}
                        height={cover.height}
                        loading="lazy"
                        decoding="async"
                      />
                    </picture>
                  </div>
                </div>
              </div>
              <div className="flex flex-col gap-1.5">
                <p className="ph-chapter-num">Bab {c.no}</p>
                <h3 className={`ph-title text-xl ${c.pending ? "italic text-fg-healing" : "text-fg"}`}>
                  {c.title}
                </h3>
                <p className="text-xs font-medium text-fg-accent">{cover.title} · {cover.pages}</p>
                <p className="text-[15px] leading-relaxed text-fg">{c.note}</p>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}
