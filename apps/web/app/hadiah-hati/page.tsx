import type { Metadata } from "next";
import { HadiahHatiPanel } from "@/components/HadiahHatiPanel";
import { PageShell } from "@/components/PageShell";
import { FREE_CARD_UNLOCK, VOUCHER_SEN } from "@/src/games/hadiah";

export const metadata: Metadata = { title: "Hadiah Hati | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title="Hadiah Hati" intro="Menang Teman Hidup atau sesi 1-on-1. Semua peserta dapat kad refleksi bonus dan voucher RM15.">
      <HadiahHatiPanel voucherRm={VOUCHER_SEN / 100} freeCardUnlock={FREE_CARD_UNLOCK} />
    </PageShell>
  );
}
