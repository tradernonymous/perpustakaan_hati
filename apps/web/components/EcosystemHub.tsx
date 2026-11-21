import { temanHatiEnabled } from "@/src/feature-flags";
import Link from "next/link";

type EcosystemItem = {
  href: string;
  tag: string;
  title: string;
  description: string;
  cta: string;
  /** Bento size on wide screens. */
  size?: "half" | "wide" | "tablet-wide";
  /** The dark feature card, so the grid has one anchor. */
  feature?: boolean;
};

const ITEMS: EcosystemItem[] = [
  {
    href: "/cermin-pasangan",
    tag: "Kuiz 5 Soalan",
    title: "Cermin Pasangan",
    description: "Ukur cara kamu bertindak balas dalam hubungan dan buka kad Peta Hubungan untuk pasangan.",
    cta: "Mula kuiz 2 minit",
    size: "wide",
    feature: true,
  },
  {
    href: "/kad-jujur-hati",
    tag: "Permainan Threads",
    title: "Kad Jujur Hati",
    description: "Tarik kad Red Flag, Green Flag atau Luka Hati, tanda Bingo kamu, dan kongsi ke Threads.",
    cta: "Tarik kad sekarang",
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
    description: "Sertai cabutan mingguan Teman Hidup atau sesi 1-on-1 dan menuntut voucher RM15.",
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
    size: "tablet-wide",
  },
];

/**
 * The interactive space, as a bento grid (Design System 3.4).
 *
 * An asymmetric grid gives the eight routes a shape instead of a uniform
 * four-by-two block: one dark feature card anchors the grid, and the
 * rest vary in width. Every route stays reachable and the DOM order
 * still matches the reading order, because the grid only changes size.
 */
export function EcosystemHub() {
  return (
    <div className="ph-bento mx-auto max-w-grid">
      {ITEMS.filter((item) => temanHatiEnabled || item.href !== "/teman-hati").map((item) => {
        const size =
          item.size === "wide"
            ? "ph-bento-wide"
            : item.size === "half"
              ? "ph-bento-half"
              : item.size === "tablet-wide"
                ? "ph-bento-tablet-wide"
                : "";
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`ph-lux ph-card flex h-full flex-col justify-between gap-4 p-5 text-left ${size} ${
              item.feature ? "ph-bento-feature" : ""
            }`}
          >
            <div className="flex flex-col gap-2">
              <span className="ph-bento-tag">{item.tag}</span>
              <h3 className="font-display text-xl">{item.title}</h3>
              <p className="text-sm leading-relaxed text-fg">{item.description}</p>
            </div>
            <span
              className={`inline-flex items-center gap-1.5 text-sm font-semibold ${
                item.feature ? "text-gold-light" : "text-fg-healing"
              }`}
            >
              <span>{item.cta}</span>
              <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                <path d="M3 8h10M9 4l4 4-4 4" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
          </Link>
        );
      })}
    </div>
  );
}
