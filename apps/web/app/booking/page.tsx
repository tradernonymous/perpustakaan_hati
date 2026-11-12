import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { quoteForType } from "@/src/games/booking";

export const metadata: Metadata = { title: "Booking Kaunseling | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title="Booking Kaunseling" intro="Sesi 1-on-1 dan pasangan dengan kaunselor berlesen di bawah Perpustakaan Hati. RM150–350+ per sesi.">
      <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-5">
        <p className="text-ink-grove">Jenis sesi:</p>
        <ul className="list-disc pl-5 text-ink-grove">
          <li>Kejelasan emosi 1-on-1, RM{quoteForType("clarity") / 100}</li>
          <li>Pengantaraan pasangan, RM{quoteForType("couples") / 100}</li>
          <li>Panel kaunselor, RM{quoteForType("panel") / 100}</li>
        </ul>
        <p className="text-sm text-muted-grove">Bayaran melalui FPX / DuitNow. Peringatan automatik melalui WhatsApp dan Google Meet.</p>
        <a href="#utama" className="ph-cta min-h-tap">Daftar minat sesi</a>
      </div>
    </PageShell>
  );
}
