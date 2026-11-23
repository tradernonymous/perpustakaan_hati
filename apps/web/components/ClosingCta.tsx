/** Last band of the home page: one more clear path back to the free opt-in. */
export function ClosingCta() {
  return (
    <section id="penutup" className="ph-dark-section relative overflow-hidden px-5 py-16 text-center md:py-24" aria-labelledby="penutup-h">
      <div className="ph-closing-glow" aria-hidden="true" />
      <div className="relative mx-auto max-w-reading">
        <h2 id="penutup-h" className="ph-title ph-closing-title text-4xl text-fg md:text-6xl">Mulakan dengan satu buku kecil.</h2>
        <p className="mx-auto mt-4 max-w-prose text-fg-muted">
          Edisi Poket percuma. Baca 60 saat sehari, naik ke edisi seterusnya bila kamu bersedia.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <a href="#percuma" className="ph-cta min-h-cta-mobile w-full items-center justify-center sm:w-auto">
            Dapatkan Edisi Poket, percuma
          </a>
          <a href="#edisi" className="btn-ghost min-h-cta-mobile w-full justify-center sm:w-auto">Lihat semua edisi</a>
        </div>
      </div>
    </section>
  );
}
