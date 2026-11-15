import { CHAPTERS } from "@/src/content";
import { ILLUSTRATIONS } from "@/src/illustrations";
import { Illustration } from "@/components/Illustration";

/**
 * The chapter preview, as a card grid (Design System 3.4).
 *
 * The confirmed chapters carry a plate from the edition's art so the grid
 * reads like a book rather than a list. The held-back chapters stay
 * visibly pending: dashed card, no art, and the same "Tajuk akan
 * diumumkan" wording the old list used.
 */
export function ChapterPreview() {
  return (
    <div className="ph-chapter-grid mx-auto max-w-grid">
      {CHAPTERS.map((c, i) => {
        const art = c.pending ? undefined : ILLUSTRATIONS[i % ILLUSTRATIONS.length];
        return (
          <article key={c.no} className="ph-chapter-card ph-page-in" data-pending={c.pending ? "true" : "false"}>
            <p className="ph-chapter-num">Bab {c.no}</p>
            {art && (
              <div className="ph-chapter-art">
                <Illustration illustration={art} sizes="(min-width: 768px) 21rem, 92vw" />
              </div>
            )}
            <h3 className={`ph-title text-xl ${c.pending ? "italic text-green-800/70" : "text-green-900"}`}>
              {c.title}
            </h3>
            <p className="text-[15px] leading-relaxed text-ink-grove">{c.note}</p>
          </article>
        );
      })}
    </div>
  );
}
