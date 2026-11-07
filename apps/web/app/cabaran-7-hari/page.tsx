import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { CABARAN_DAYS, CABARAN_TITLE } from "@/src/games/cabaran";

export const metadata: Metadata = { title: "7 Hari Cabaran Pulih Hati | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title={CABARAN_TITLE} intro="Satu prompt setiap hari selama 7 hari. Sertai ribuan pengikut di Threads dengan #CabaranPulihHati.">
      <ol className="mx-auto flex max-w-reading flex-col gap-3">
        {CABARAN_DAYS.map((d) => (
          <li key={d.day} className="ph-card p-4">
            <p className="font-display text-gold-light">Hari {d.day}</p>
            <p className="text-on-dark">{d.prompt}</p>
            <p className="mt-1 text-sm text-on-dark-muted">{d.action}</p>
          </li>
        ))}
      </ol>
    </PageShell>
  );
}
