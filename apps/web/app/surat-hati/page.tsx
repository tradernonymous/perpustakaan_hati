import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { SuratHatiForm } from "@/components/SuratHatiForm";

export const metadata: Metadata = { title: "Surat Hati | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title="Surat Hati" intro="Hantar luahan anonim. Surat terpilih akan terima breakdown psikologi daripada Rahimam.">
      <SuratHatiForm />
    </PageShell>
  );
}
