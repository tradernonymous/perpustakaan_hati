export function Hero() {
  return (
    <section className="ph-stage relative overflow-hidden px-5 pb-16 pt-14 text-center md:pb-24 md:pt-24">
      <div className="mx-auto flex max-w-reading flex-col items-center gap-6">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/brand/emblem-book-heart.svg" alt="" width={96} height={96} className="h-24 w-24" />
        <p className="ph-kicker w-full">oleh @rahimam</p>
        <h1 className="ph-hero ph-foil-emerald text-5xl md:text-7xl">Perpustakaan Hati</h1>
        <p className="font-display text-2xl italic text-gold-light md:text-3xl">
          Karya untuk jiwa yang pernah terluka
        </p>
        <p className="max-w-prose text-base leading-relaxed text-on-dark md:text-lg">
          Tulisan yang memulihkan, dalam Bahasa Melayu yang dekat di hati. Mulakan dengan satu buku
          kecil yang boleh dibaca sementara menunggu bas atau train.
        </p>
        <a href="#percuma" className="ph-cta min-h-cta-mobile items-center justify-center">
          Mula dengan Edisi Poket, percuma
        </a>
      </div>
    </section>
  );
}
