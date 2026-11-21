import type { Metadata } from "next";
import type { ReactNode } from "react";
import { HeroAtmosphere } from "@/components/HeroAtmosphere";
import atmosphere from "@/components/HeroAtmosphere.module.css";
import { HeroGlyphs } from "@/components/HeroGlyphs";
import { HeroBook } from "@/components/HeroBook";
import { StatsStrip } from "@/components/StatsStrip";
import { Ticker } from "@/components/Ticker";
import { SectionOrnament } from "@/components/SectionOrnament";
import { TierCompare } from "@/components/TierCompare";
import { ProductCover } from "@/components/ProductCover";
import { TipsFlipbook } from "@/components/TipsFlipbook";
import { TIERS } from "@/src/content";
import { hasTipsArtwork } from "@/src/server/tips-artwork";
import { ShowcaseControls } from "./Controls";

export const metadata: Metadata = {
  title: "Sistem Reka Bentuk 3.9 | Perpustakaan Hati",
  description: "Panduan visual Void Grove: tipografi, warna, identiti, komponen, gerakan dan edisi buku.",
  alternates: { canonical: "/design-system" },
};

const sections = [
  ["warna", "Warna dan bahan"],
  ["tipografi", "Tipografi"],
  ["identiti", "Identiti dan aset"],
  ["kawalan", "Kawalan dan navigasi"],
  ["borang", "Borang dan keadaan"],
  ["kad", "Kad dan susun atur"],
  ["edisi", "Edisi dan kulit 3D"],
  ["gerakan", "Gerakan dan pembaca"],
  ["penerbitan", "Reka letak penerbitan"],
] as const;

const colors = [
  ["ph-void", "#030604"], ["ph-void-raised", "#08120c"], ["ph-void-soft", "#0e1b13"],
  ["green-900", "#123d2a"], ["green-700", "#2d7954"], ["green-500", "#5b9b7d"],
  ["green-300", "#a7d3b6"], ["gold", "#c9a86a"], ["gold-light", "#e9cea2"],
  ["burgundy", "#5c1e17"], ["cream", "#fdfee6"], ["paper", "#f4efe6"],
] as const;

const brandAssets = [
  ["emblem-book-heart.svg", "Lambang buku dan hati"],
  ["lockup-hero.svg", "Logo utama"],
  ["monogram-stamp.svg", "Cop monogram"],
  ["ph-mark-flat.svg", "Tanda rata"],
  ["seal-edisi-poket.svg", "Meterai Edisi Poket"],
  ["seal-edisi-membangun.svg", "Meterai Edisi Membangun"],
  ["seal-teman-hidup.svg", "Meterai Teman Hidup"],
  ["aje/aje-turtle-noir.svg", "Armazas Jaya Enterprise"],
] as const;

function Section({ index, children }: { index: number; children: ReactNode }) {
  const [id, title] = sections[index];
  return (
    <section id={id} aria-labelledby={`heading-${id}`} className="scroll-mt-8 border-t border-line py-9 sm:py-12">
      <h2 id={`heading-${id}`} className="ph-title mb-6 text-4xl sm:text-6xl">{title}</h2>
      {children}
    </section>
  );
}

export default function DesignSystem() {
  return (
    <>
      <a href="#panduan" className="sr-only focus:not-sr-only">Langkau ke panduan</a>
      <header className="border-b border-line">
        <div className="mx-auto flex max-w-grid flex-wrap items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <a href="/" className="inline-flex min-h-tap items-center gap-2 font-display text-xl">
            <img src="/brand/ph-mark-flat.svg" width={30} height={30} alt="" />
            Perpustakaan Hati
          </a>
          <a href="/" className="inline-flex min-h-tap items-center text-sm text-fg-healing underline">Ke laman utama</a>
        </div>
      </header>
      <main id="panduan" className="mx-auto max-w-grid px-4 pb-16 sm:px-6">
        <div className="relative isolate my-6 overflow-hidden rounded-lg border border-line px-6 py-12 sm:my-10 sm:px-12 sm:py-20">
          <HeroAtmosphere />
          <HeroGlyphs />
          <div className={atmosphere.copy}>
            <p className="mb-2 text-sm font-semibold text-fg-accent">Sistem Reka Bentuk 3.9</p>
            <h1 className="ph-display-hero font-display">Void Grove</h1>
            <p className="mt-4 max-w-reading text-fg-muted">Panduan Perpustakaan Hati untuk identiti, tipografi, bahan buku, gerakan dan komponen antara muka.</p>
          </div>
        </div>
        <nav aria-label="Kandungan sistem reka bentuk" className="mb-8 flex flex-wrap gap-2">
          {sections.map(([id, label]) => (
            <a key={id} href={`#${id}`} className="inline-flex min-h-tap items-center rounded-pill border border-line px-3 text-sm text-fg-healing hover:border-gold">{label}</a>
          ))}
        </nav>

        <Section index={0}>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {colors.map(([name, hex]) => (
              <figure key={name} className="ph-card m-0 overflow-hidden">
                <div aria-hidden="true" className="h-14 border-b border-line" style={{ backgroundColor: `var(--${name})` }} />
                <figcaption className="grid gap-1 p-2 text-xs sm:p-3 sm:text-sm"><code>{name}</code><span className="text-fg-muted">{hex}</span></figcaption>
              </figure>
            ))}
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="ph-card ph-elev-1 p-4">Permukaan asas</div>
            <div className="ph-card ph-elev-2 p-4">Permukaan terangkat</div>
            <div className="ph-card ph-elev-4 p-4">Permukaan timbul</div>
          </div>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="ph-card p-5">
              <h3 className="ph-title mb-3 text-2xl">Skala jarak</h3>
              <div className="flex flex-wrap items-end gap-3">
                {[1, 2, 3, 4, 6, 8, 12, 16].map((step) => (
                  <div key={step} className="grid gap-1 text-xs text-fg-muted">
                    <span style={{ width: `var(--space-${step})` }} className="block h-2 rounded bg-green-500" />
                    <code>{step}</code>
                  </div>
                ))}
              </div>
            </div>
            <div className="ph-card p-5">
              <h3 className="ph-title mb-3 text-2xl">Palet carta</h3>
              <div className="flex flex-wrap gap-2">
                {[1, 2, 3, 4, 5].map((step) => (
                  <span key={step} className="rounded border border-line p-2 text-xs">
                    <span aria-hidden="true" className="mb-2 block h-2 rounded" style={{ background: `var(--chart-${step})` }} />
                    <code>chart-{step}</code>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </Section>

        <Section index={1}>
          <div className="grid gap-4 md:grid-cols-2">
            <article className="ph-card p-5">
              <p className="text-sm text-fg-accent">Instrument Serif · paparan</p>
              <p className="ph-title mt-2 text-5xl">Ruang untuk pulih.</p>
              <p className="font-display mt-2 text-3xl italic">Baca mengikut rentakmu.</p>
            </article>
            <article className="ph-card grid gap-4 p-5">
              <p><span className="block text-sm text-fg-accent">Geist Sans · antara muka</span>Bacaan kecil dalam Bahasa Melayu.</p>
              <p><span className="block text-sm text-fg-accent">Source Serif 4 · bacaan</span><span className="font-reading text-lg">Ambil masa untuk membaca sehalaman demi sehalaman.</span></p>
              <p className="ph-nums">RM 29.00 · RM 79.00</p>
            </article>
          </div>
        </Section>

        <Section index={2}>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {brandAssets.map(([file, label]) => (
              <figure key={file} className="ph-card m-0 grid content-start gap-3 p-4">
                <img src={`/brand/${file}`} alt="" width={180} height={110} className="mx-auto h-24 w-full object-contain" loading="lazy" />
                <figcaption><a href={`/brand/${file}`} className="text-sm text-fg-healing underline">{label}</a></figcaption>
              </figure>
            ))}
          </div>
          <SectionOrnament className="mt-6" />
        </Section>

        <Section index={3}>
          <div className="grid gap-5">
            <div className="flex flex-wrap items-center gap-2" aria-label="Variasi butang">
              <a href="#edisi" className="ph-cta min-h-tap">Tindakan utama</a>
              <a href="#tipografi" className="btn-ghost">Tindakan sekunder</a>
              <a href="#warna" className="text-fg-healing underline">Pautan teks</a>
              <button type="button" disabled className="ph-cta min-h-tap cursor-not-allowed opacity-50">Dilumpuhkan</button>
            </div>
            <div className="ph-card flex flex-wrap items-center gap-3 p-4"><span className="text-fg-muted">Lompat ke</span><a href="#edisi" className="text-fg-healing underline">Edisi</a><a href="#gerakan" className="text-fg-healing underline">Pembaca</a><kbd className="ml-auto rounded border border-line px-2 py-1 text-sm">Ctrl K</kbd></div>
            <ShowcaseControls />
          </div>
        </Section>

        <Section index={4}>
          <div className="grid gap-4 md:grid-cols-3">
            <label className="ph-card grid gap-2 p-4">Alamat e-mel<input type="email" placeholder="nama@contoh.my" className="min-h-tap w-full rounded border border-line px-3" /></label>
            <label className="ph-card grid gap-2 p-4">Nombor telefon<input type="tel" defaultValue="012" aria-invalid="true" aria-describedby="contoh-ralat" className="min-h-tap w-full rounded border border-current px-3" /><span id="contoh-ralat" className="text-sm text-fg-muted">Masukkan nombor yang lengkap.</span></label>
            <label className="ph-card grid gap-2 p-4">Pilih edisi<select className="min-h-tap w-full rounded border border-line px-3"><option>Edisi Poket</option><option>Edisi Membangun</option><option>Teman Hidup</option></select></label>
          </div>
          <label className="mt-4 inline-flex min-h-tap items-center gap-2"><input type="checkbox" className="h-5 w-5 accent-green-500" /> Terima kemas kini bacaan</label>
          <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
            <div className="ph-card grid gap-2 p-4" aria-busy="true"><b>Memuatkan</b><span className="block h-2 w-3/4 rounded bg-surface-soft" /></div>
            <div className="ph-card p-4"><b>Tiada hasil</b><p className="mt-1 text-sm text-fg-muted">Cuba kata kunci lain.</p></div>
            <div className="ph-card p-4"><b className="text-fg-healing">Berjaya</b><p className="mt-1 text-sm text-fg-muted">Pilihan disimpan.</p></div>
            <div className="ph-card p-4"><b style={{ color: "var(--text-danger)" }}>Ralat</b><p className="mt-1 text-sm text-fg-muted">Semak medan di atas.</p></div>
          </div>
        </Section>

        <Section index={5}>
          <div className="grid gap-4 md:grid-cols-3">
            <article className="ph-card p-5"><h3 className="ph-title text-2xl">Kad editorial</h3><p className="mt-2 text-fg-muted">Pembuka bab, penerangan koleksi dan nota bacaan.</p></article>
            <article className="ph-glass rounded-lg border border-line p-5"><h3 className="ph-title text-2xl">Kad kaca</h3><p className="mt-2 text-fg-muted">Permukaan untuk panel pendamping.</p></article>
            <article className="ph-card p-5"><h3 className="ph-title text-2xl">Kemajuan</h3><progress className="mt-3 w-full accent-green-500" value={60} max={100} aria-label="Kemajuan bacaan" /><p className="text-fg-muted">60% dibaca</p></article>
          </div>
          <details className="ph-card ph-faq mt-4 p-5">
            <summary className="min-h-tap cursor-pointer font-display text-2xl">Bagaimana kad ini terbuka?</summary>
            <p className="ph-faq-answer text-fg-muted">Soalan lazim menggunakan pendedahan asli yang boleh dibuka dengan papan kekunci.</p>
          </details>
        </Section>

        <Section index={6}>
          <div className="grid gap-4 sm:grid-cols-3">
            {TIERS.map((tier) => (
              <article key={tier.id} data-tier={tier.id} className="ph-tier-card p-4">
                <div className="ph-book-stage mx-auto w-full max-w-[190px]">
                  <div className="ph-book-object">
                    <ProductCover name={tier.name} src={tier.cover} seal={tier.seal} tier={tier.id} />
                  </div>
                </div>
                <h3 className="ph-title mt-3 text-2xl">{tier.name}</h3>
                <p className="text-sm text-fg-muted">{tier.size} · {tier.subcopy}</p>
                <span className="ph-tier-badge mt-3" data-tier={tier.id}>{tier.name}</span>
              </article>
            ))}
          </div>
          <div className="mt-6">
            <h3 className="ph-title mb-4 text-2xl">Jadual perbandingan responsif</h3>
            <TierCompare />
          </div>
        </Section>

        <Section index={7}>
          <div className="mb-6 grid gap-4 lg:grid-cols-2">
            <figure className="ph-card m-0 grid content-start gap-3 p-5">
              <HeroBook
                name="Teman Hidup"
                cover={TIERS[2].cover ?? "/ebooks/cover-teman-hidup.png"}
                seal={TIERS[2].seal.replace("/brand/", "/brand/animated/")}
                pages={[
                  { title: "Bab Pembukaan", text: "Teman Hidup menemani langkah harian dengan kad refleksi dan buku kerja." },
                  { title: "Kad Refleksi", text: "Apa yang berubah dalam dirimu minggu ini?" },
                  { title: "Nota Suara", text: "Rakamkan satu isi hati untuk didengar semula nanti." },
                ]}
              />
              <figcaption className="text-sm text-fg-muted">Buku 3D interaktif — klik kulit untuk membuka, anak panah untuk menukar muka surat.</figcaption>
            </figure>
            <div className="grid content-start gap-4">
              <StatsStrip />
              <Ticker />
            </div>
          </div>
          <div className="mb-4 grid gap-4 md:grid-cols-2">
            <figure className="ph-card m-0 grid justify-items-center gap-2 p-5">
              <img src="/brand/animated/emblem-book-heart.svg" width={110} height={80} alt="" />
              <figcaption className="text-sm text-fg-muted">Animasi lambang</figcaption>
            </figure>
            <div className="ph-card self-stretch p-5">
              <h3 className="ph-title text-2xl">Maklum balas dan peralihan</h3>
              <p className="mt-2 text-fg-muted">Tiga lencana di atas mempamerkan kemasan emas, lambang buku dan hati asal, serta kemasan grid berinspirasikan fintech. Jeda latar untuk menghentikan lencana dan orbit. Halakan penuding pada kulit bab untuk melihat kilauan, atau selak buku di bawah. Lapisan gerakan terkini: medan glif terapung dengan paralaks penuding, gelang putar di belakang medali, kilauan diagonal pada setiap <code>ph-cta</code>, dan kemasukan muka surat 3D secara berperingkat. Semua dilumpuhkan di bawah <code>prefers-reduced-motion</code>.</p>
            </div>
          </div>
          <div id="percuma" className="scroll-mt-8">
            <TipsFlipbook artwork={hasTipsArtwork()} />
          </div>
        </Section>

        <Section index={8}>
          <div className="grid gap-4 md:grid-cols-3">
            {TIERS.map(({ id, name }) => (
              <article key={id} className={`ph-ebook-${id} rounded-lg border p-5`}
                style={{
                  backgroundColor: `var(--ebook-${id}-page)`,
                  color: `var(--ebook-${id}-ink)`,
                  borderColor: `var(--ebook-${id}-rule)`,
                }}>
                <p className="mb-3 text-sm">{name}</p>
                <h3 className="font-display text-3xl" style={{ color: `var(--ebook-${id}-heading)` }}>Sehalaman untuk diri</h3>
                <p className="my-4 font-reading">Ada hari yang meminta kita memperlahankan langkah. Bacalah mengikut rentakmu.</p>
                <p className="rounded p-3 text-sm" style={{ backgroundColor: `var(--ebook-${id}-field)`, color: `var(--ebook-${id}-field-ink)` }}>
                  Refleksi · Apakah satu langkah kecil yang boleh kamu ambil hari ini?
                </p>
              </article>
            ))}
          </div>
        </Section>
      </main>
    </>
  );
}
