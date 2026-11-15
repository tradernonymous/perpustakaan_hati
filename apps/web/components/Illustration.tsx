import type { Illustration as IllustrationData } from "@/src/illustrations";

type Props = {
  illustration: IllustrationData;
  /** The `sizes` attribute: how wide the image renders at each breakpoint. */
  sizes?: string;
  /** True for the above-the-fold hero image: eager, high priority, no lazy. */
  priority?: boolean;
  className?: string;
};

/**
 * A painterly illustration, served as WebP with a JPEG fallback.
 *
 * Plain <img> with a <picture> element rather than next/image: the
 * production image optimizer needs sharp at runtime, and sharp is a
 * devDependency here, so a Railway deploy would 500 on every optimized
 * image request. The files are pre-rendered by
 * scripts/build-illustrations.mjs, so they are static and already
 * smaller than the optimizer would produce.
 *
 * Width and height are always set, so the browser reserves the box before
 * the image loads and the page does not shift.
 */
export function Illustration({
  illustration,
  sizes = "(min-width: 1024px) 36rem, 100vw",
  priority = false,
  className = "",
}: Props) {
  const srcSet = illustration.variants.map((v) => `/illustrations/${v.webp} ${v.width}w`).join(", ");
  const fallback = illustration.variants.find((v) => v.width === 768) ?? illustration.variants.at(-1);

  return (
    <picture>
      <source type="image/webp" srcSet={srcSet} sizes={sizes} />
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={`/illustrations/${fallback?.webp.replace(".webp", ".jpg") ?? ""}`}
        alt={illustration.alt}
        width={illustration.width}
        height={illustration.height}
        loading={priority ? "eager" : "lazy"}
        decoding={priority ? "sync" : "async"}
        fetchPriority={priority ? "high" : "auto"}
        className={className}
      />
    </picture>
  );
}
