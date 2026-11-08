import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { FREE_CARD_UNLOCK, VOUCHER_SEN } from "@/src/games/hadiah";

export const metadata: Metadata = { title: "Hadiah Hati | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title="Hadiah Hati" intro="Menang Teman Hidup atau sesi 1-on-1. Semua peserta dapat kad refleksi bonus dan voucher RM15.">
      <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-5">
        <p className="text-ink-grove">Cara menang:</p>
        <ol className="list-decimal pl-5 text-ink-grove">
          <li>Muat turun Edisi Poket percuma</li>
          <li>Kongsi kad hasil kuiz di Threads tag @rahimam</li>
          <li>Ajak 3 kawan dengan pautan referral kamu</li>
        </ol>
        <p className="text-sm text-muted-grove">Setiap peserta mendapat {FREE_CARD_UNLOCK ? "kad refleksi bonus" : ""} dan voucher RM{VOUCHER_SEN / 100} untuk Standard/Premium.</p>
      </div>
    </PageShell>
  );
}
