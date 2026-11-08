import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = { title: "Surat Hati | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title="Surat Hati" intro="Hantar luahan anonim. Surat terpilih akan terima breakdown psikologi daripada Rahimam.">
      <form className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-5" action="/api/surat" method="post">
        <label className="flex flex-col gap-1 text-sm text-green-900">
          Nama samaran (pilihan)
          <input name="name" className="min-h-tap rounded border border-daylight-edge bg-sage px-3 text-ink-grove" placeholder="cth: Aina" />
        </label>
        <label className="flex flex-col gap-1 text-sm text-green-900">
          Luahan kamu
          <textarea name="dilemma" rows={6} className="rounded border border-daylight-edge bg-sage px-3 py-2 text-ink-grove" placeholder="Tulis di sini, nama kamu akan disembunyikan..." required />
        </label>
        <button type="submit" className="ph-cta min-h-tap">Hantar Surat</button>
        <p className="text-xs text-muted-grove">Surat anonim disimpan untuk terbitan dan siri Threads. Tiada perkongsian dengan pihak ketiga.</p>
      </form>
    </PageShell>
  );
}
