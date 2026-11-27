import type { Tier } from "@/src/content";

type Props = {
  name: string;
  src: string | null;
  seal?: string;
  /** The tier this cover belongs to. Drives the cover's metal and light. */
  tier?: Tier["id"];
  className?: string;
};

/**
 * Cover slot for a book. Until the real cover art exists, the slot shows a
 * brand cover-in-waiting built from the design system (the eBook cover
 * recipe: forest stage, double gilt frame, book-heart emblem, tier seal) and
 * is still labelled "Kulit buku akan datang" so nobody mistakes it for the
 * final art. Drop the real image in public/products/ and set Tier.cover.
 *
 * With a tier, the cover is framed in that tier's own metal and lit by that
 * tier's own colour, so the three editions never look like the same book in
 * three sizes. The tier colour never travels alone: the seal carries the
 * tier's silhouette and the name is always on the cover.
 */
export function ProductCover({ name, src, seal, tier, className = "" }: Props) {
  if (src) {
    // eslint-disable-next-line @next/next/no-img-element
    return (
      <img
        src={src}
        alt={`Kulit ${name}`}
        data-cover-slot
        data-tier={tier}
        className={`h-auto w-full rounded object-cover ${className}`}
      />
    );
  }
  return (
    <div
      data-cover-slot
      data-tier={tier}
      role="img"
      aria-label={`Kulit ${name} belum sedia`}
      className={`ph-cover-frame ph-tier-cover relative flex aspect-[3/4] w-full flex-col items-center justify-center gap-3 overflow-hidden rounded p-6 text-center ${className}`}
    >
      <svg viewBox="0 0 600 420" className="w-3/5 max-w-[180px]" aria-hidden="true" focusable="false">
        <image href="/brand/emblem-book-heart.svg" width="600" height="420" />
      </svg>
      <span className="ph-caps text-[0.6rem] text-gold-light">Perpustakaan Hati</span>
      <span className="font-display text-2xl leading-tight text-cream">{name}</span>
      {seal && (
        <svg viewBox="0 0 600 600" className="ph-coin ph-coin-edge h-24 w-24" aria-hidden="true" focusable="false">
          <image href={seal} width="600" height="600" />
        </svg>
      )}
      <span className="mt-1 text-xs uppercase tracking-kicker text-on-dark-muted">Kulit buku akan datang</span>
    </div>
  );
}
