import { temanHatiEnabled } from "@/src/feature-flags";
import { AuthorByline } from "@/components/AuthorByline";
import { NAV } from "@/src/content";

export function SafetyFooter({ base = "" }: { base?: string }) {
  return (
    <footer id="kaki-laman" className="bg-surface-soft px-4 pb-[calc(2.5rem+env(safe-area-inset-bottom))] pt-10 text-sm text-fg sm:px-5">
      <div className="mx-auto flex max-w-grid flex-col gap-8">
        <div className="grid gap-8 md:grid-cols-[1.2fr_0.8fr]">
          <div className="flex max-w-reading flex-col gap-3">
            <p className="font-display text-lg text-fg">Jika kamu sedang dalam kesusahan</p>
            <p>
              Buku dan bahan di sini ialah pendidikan dan renungan diri, bukan pengganti bantuan
              profesional. Jika kamu perlu bercakap dengan seseorang sekarang, hubungi{" "}
              <a href="tel:15555" className="font-semibold text-fg underline underline-offset-4">
                Talian HEAL 15555
              </a>{" "}
              atau{" "}
              <a href="tel:0376272929" className="font-semibold text-fg underline underline-offset-4">
                Befrienders (03-7627 2929)
              </a>
              .
            </p>
            <p>
              Privasi kamu penting. E-mel dan nombor WhatsApp dilindungi di bawah Akta Perlindungan
              Data Peribadi (PDPA) Malaysia dan tidak dikongsi dengan pihak lain.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6 sm:grid-cols-3">
            <div>
              <p className="text-xs font-semibold text-fg-accent">Edisi buku</p>
              <nav aria-label="Pautan edisi" className="mt-2 flex flex-col">
                {NAV.map((n) => (
                  <a key={n.href} href={`${base}${n.href}`} className="flex min-h-tap items-center text-fg-healing underline-offset-4 hover:underline">
                    {n.label}
                  </a>
                ))}
                <a href="/pustaka" className="flex min-h-tap items-center font-medium text-fg underline-offset-4 hover:underline">
                  Pustaka saya
                </a>
              </nav>
            </div>

            <div>
              <p className="text-xs font-semibold text-fg-accent">Interaktif</p>
              <nav aria-label="Pautan interaktif" className="mt-2 flex flex-col">
                <a href="/kad-jujur-hati" className="flex min-h-tap items-center text-fg-healing underline-offset-4 hover:underline">Kad Jujur Hati</a>
                <a href="/cermin-pasangan" className="flex min-h-tap items-center text-fg-healing underline-offset-4 hover:underline">Cermin Pasangan</a>
                {temanHatiEnabled && (<a href="/teman-hati" className="flex min-h-tap items-center text-fg-healing underline-offset-4 hover:underline">Teman Hati AI</a>)}
                <a href="/cabaran-7-hari" className="flex min-h-tap items-center text-fg-healing underline-offset-4 hover:underline">Cabaran 7 Hari</a>
              </nav>
            </div>

            <div>
              <p className="text-xs font-semibold text-fg-accent">Komuniti &amp; sesi</p>
              <nav aria-label="Pautan perkhidmatan" className="mt-2 flex flex-col">
                <a href="/surat-hati" className="flex min-h-tap items-center text-fg-healing underline-offset-4 hover:underline">Surat Hati</a>
                <a href="/hadiah-hati" className="flex min-h-tap items-center text-fg-healing underline-offset-4 hover:underline">Hadiah Hati</a>
                <a href="/booking" className="flex min-h-tap items-center text-fg-healing underline-offset-4 hover:underline">Booking Kaunseling</a>
                <a href="/kelab" className="flex min-h-tap items-center text-fg-healing underline-offset-4 hover:underline">Kelab Perpustakaan Hati</a>
              </nav>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4 border-t border-line pt-6">
          <div className="flex items-center gap-4">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/brand/emblem-book-heart.svg" alt="" width={72} height={50} loading="eager" fetchPriority="high" className="h-[50px] w-[72px] shrink-0" />
            <div className="text-fg-muted">
              <span className="ph-caps block text-xs text-fg">Perpustakaan Hati</span>
              <AuthorByline className="justify-start px-0 text-xs text-fg" />
            </div>
          </div>
          <p className="text-xs text-fg-muted">Karya pendidikan dan renungan diri untuk komuniti Malaysia.</p>
        </div>
      </div>
    </footer>
  );
}
