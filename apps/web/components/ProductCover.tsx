type Props = { name: string; src: string | null; className?: string };

/**
 * Cover slot for a book. Until the real cover art exists, a labelled dashed box
 * holds the space so nothing has to be redesigned later. Drop the image in
 * public/products/ and set Tier.cover to its path.
 */
export function ProductCover({ name, src, className = "" }: Props) {
  if (src) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={src} alt={`Kulit ${name}`} data-cover-slot className={`h-auto w-full rounded object-cover ${className}`} />;
  }
  return (
    <div
      data-cover-slot
      aria-label={`Kulit ${name} belum sedia`}
      className={`flex aspect-[3/4] w-full flex-col items-center justify-center gap-2 rounded border-2 border-dashed border-forest-edge bg-forest-soft p-4 text-center ${className}`}
    >
      <span aria-hidden="true" className="text-2xl text-gold">❖</span>
      <span className="font-display text-sm text-gold-light">Kulit buku akan datang</span>
      <span className="text-xs text-on-dark-muted">{name}</span>
    </div>
  );
}
