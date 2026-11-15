import { ILLUSTRATIONS } from "@/src/illustrations";
import { Illustration } from "@/components/Illustration";

/**
 * The six plates of Edisi Poket.
 *
 * A horizontal scroller on a phone (one plate at a time, scroll-snap) and
 * a three-column grid on a wide screen. The scroller is focusable so a
 * keyboard user can scroll it with the arrow keys, and it is labelled so
 * a screen reader announces what the region holds.
 */
export function PlateGallery() {
  return (
    <div
      className="ph-gallery"
      role="region"
      aria-label="Enam ilustrasi Edisi Poket"
      tabIndex={0}
    >
      {ILLUSTRATIONS.map((illustration) => (
        <figure key={illustration.slug}>
          <div className="ph-gallery-fig">
            <Illustration illustration={illustration} sizes="(min-width: 768px) 21rem, 78vw" />
          </div>
          <figcaption>{illustration.caption}</figcaption>
        </figure>
      ))}
    </div>
  );
}
