import type { Metadata } from "next";
import { CerminPasangan } from "@/components/CerminPasangan";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = { title: "Cermin Pasangan | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title="Cermin Pasangan" intro="5 soalan untuk berdua. Jawab sendiri, hantar pautan rahsia kepada pasangan, dan buka Peta Hubungan bersama.">
      <CerminPasangan />
    </PageShell>
  );
}
