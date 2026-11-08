import { TESTIMONIALS } from "@/src/content";

export function Testimonials() {
  return (
    <div className="mx-auto grid max-w-grid gap-5 md:grid-cols-3">
      {TESTIMONIALS.map((t) => (
        <figure key={t.quote} className="ph-lux ph-card flex flex-col gap-3 p-5">
          {t.placeholder && (
            <span className="w-fit rounded border border-gold-deep px-2 py-0.5 text-xs font-semibold uppercase tracking-[0.18em] text-green-900">
              CONTOH
            </span>
          )}
          <blockquote className="border-l-2 border-gold-deep pl-3 font-display text-xl italic text-ink-grove">
            {t.quote}
          </blockquote>
          <figcaption className="text-sm text-muted-grove">{t.who}</figcaption>
        </figure>
      ))}
    </div>
  );
}
