import { HeroBook } from "@/components/HeroBook";
import { HeroGlyphs } from "@/components/HeroGlyphs";
import { ReadingProgress } from "@/components/ReadingProgress";
import { SectionOrnament } from "@/components/SectionOrnament";

const CHIPS = ["Percuma untuk bermula", "Bahasa Melayu", "Sesuai dibaca di telefon"];

const LESSONS = [
  { title: "Baca 60 saat sehari", text: "Satu kad pendek untuk masa menunggu bas atau train." },
  { title: "Kad Refleksi", text: "Namakan apa yang kamu rasa, sebelum bertindak balas." },
  { title: "7 Hari Reset", text: "Tujuh langkah kecil, satu ayat setiap hari." },
];

/**
 * Daylight Grove hero (Design System 3.2). The page ground is warm ivory, so
 * the extruded emerald lockup (built for the forest stage) gives way to a
 * typeset lockup: gilt small caps over an emerald Fraunces hero word, with the
 * book itself still dark — it is an object, not a background.
 */
export function Hero() {
  return (
    <section id="atas" className="ph-day-stage relative overflow-hidden px-5 pb-16 pt-12 md:pb-24 md:pt-20">
      <HeroGlyphs />
      <ReadingProgress />

      <div className="mx-auto grid max-w-grid items-center gap-10 md:grid-cols-[1.15fr_0.85fr]">
        <div className="flex flex-col items-center gap-6 text-center md:items-start md:text-left">
          <div className="w-full max-w-[560px] animate-fade-up" style={{ animationDelay: "120ms" }}>
            <h1 className="font-display text-green-900">
              <span className="ph-caps block text-[clamp(1.4rem,1rem+1.5vw,2.15rem)] text-gold-ink">Perpustakaan</span>
              <span className="ph-hero mt-1 block text-[clamp(3.9rem,2.4rem+6.6vw,7rem)] leading-[0.94]">HATI</span>
            </h1>
            <SectionOrnament className="mt-5 md:mx-0" />
          </div>
          <p className="ph-kicker w-full max-w-[420px] animate-fade-up" style={{ animationDelay: "240ms" }}>oleh @rahimam</p>
          <p className="ph-script text-2xl text-green-800 md:text-3xl animate-fade-up" style={{ animationDelay: "320ms" }}>
            Karya untuk jiwa yang pernah terluka
          </p>
          <p className="max-w-prose text-base leading-relaxed text-ink-grove md:text-lg animate-fade-up" style={{ animationDelay: "420ms" }}>
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
              <li key={c} className="rounded-pill border border-daylight-edge bg-daylight-raised px-3 py-1 text-xs text-green-800">
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
            <p className="font-display text-lg text-green-900">{l.title}</p>
            <p className="mt-1 text-sm text-ink-grove">{l.text}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
