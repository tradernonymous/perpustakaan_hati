import type { Metadata } from "next";
import { KadJujurHati } from "@/components/KadJujurHati";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = { title: "Kad Jujur Hati | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title="Kad Jujur Hati" intro="Tarik kad, baca prompt, dan kongsi di Threads. Red Flag, Green Flag, Luka Hati: tiga kategori, satu perbualan jujur.">
      <KadJujurHati />
    </PageShell>
  );
}
