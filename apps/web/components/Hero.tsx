import { AuthorByline } from "@/components/AuthorByline";
import { HeroBook } from "@/components/HeroBook";
import { HeroExcerptPreview } from "@/components/HeroExcerptPreview";
import { HeroGlyphs } from "@/components/HeroGlyphs";
import { Illustration } from "@/components/Illustration";
import { ReadingProgress } from "@/components/ReadingProgress";
import { SectionOrnament } from "@/components/SectionOrnament";
import { ILLUSTRATIONS } from "@/src/illustrations";

const CHIPS = ["Percuma untuk bermula", "Bahasa Melayu", "Format A4 & telefon"];

const LESSONS = [
  { title: "Baca 60 saat sehari", text: "Satu kad pendek untuk masa menunggu bas atau train." },
  { title: "Kad Refleksi", text: "Namakan apa yang kamu rasa, sebelum bertindak balas." },
  { title: "7 Hari Reset", text: "Tujuh langkah kecil, satu ayat setiap hari." },
];

/**
 * Editorial Sanctuary Hero (Daylight Grove 3.4+).
 *
 * Designed as an asymmetric gallery + dark-forest collector plinth:
 * - Left column anchors the live Fraunces wordmark, author byline, promise,
 *   whispered pull-quote, and dual-path CTAs.
 * - Right column frames the uncluttered painting plate above an emerald
 *   collector plinth that stages both the 3D Edisi Poket book and an instant
 *   60-second interactive excerpt reader ("Intai 60 saat") with zero collision.
 */
export function Hero() {
  const plate = ILLUSTRATIONS[0];

  return (
    <section id="atas" className="ph-day-stage relative overflow-hidden px-5 pb-14 pt-8 md:pb-20 md:pt-12">
      <HeroGlyphs />

      <div className="ph-hero-grid mx-auto max-w-grid">
        <div className="flex flex-col items-center gap-5 text-center lg:items-start lg:text-left">
          <div className="animate-fade-up" style={{ animationDelay: "60ms" }}>
            <span className="ph-hero-eyebrow">
              <span className="ph-pulse-dot" aria-hidden="true" />
              <span>Koleksi Edisi 01 · Psikologi Hubungan</span>
            </span>
          </div>

          <div className="w-full max-w-[560px] animate-fade-up" style={{ animationDelay: "120ms" }}>
            <h1 className="font-display text-green-900">
              <span className="ph-caps block text-[clamp(1.35rem,1rem+1.4vw,2rem)] text-gold-ink">Perpustakaan</span>
              <span className="ph-hero mt-1 block text-[clamp(3.75rem,2.3rem+6.2vw,6.75rem)] leading-[0.94]">HATI</span>
            </h1>
            <SectionOrnament className="mt-4 lg:mx-0" />
          </div>

          <p className="ph-kicker w-full max-w-[420px] animate-fade-up" style={{ animationDelay: "220ms" }}>
            <AuthorByline />
          </p>

          <p className="ph-script text-2xl text-green-800 md:text-3xl animate-fade-up" style={{ animationDelay: "300ms" }}>
            Karya untuk jiwa yang pernah terluka
          </p>

          <p className="max-w-prose text-base leading-relaxed text-ink-grove md:text-lg animate-fade-up" style={{ animationDelay: "380ms" }}>
            Tulisan yang memulihkan, dalam Bahasa Melayu yang dekat di hati. Mulakan dengan satu buku
            kecil yang boleh dibaca sementara menunggu bas atau train.
          </p>

          <div className="flex w-full flex-col items-center gap-3 sm:w-auto sm:flex-row animate-fade-up" style={{ animationDelay: "480ms" }}>
            <a href="#percuma" className="ph-cta min-h-cta-mobile w-full items-center justify-center sm:w-auto">
              Mula dengan Edisi Poket, percuma
            </a>
            <a href="#edisi" className="btn-ghost min-h-cta-mobile w-full justify-center sm:w-auto">
              Lihat semua edisi
            </a>
          </div>

          <ul className="flex flex-wrap justify-center gap-2 lg:justify-start animate-fade-up" style={{ animationDelay: "560ms" }} aria-label="Kelebihan">
            {CHIPS.map((c) => (
              <li key={c} className="rounded-pill border border-daylight-edge bg-daylight-raised px-3 py-1 text-xs text-green-800">
                {c}
              </li>
            ))}
          </ul>

          <p className="max-w-md border-l-2 border-gold/60 pl-3.5 text-left font-reading text-sm italic text-muted-grove animate-fade-up" style={{ animationDelay: "620ms" }}>
            “Sekali baca, lama terasa. Ruang kecil untuk hati bertenang sebelum berbicara.”
          </p>
        </div>

        <div className="animate-fade-up" style={{ animationDelay: "200ms" }}>
          <figure className="m-0">
            <div className="ph-art">
              <Illustration illustration={plate} sizes="(min-width: 1024px) 38rem, 100vw" priority />
              <span className="ph-art-veil" aria-hidden="true" />
            </div>
            <figcaption className="ph-art-cap">{plate.caption}</figcaption>
          </figure>

          <div className="ph-hero-plinth">
            <div className="py-1">
              <HeroBook name="Edisi Poket" />
            </div>
            <HeroExcerptPreview />
          </div>
        </div>
      </div>

      <ul className="mx-auto mt-10 grid max-w-grid gap-4 sm:grid-cols-3 animate-fade-up" style={{ animationDelay: "680ms" }} aria-label="Cara belajar">
        {LESSONS.map((l) => (
          <li key={l.title} className="ph-glass border-t-2 border-t-gold/50 p-4">
            <p className="font-display text-lg text-green-900">{l.title}</p>
            <p className="mt-1 text-sm text-ink-grove">{l.text}</p>
          </li>
        ))}
      </ul>

      <div className="mx-auto mt-6 max-w-grid">
        <ReadingProgress />
      </div>
    </section>
  );
}
