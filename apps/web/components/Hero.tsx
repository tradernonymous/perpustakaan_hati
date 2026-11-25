import { TipsFlipbook } from "./TipsFlipbook";
import { SignupDialog } from "./SignupDialog";
import { hasTipsArtwork } from "@/src/server/tips-artwork";
import { ReaderSignup } from "@/components/ReaderSignup";
import { HeroOrbitClient } from "./HeroOrbitClient";
import styles from "./HeroVoid.module.css";

export function Hero() {
  return (
    <>
      <section id="atas" aria-labelledby="hero-heading" className={styles.stage}>
        <div className={styles.content}>
          <p className={styles.kicker}>Perpustakaan Hati <span>/</span> Edisi Poket</p>
          <h1 id="hero-heading" className={styles.headline}>
            Bacaan kecil.<br /><em>Ruang untuk pulih.</em>
          </h1>
          <p className={styles.subline}>
            Tulisan tentang hubungan dan pemulihan diri, dalam Bahasa Melayu yang dekat di hati.
          </p>
          <div className={styles.actions}>
            <a href="#percuma" className="ph-cta inline-flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4">
              Mulakan percuma
            </a>
            <a href="#edisi" className="btn-ghost inline-flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4">
              Lihat koleksi
            </a>
          </div>
        </div>
        <figure className={styles.exhibit}>
          <div className={styles.canvasLayer}><HeroOrbitClient /></div>
          <figcaption className={styles.caption}><span>Rajah 01</span>Orbit koleksi</figcaption>
        </figure>
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
