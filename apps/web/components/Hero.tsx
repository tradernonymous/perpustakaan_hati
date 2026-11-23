import { TipsFlipbook } from "./TipsFlipbook";
import { SignupDialog } from "./SignupDialog";
import { hasTipsArtwork } from "@/src/server/tips-artwork";
import { ReaderSignup } from "@/components/ReaderSignup";

/** A short introduction, followed by the Edisi Poket signup. */
export function Hero() {
  return (
    <>
      <section id="atas" aria-labelledby="hero-heading" className="ph-day-stage relative overflow-hidden px-4 py-20 sm:px-5 sm:py-32">
        <div className="ph-grid-dots" aria-hidden="true" />
        <div className="relative z-10 mx-auto max-w-4xl text-center">
          <h1 id="hero-heading" className="ph-display-hero text-balance font-display text-fg">
            Bacaan kecil.<br />Ruang untuk pulih.
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-fg-muted sm:mt-8 sm:text-xl">
            Tulisan tentang hubungan dan pemulihan diri, dalam Bahasa Melayu yang dekat di hati.
          </p>
          <div className="mx-auto mt-10 flex max-w-xs flex-col items-stretch justify-center gap-3 sm:mt-12 sm:max-w-none sm:flex-row sm:items-center">
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
