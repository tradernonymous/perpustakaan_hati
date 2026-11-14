import type { Metadata } from "next";
import { CabaranTracker } from "@/components/CabaranTracker";
import { PageShell } from "@/components/PageShell";
import { CABARAN_DAYS, CABARAN_TITLE } from "@/src/games/cabaran";

export const metadata: Metadata = { title: "7 Hari Cabaran Pulih Hati | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title={CABARAN_TITLE} intro="Satu prompt setiap hari selama 7 hari. Sertai ribuan pengikut di Threads dengan #CabaranPulihHati.">
      <CabaranTracker days={CABARAN_DAYS} />
    </PageShell>
  );
}
