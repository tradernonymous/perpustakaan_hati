import { TESTIMONIALS } from "@/src/content";

export function Testimonials() {
  return (
    <div className="mx-auto grid max-w-grid gap-5 md:grid-cols-3">
      {TESTIMONIALS.map((t) => (
        <figure key={t.quote} className="ph-card flex flex-col gap-3 p-5">
          {t.placeholder && (
            <span className="w-fit rounded border border-gold-deep px-2 py-0.5 text-xs font-semibold uppercase tracking-[0.18em] text-gold-light">
              CONTOH
            </span>
          )}
          <blockquote className="border-l-2 border-gold-deep pl-3 font-display text-xl italic text-on-dark">
            {t.quote}
          </blockquote>
          <figcaption className="text-sm text-on-dark-muted">{t.who}</figcaption>
        </figure>
      ))}
    </div>
  );
}
