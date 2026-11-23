import { TipsFlipbook } from "./TipsFlipbook";
import { HeroGlyphs } from "./HeroGlyphs";
import { SignupDialog } from "./SignupDialog";
import { hasTipsArtwork } from "@/src/server/tips-artwork";
import { ReaderSignup } from "@/components/ReaderSignup";
import { HeroAtmosphere } from "./HeroAtmosphere";
import styles from "./HeroAtmosphere.module.css";

/** A short introduction, followed by the Edisi Poket signup. */
export function Hero() {
  return (
    <>
      <section id="atas" aria-labelledby="hero-heading" className="ph-day-stage relative overflow-hidden border-b border-line px-4 py-12 sm:px-5 sm:py-24">
        <div className="ph-grid-dots" aria-hidden="true" />
        <HeroAtmosphere />
        <HeroGlyphs />
        <div className={`${styles.copy} mx-auto max-w-3xl text-center`}>
          <p className="mb-5 text-xs font-semibold tracking-wide text-fg-accent">Perpustakaan Hati · Bahasa Melayu</p>
          <h1 id="hero-heading" className="ph-display-hero text-balance font-display text-fg">
            Bacaan kecil.<br /><span className={`text-fg-healing ${styles.accent}`}>Ruang untuk pulih.</span>
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-base leading-relaxed text-fg-muted sm:mt-5 sm:text-lg">
            Tulisan tentang hubungan dan pemulihan diri, dalam Bahasa Melayu yang dekat di hati.
          </p>
          <div className="mx-auto mt-6 flex max-w-xs flex-col items-stretch justify-center gap-2.5 sm:mt-7 sm:max-w-none sm:flex-row sm:items-center">
            <a href="#percuma" className="ph-cta min-h-cta-mobile inline-flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4">Mulakan percuma</a>
            <a href="#edisi" className="btn-ghost min-h-cta-mobile inline-flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4">Lihat koleksi</a>
          </div>
        </div>
      </section>
      <section id="percuma" aria-labelledby="percuma-heading" className="px-4 py-8 sm:px-5 sm:py-14">
        <div className="mx-auto mb-6 max-w-reading text-center">
          <h2 id="percuma-heading" className="ph-title font-display text-4xl">Tips Psikologi Suami Isteri</h2>
          <p className="mt-2 text-fg-muted">Selak buku percuma. Daftar bila kamu mahu membuka koleksi Edisi Poket.</p>
        </div>
        <TipsFlipbook artwork={hasTipsArtwork()} signup={
          <div className="mx-auto grid w-full max-w-md gap-3 text-center">
            <SignupDialog><ReaderSignup /></SignupDialog>
            <a href="/pustaka" className="inline-flex min-h-tap items-center justify-center text-sm text-fg-healing underline">Buka halaman daftar atau log masuk</a>
          </div>
        } />
      </section>
    </>
  );
}
