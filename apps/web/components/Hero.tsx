const CHIPS = ["Percuma untuk bermula", "Bahasa Melayu", "Sesuai dibaca di telefon"];

export function Hero() {
  return (
    <section id="atas" className="ph-stage relative overflow-hidden px-5 pb-16 pt-12 md:pb-24 md:pt-20">
      <div className="mx-auto grid max-w-grid items-center gap-10 md:grid-cols-[1.2fr_0.8fr]">
        <div className="flex flex-col items-center gap-6 text-center md:items-start md:text-left">
          <p className="ph-kicker w-full md:w-auto">oleh @rahimam</p>
          <h1 className="ph-hero ph-foil-emerald text-5xl md:text-7xl">Perpustakaan Hati</h1>
          <p className="font-display text-2xl italic text-gold-light md:text-3xl">
            Karya untuk jiwa yang pernah terluka
          </p>
          <p className="max-w-prose text-base leading-relaxed text-on-dark md:text-lg">
            Tulisan yang memulihkan, dalam Bahasa Melayu yang dekat di hati. Mulakan dengan satu buku
            kecil yang boleh dibaca sementara menunggu bas atau train.
          </p>
          <div className="flex w-full flex-col items-center gap-3 sm:w-auto sm:flex-row">
            <a href="#percuma" className="ph-cta min-h-cta-mobile w-full items-center justify-center sm:w-auto">
              Mula dengan Edisi Poket, percuma
            </a>
            <a href="#edisi" className="btn-ghost min-h-cta-mobile w-full justify-center sm:w-auto">
              Lihat semua edisi
            </a>
          </div>
          <ul className="flex flex-wrap justify-center gap-2 md:justify-start" aria-label="Kelebihan">
            {CHIPS.map((c) => (
              <li key={c} className="rounded-pill border border-forest-edge bg-forest-raised px-3 py-1 text-xs text-green-300">
                {c}
              </li>
            ))}
          </ul>
        </div>

        <div className="relative mx-auto flex w-full max-w-[280px] justify-center" aria-hidden="true">
          <div className="absolute inset-0 -z-10 bg-glow-emerald" />
          <div className="ph-card flex aspect-[3/4] w-full flex-col items-center justify-center gap-4 border-l-[6px] border-l-green-600 p-6 shadow-depth-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/brand/emblem-book-heart.svg" alt="" width={112} height={112} className="h-28 w-28" />
            <p className="font-display text-xl text-gold-light">Edisi Poket</p>
            <p className="text-center text-xs uppercase tracking-kicker text-on-dark-muted">15 hingga 25 muka surat</p>
          </div>
        </div>
      </div>
    </section>
  );
}
