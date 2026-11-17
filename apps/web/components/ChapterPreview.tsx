import { CHAPTERS } from "@/src/content";
import { EBOOK_COVERS } from "@/src/ebook-covers";

/**
 * Chapter & A4 ebook preview section (Section 04).
 *
 * Uses the real A4 ebook cover assets from docs/brand/preview rendered into
 * apps/web/public/ebooks/ at exact A4 portrait aspect ratio (210:297), avoiding
 * duplication with the six charcoal paintings in Section 05.
 */
export function ChapterPreview() {
  return (
    <div className="mx-auto flex max-w-grid flex-col gap-10">
      <div>
        <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
          <h3 className="font-display text-xl text-fg">Koleksi Ebook Semasa (Pratonton A4)</h3>
          <span className="text-xs uppercase tracking-caps text-fg-accent">
            {EBOOK_COVERS.length} judul A4 dalam folder koleksi
          </span>
        </div>
        <div
          className="ph-ebook-shelf"
          role="region"
          aria-label="Pratonton kulit ebook A4 semasa"
          tabIndex={0}
        >
          {EBOOK_COVERS.map((ebook) => (
            <figure key={ebook.slug} className="flex flex-col gap-2.5">
              <div className="ph-a4-cover">
                <picture>
                  <source srcSet={ebook.webp} type="image/webp" />
                  <img
                    src={ebook.jpg}
                    alt={`Kulit A4 ebook ${ebook.title}`}
                    width={ebook.width}
                    height={ebook.height}
                    loading="lazy"
                    decoding="async"
                  />
                </picture>
              </div>
              <figcaption className="flex flex-col gap-0.5">
                <span className="text-[11px] font-semibold uppercase tracking-caps text-fg-accent">{ebook.pages}</span>
                <span className="font-display text-base leading-snug text-fg">{ebook.title}</span>
                <span className="text-xs leading-relaxed text-fg-muted">{ebook.summary}</span>
              </figcaption>
            </figure>
          ))}
        </div>
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
