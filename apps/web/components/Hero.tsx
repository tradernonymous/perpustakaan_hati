import { HeroBook } from "@/components/HeroBook";
import { ReadingProgress } from "@/components/ReadingProgress";

const CHIPS = ["Percuma untuk bermula", "Bahasa Melayu", "Sesuai dibaca di telefon"];

const LESSONS = [
  { title: "Baca 60 saat sehari", text: "Satu kad pendek untuk masa menunggu bas atau train." },
  { title: "Kad Refleksi", text: "Namakan apa yang kamu rasa, sebelum bertindak balas." },
  { title: "7 Hari Reset", text: "Tujuh langkah kecil, satu ayat setiap hari." },
];

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
      <ReadingProgress />

      <div className="mx-auto grid max-w-grid items-center gap-10 md:grid-cols-[1.2fr_0.8fr]">
        <div className="flex flex-col items-center gap-6 text-center md:items-start md:text-left">
          <p className="ph-kicker w-full md:w-auto animate-fade-up" style={{ animationDelay: "60ms" }}>oleh @rahimam</p>
          <h1 className="ph-hero ph-foil-emerald ph-sheen text-5xl md:text-7xl animate-fade-up" style={{ animationDelay: "180ms" }}>Perpustakaan Hati</h1>
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

        <div className="animate-fade-up" style={{ animationDelay: "240ms" }}>
          <HeroBook name="Edisi Poket" />
        </div>
      </div>

      <ul className="mx-auto mt-12 grid max-w-grid gap-4 sm:grid-cols-3 animate-fade-up" style={{ animationDelay: "720ms" }} aria-label="Cara belajar">
        {LESSONS.map((l) => (
          <li key={l.title} className="ph-glass p-4">
            <p className="font-display text-lg text-gold-light">{l.title}</p>
            <p className="mt-1 text-sm text-on-dark">{l.text}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
