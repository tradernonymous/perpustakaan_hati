type Props = { name: string; src: string | null; seal?: string; className?: string };

/**
 * Cover slot for a book. Until the real cover art exists, the slot shows a
 * brand cover-in-waiting built from the design system (the eBook cover
 * recipe: forest stage, double gilt frame, book-heart emblem, tier seal) and
 * is still labelled "Kulit buku akan datang" so nobody mistakes it for the
 * final art. Drop the real image in public/products/ and set Tier.cover.
 */
export function ProductCover({ name, src, seal, className = "" }: Props) {
  if (src) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={src} alt={`Kulit ${name}`} data-cover-slot className={`h-auto w-full rounded object-cover ${className}`} />;
  }
  return (
    <div
      data-cover-slot
      role="img"
      aria-label={`Kulit ${name} belum sedia`}
      className={`ph-cover-frame relative flex aspect-[3/4] w-full flex-col items-center justify-center gap-3 overflow-hidden rounded p-6 text-center ${className}`}
    >
      <svg viewBox="0 0 600 420" className="w-3/5 max-w-[180px]" aria-hidden="true" focusable="false">
        <image href="/brand/emblem-book-heart.svg" width="600" height="420" />
      </svg>
      <span className="ph-caps text-[0.6rem] text-gold-light">Perpustakaan Hati</span>
      <span className="font-display text-2xl leading-tight text-cream">{name}</span>
      {seal && (
        <svg viewBox="0 0 600 600" className="h-16 w-16" aria-hidden="true" focusable="false">
          <image href={seal} width="600" height="600" />
        </svg>
      )}
      <span className="mt-1 text-xs uppercase tracking-kicker text-on-dark-muted">Kulit buku akan datang</span>
    </div>
  );
}
