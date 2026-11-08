import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = { title: "Kelab Perpustakaan Hati | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title="Kelab Perpustakaan Hati" intro="Keahlian bulanan: Audio Terapi Hati 5 minit dan Malam Bicara Hati secara langsung.">
      <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-5">
        <p className="text-ink-grove">Kelab ialah untuk kamu yang mahu continuity selepas Teman Hidup.</p>
        <ul className="list-disc pl-5 text-ink-grove">
          <li>Audio Terapi Hati — nota suara 5 minit untuk perjalanan atau sebelum tidur</li>
          <li>Malam Bicara Hati — sesi Q&A anonim secara langsung setiap minggu</li>
          <li>Surat Hati terpilih dengan breakdown psikologi daripada Rahimam</li>
        </ul>
        <p className="text-sm text-muted-grove">Harga keahlian akan diumumkan tidak lama lagi. Sertai senarai menunggu di halaman utama.</p>
      </div>
    </PageShell>
  );
}
