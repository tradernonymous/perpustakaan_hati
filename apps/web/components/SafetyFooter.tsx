import { NAV } from "@/src/content";

export function SafetyFooter({ base = "" }: { base?: string }) {
  return (
    <footer className="bg-forest-soft px-5 py-10 pb-28 text-sm text-on-dark md:pb-10">
      <div className="mx-auto flex max-w-reading flex-col gap-4">
        <p className="font-display text-lg text-gold-light">Jika kamu sedang dalam kesusahan</p>
        <p>
          Buku dan bahan di sini ialah pendidikan dan renungan diri, bukan pengganti bantuan
          profesional. Jika kamu perlu bercakap dengan seseorang sekarang, hubungi{" "}
          <strong>Talian HEAL 15555</strong> atau <strong>Befrienders</strong>.
        </p>
        <p>
          Privasi kamu penting. E-mel dan nombor WhatsApp dilindungi di bawah Akta Perlindungan
          Data Peribadi (PDPA) Malaysia dan tidak dikongsi dengan pihak lain.
        </p>
        <nav aria-label="Pautan kaki" className="flex flex-wrap gap-x-4">
          {NAV.map((n) => (
            <a key={n.href} href={`${base}${n.href}`} className="flex min-h-tap items-center text-green-300 underline-offset-4 hover:underline">{n.label}</a>
          ))}
          <a href="/pustaka" className="flex min-h-tap items-center text-green-300 underline-offset-4 hover:underline">Pustaka saya</a>
        </nav>
        <div className="mt-2 flex items-center gap-4 border-t border-forest-edge pt-6">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/emblem-book-heart.svg" alt="" width={72} height={50} loading="lazy" className="h-[50px] w-[72px] shrink-0" />
          <p className="text-on-dark-muted">
            <span className="ph-caps block text-xs text-gold-light">Perpustakaan Hati</span>
            oleh @rahimam
          </p>
        </div>
      </div>
    </footer>
  );
}
