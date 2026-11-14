import Link from "next/link";

type EcosystemItem = {
  href: string;
  tag: string;
  title: string;
  description: string;
  cta: string;
};

const ITEMS: EcosystemItem[] = [
  {
    href: "/kad-jujur-hati",
    tag: "Permainan Threads",
    title: "Kad Jujur Hati",
    description: "Tarik kad Red Flag, Green Flag atau Luka Hati, tanda Bingo kamu, dan kongsi ke Threads.",
    cta: "Tarik kad sekarang",
  },
  {
    href: "/cermin-pasangan",
    tag: "Kuiz 5 Soalan",
    title: "Cermin Pasangan",
    description: "Ukur cara kamu bertindak balas dalam hubungan dan buka kad Peta Hubungan untuk pasangan.",
    cta: "Mula kuiz 2 minit",
  },
  {
    href: "/teman-hati",
    tag: "Sokongan 24/7",
    title: "Teman Hati AI",
    description: "Ruang luahan selamat dalam Bahasa Melayu dan English apabila hati terasa berat tengah malam.",
    cta: "Mula berbual",
  },
  {
    href: "/cabaran-7-hari",
    tag: "Cabaran Harian",
    title: "7 Hari Cabaran Pulih Hati",
    description: "Satu soalan refleksi setiap hari selama seminggu bersama komuniti #CabaranPulihHati.",
    cta: "Lihat jadual 7 hari",
  },
  {
    href: "/hadiah-hati",
    tag: "Ganjaran Komuniti",
    title: "Hadiah Hati",
    description: "Sertai cabutan mingguan Teman Hidup atau sesi 1-on-1 dan tuntut voucher RM15.",
    cta: "Semak ganjaran",
  },
  {
    href: "/surat-hati",
    tag: "Luahan Anonim",
    title: "Surat Hati",
    description: "Hantar cerita hubungan secara rahsia. Surat terpilih menerima ulasan psikologi oleh @rahimam.",
    cta: "Tulis surat anonim",
  },
  {
    href: "/booking",
    tag: "Sesi Manusia",
    title: "Booking Kaunseling",
    description: "Tempah sesi kejelasan emosi 1-on-1 atau pengantaraan pasangan dengan panel berlesen.",
    cta: "Lihat pilihan sesi",
  },
  {
    href: "/kelab",
    tag: "Keahlian Bulanan",
    title: "Kelab Perpustakaan Hati",
    description: "Audio Terapi Hati 5 minit dan Malam Bicara Hati secara langsung setiap minggu.",
    cta: "Teroka kelab",
  },
];

export function EcosystemHub() {
  return (
    <div className="mx-auto grid max-w-grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {ITEMS.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className="ph-lux ph-card flex h-full flex-col justify-between gap-4 p-5 text-left"
        >
          <div className="flex flex-col gap-2">
            <span className="w-fit rounded-pill border border-daylight-edge bg-sage px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-kicker text-green-800">
              {item.tag}
            </span>
            <h3 className="font-display text-xl text-green-900">{item.title}</h3>
            <p className="text-sm leading-relaxed text-ink-grove">{item.description}</p>
          </div>
          <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-green-800">
            <span>{item.cta}</span>
            <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
              <path d="M3 8h10M9 4l4 4-4 4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
        </Link>
      ))}
    </div>
  );
}
