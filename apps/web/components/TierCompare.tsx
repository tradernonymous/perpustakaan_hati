import { TIERS, type Tier } from "@/src/content";
import { ProductCover } from "./ProductCover";

type MatrixCell = boolean | string;

type CompareRow = {
  feature: string;
  poket: MatrixCell;
  membangun: MatrixCell;
  "teman-hidup": MatrixCell;
};

const COMPARE_ROWS: CompareRow[] = [
  {
    feature: "Kad Refleksi: Red Flag, Green Flag, Luka Hati & Corak Attach",
    poket: true,
    membangun: true,
    "teman-hidup": true,
  },
  {
    feature: "Ceklis Pencetus Attach (10 soalan)",
    poket: true,
    membangun: true,
    "teman-hidup": true,
  },
  {
    feature: "7 Hari Reset (60 saat sehari)",
    poket: true,
    membangun: true,
    "teman-hidup": true,
  },
  {
    feature: "3 skrip untuk perbualan paling sukar minggu ini",
    poket: true,
    membangun: true,
    "teman-hidup": true,
  },
  {
    feature: "7 bab panduan dengan situasi sebenar rumah tangga Malaysia",
    poket: false,
    membangun: true,
    "teman-hidup": true,
  },
  {
    feature: "Kit Refleksi: 30 soalan mendalam (satu soalan setiap halaman)",
    poket: false,
    membangun: true,
    "teman-hidup": true,
  },
  {
    feature: "5 contoh skrip untuk bercakap dengan jujur",
    poket: false,
    membangun: true,
    "teman-hidup": true,
  },
  {
    feature: "Buku Kerja 30 Hari",
    poket: false,
    membangun: false,
    "teman-hidup": true,
  },
  {
    feature: "Skrip Bincang Hati ke Hati (pasangan)",
    poket: false,
    membangun: false,
    "teman-hidup": true,
  },
  {
    feature: "Nota Suara Rahimam: Audio Terapi Hati",
    poket: false,
    membangun: false,
    "teman-hidup": true,
  },
  {
    feature: "12 Kad Refleksi siap cetak (format A4)",
    poket: false,
    membangun: false,
    "teman-hidup": true,
  },
  {
    feature: "Anggaran saiz & format",
    poket: "15–25 ms",
    membangun: "60–90 ms",
    "teman-hidup": "Buku, kerja, skrip & audio",
  },
];

const EXACT_LAUNCH_PRICE: Record<string, string | null> = {
  poket: "Percuma sepenuhnya",
  membangun: "Pelancaran: RM 29.00",
  "teman-hidup": "Pelancaran: RM 79.00",
};

function CellMark({
  value,
  tierName,
  tier,
}: {
  value: MatrixCell;
  tierName: string;
  tier: Tier["id"];
}) {
  if (value === true) {
    return (
      <span className="ph-tick" role="img" aria-label={`Termasuk dalam ${tierName}`} data-tier={tier}>
        ✓
      </span>
    );
  }
  if (value === false) {
    return (
      <span className="inline-block h-0.5 w-4 rounded-full bg-line" aria-label={`Tidak termasuk dalam ${tierName}`} />
    );
  }
  return (
    <span className="text-xs font-medium ph-tier-ink" data-tier={tier}>
      {value}
    </span>
  );
}

export function TierCompare() {
  return (
    <div className="ph-compare-wrap mx-auto max-w-grid">
      <table className="ph-compare-table">
        <caption className="sr-only">Perbandingan kandungan antara tiga edisi Perpustakaan Hati</caption>
        <thead>
          <tr>
            <th scope="col" className="w-[40%] align-bottom text-left">
              <span className="ph-caps block text-[0.65rem] text-fg-accent">Matriks Kandungan</span>
              <span className="mt-1 block font-display text-lg text-fg">Apa yang kamu terima</span>
            </th>
            {TIERS.map((t) => {
              const featured = t.id === "membangun";
              const launch = EXACT_LAUNCH_PRICE[t.id];
              return (
                <th
                  key={t.id}
                  scope="col"
                  data-tier={t.id}
                  className={`w-[20%] ${featured ? "ph-compare-featured" : ""}`}
                >
                  <div className="flex flex-col items-center gap-2">
                    {featured ? (
                      <span className="rounded-pill bg-green-700 px-2.5 py-0.5 text-[11px] font-semibold text-cream">
                        Langkah seterusnya
                      </span>
                    ) : (
                      <span className="text-[11px] uppercase tracking-caps text-fg-muted">
                        {t.id === "poket" ? "Permulaan" : "Lengkap"}
                      </span>
                    )}
                    <div className="mx-auto w-[52px]">
                      <ProductCover name={t.name} src={t.cover} seal={t.seal} tier={t.id} className="rounded-sm" />
                    </div>
                    <span className="ph-tier-badge" data-tier={t.id}>{t.name}</span>
                    <span className="font-display text-lg font-semibold ph-tier-ink">{t.price}</span>
                    {launch && <span className="text-[11px] font-medium ph-tier-ink">{launch}</span>}
                  </div>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {COMPARE_ROWS.map((row) => (
            <tr key={row.feature}>
              <th scope="row" className="text-sm font-normal leading-snug text-fg">
                {row.feature}
              </th>
              <td className="align-middle" data-tier="poket">
                <CellMark value={row.poket} tierName="Edisi Poket" tier="poket" />
              </td>
              <td className="ph-compare-featured align-middle" data-tier="membangun">
                <CellMark value={row.membangun} tierName="Edisi Membangun" tier="membangun" />
              </td>
              <td className="align-middle" data-tier="teman-hidup">
                <CellMark value={row["teman-hidup"]} tierName="Teman Hidup" tier="teman-hidup" />
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th scope="row" className="text-left text-xs text-fg-muted">
              Pilih edisi yang sesuai dengan fasa kamu sekarang.
            </th>
            {TIERS.map((t) => {
              const free = t.id === "poket";
              const featured = t.id === "membangun";
              return (
                <td key={t.id} data-tier={t.id} className={featured ? "ph-compare-featured" : ""}>
                  <a
                    href={free ? "#percuma" : `/beli/${t.id}`}
                    className={`${free || featured ? "ph-cta" : "btn-ghost"} min-h-tap w-full justify-center px-3 py-2 text-xs`}
                  >
                    {free ? "Dapatkan percuma" : `Beli ${t.name}`}
                  </a>
                </td>
              );
            })}
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
