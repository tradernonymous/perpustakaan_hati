import { activeReader } from "@/src/server/reader-session";
import { tipsPage } from "@/src/tips";
import { PageShell } from "@/components/PageShell";
import pages from "@/src/tips-reader.json";

export const metadata = { title: "Tips Psikologi Suami Isteri | Perpustakaan Hati" };

export default async function TipsReader({ searchParams }: { searchParams: Promise<{ halaman?: string; disimpan?: string }> }) {
  const { halaman, disimpan } = await searchParams;
  const page = tipsPage(halaman) ?? 1;
  const signedIn = Boolean(await activeReader());
  const link = (number: number) => `?halaman=${number}`;
  const last = page === pages.length;

  return (
    <PageShell title="Tips Psikologi Suami Isteri" intro="Buku percuma · Baca terus tanpa daftar">
      <div className="mx-auto grid max-w-reading gap-4">
        <nav aria-label="Halaman buku" className="flex flex-wrap items-center justify-between gap-2">
          {page > 1 && <a className="btn-ghost min-h-tap" href={link(page - 1)}>Sebelumnya</a>}
          <span>Halaman {page} daripada {pages.length}</span>
          {!last && <a className="btn-ghost min-h-tap" href={link(page + 1)}>Seterusnya</a>}
        </nav>
        <article className="ph-card grid gap-5 px-6 py-8 sm:px-10" aria-label={`Halaman ${page}`}>
          {page === 1 && <img src="/ebooks/tips-psikologi-suami-isteri-a4.webp" alt="Kulit Tips Psikologi Suami Isteri" width={560} height={792} className="mx-auto w-48 rounded" />}
          <div className="whitespace-pre-line leading-relaxed">{pages[page - 1]}</div>
        </article>
        <nav aria-label="Terus membaca" className="flex flex-wrap items-center justify-end gap-3">
          {page > 1 && <a className="btn-ghost min-h-tap" href={link(page - 1)}>Halaman sebelumnya</a>}
          {!last && <a className="ph-cta min-h-tap" href={link(page + 1)}>Halaman seterusnya</a>}
        </nav>
        {signedIn && <form method="post" action="/api/pustaka/bookmark">
          <input type="hidden" name="halaman" value={page} />
          <button className="btn-ghost min-h-tap">Simpan halaman ini</button>
          {disimpan === "1" && <p role="status">Halaman disimpan dalam Pustaka.</p>}
        </form>}
        {!signedIn && (
          <aside className="ph-card grid gap-3 p-4">
            <p className="text-sm text-fg-muted">Suka bacaan ini? Buka koleksi PDF Edisi Poket percuma di Pustaka Saya.</p>
            <a className="ph-cta min-h-tap" href={`/pustaka?halaman=${page}`}>Daftar & buka Edisi Poket</a>
          </aside>
        )}
      </div>
    </PageShell>
  );
}
