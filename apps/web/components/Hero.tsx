import { OptInForm } from "@/components/OptInForm";

/** A short introduction, followed by the existing free-edition signup. */
export function Hero() {
  return (
    <>
      <section id="atas" aria-labelledby="hero-heading" className="ph-day-stage relative overflow-hidden border-b border-line px-5 py-14 sm:py-20">
        <div className="relative mx-auto max-w-3xl text-center">
          <p className="mb-5 text-xs font-semibold uppercase tracking-[0.18em] text-fg-accent">Perpustakaan Hati · Bahasa Melayu</p>
          <h1 id="hero-heading" className="font-display text-[clamp(2.5rem,6vw,4.75rem)] leading-[1.08] tracking-tight text-fg">
            Bacaan kecil.<br /><span className="text-fg-healing">Ruang untuk pulih.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-fg-muted sm:text-lg">
            Tulisan tentang hubungan dan pemulihan diri, dalam Bahasa Melayu yang dekat di hati.
          </p>
          <div className="mt-7 flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:items-center">
            <a href="#percuma" className="ph-cta min-h-cta-mobile inline-flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4">Mulakan percuma</a>
            <a href="#edisi" className="btn-ghost min-h-cta-mobile inline-flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4">Lihat koleksi</a>
          </div>
          <p className="mt-4 text-xs text-fg-muted">Mulakan dengan Edisi Poket. Baca mengikut rentak kamu.</p>
        </div>
      </section>
      <section id="percuma" aria-labelledby="percuma-heading" className="scroll-mt-20 px-5 py-10 sm:py-12">
        <div className="mx-auto max-w-[520px]">
          <h2 id="percuma-heading" className="mb-5 text-center font-display text-2xl text-fg">Edisi Poket, percuma</h2>
          <OptInForm />
        </div>
      </section>
    </>
  );
}
