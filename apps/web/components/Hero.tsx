const CHIPS = ["Percuma untuk bermula", "Bahasa Melayu", "Sesuai dibaca di telefon"];

const EMBERS = [
  { cx: 140, cy: 220, r: 3, delay: "0s" },
  { cx: 320, cy: 140, r: 2, delay: "1.2s" },
  { cx: 520, cy: 300, r: 2.6, delay: "2.4s" },
  { cx: 760, cy: 110, r: 2, delay: "0.8s" },
  { cx: 980, cy: 260, r: 3.2, delay: "3.1s" },
  { cx: 1120, cy: 180, r: 1.8, delay: "1.7s" },
];

export function Hero() {
  return (
    <section id="atas" className="ph-stage relative overflow-hidden px-5 pb-16 pt-12 md:pb-24 md:pt-20">
      {/* Animated ember field — drifting warm sparks behind the headline. */}
      <svg
        className="ph-ember pointer-events-none absolute inset-0 h-full w-full"
        viewBox="0 0 1200 800"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden="true"
        focusable="false"
      >
        {EMBERS.map((e, i) => (
          <circle
            key={i}
            cx={e.cx}
            cy={e.cy}
            r={e.r}
            fill="#f2b85c"
            className="ph-ember"
            style={i % 2 === 0 ? { animationDelay: e.delay } : undefined}
          />
        ))}
      </svg>

      <div className="mx-auto grid max-w-grid items-center gap-10 md:grid-cols-[1.2fr_0.8fr]">
        <div className="flex flex-col items-center gap-6 text-center md:items-start md:text-left">
          <p className="ph-kicker w-full md:w-auto animate-fade-up" style={{ animationDelay: "60ms" }}>oleh @rahimam</p>
          <h1 className="ph-hero ph-foil-emerald text-5xl md:text-7xl animate-fade-up" style={{ animationDelay: "180ms" }}>Perpustakaan Hati</h1>
          <p className="font-display text-2xl italic text-gold-light md:text-3xl animate-fade-up" style={{ animationDelay: "300ms" }}>
            Karya untuk jiwa yang pernah terluka
          </p>
          <p className="max-w-prose text-base leading-relaxed text-on-dark md:text-lg animate-fade-up" style={{ animationDelay: "420ms" }}>
            Tulisan yang memulihkan, dalam Bahasa Melayu yang dekat di hati. Mulakan dengan satu buku
            kecil yang boleh dibaca sementara menunggu bas atau train.
          </p>
          <div className="flex w-full flex-col items-center gap-3 sm:w-auto sm:flex-row animate-fade-up" style={{ animationDelay: "540ms" }}>
            <a href="#percuma" className="ph-cta min-h-cta-mobile w-full items-center justify-center sm:w-auto">
              Mula dengan Edisi Poket, percuma
            </a>
            <a href="#edisi" className="btn-ghost min-h-cta-mobile w-full justify-center sm:w-auto">
              Lihat semua edisi
            </a>
          </div>
          <ul className="flex flex-wrap justify-center gap-2 md:justify-start animate-fade-up" style={{ animationDelay: "660ms" }} aria-label="Kelebihan">
            {CHIPS.map((c) => (
              <li key={c} className="rounded-pill border border-forest-edge bg-forest-raised px-3 py-1 text-xs text-green-300">
                {c}
              </li>
            ))}
          </ul>
        </div>

        <div className="relative mx-auto flex w-full max-w-[280px] justify-center animate-fade-up" style={{ animationDelay: "240ms" }} aria-hidden="true">
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
