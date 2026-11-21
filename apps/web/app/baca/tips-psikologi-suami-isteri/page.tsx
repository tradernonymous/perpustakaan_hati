import { activeReader } from "@/src/server/reader-session";
import { hasTipsArtwork } from "@/src/server/tips-artwork";
import { tipsPage } from "@/src/tips";
import { PageShell } from "@/components/PageShell";
import { TipsFlipbook } from "@/components/TipsFlipbook";

export const metadata = { title: "Tips Psikologi Suami Isteri | Perpustakaan Hati" };

export default async function TipsReader({ searchParams }: { searchParams: Promise<{ halaman?: string; disimpan?: string }> }) {
  const { halaman, disimpan } = await searchParams;
  return (
    <PageShell title="Tips Psikologi Suami Isteri" intro="Buku percuma · Baca terus tanpa daftar">
      {disimpan === "1" && <p role="status" className="mb-4 text-center">Halaman disimpan dalam Pustaka.</p>}
      <TipsFlipbook initialPage={tipsPage(halaman) ?? 1} artwork={hasTipsArtwork()} signedIn={Boolean(await activeReader())} />
    </PageShell>
  );
}
