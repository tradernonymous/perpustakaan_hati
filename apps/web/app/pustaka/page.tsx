import { getTipsBookmark } from "@/src/server/reader-bookmark";
import { TIPS_PATH, tipsPage } from "@/src/tips";

import type { Metadata } from "next";
import { ReaderSignup } from "@/components/ReaderSignup";
import { PageShell } from "@/components/PageShell";
import { getOrders } from "@/src/server/instance";
import { redirect } from "next/navigation";
import { activeReader } from "@/src/server/reader-session";
import { listPocketBooks } from "@/src/server/poket-books";
import { libraryForEmail } from "@/src/server/library";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Pustaka Saya | Perpustakaan Hati", robots: { index: false }, referrer: "no-referrer" };

export default async function Pustaka({ searchParams }: { searchParams: Promise<{ t?: string; expired?: string; google?: string; halaman?: string }> }) {
  const { t, expired, google, halaman } = await searchParams;
  if (t) redirect(`/api/pustaka/session?t=${encodeURIComponent(t)}`);
  const returnPage = tipsPage(halaman);
  const email = await activeReader();
  const lib = email ? libraryForEmail(email, { orders: getOrders(), env: process.env }) : null;

  if (!lib) {
    return (
      <PageShell title="Pustaka Saya" intro="Daftar dengan e-mel untuk membuka koleksi Poket percuma dan buku yang kamu beli.">
        {expired && <p className="mb-6 text-center text-danger">Pautan sudah tamat atau tidak sah. Minta yang baharu di bawah.</p>}
        {google && <p className="mx-auto mb-4 max-w-reading text-sm">Untuk masuk, buka laman ini dalam pelayar telefon kamu atau minta pautan melalui e-mel.</p>}
        <ReaderSignup returnPage={returnPage} />
      </PageShell>
    );
  }
  const bookmark = getTipsBookmark(lib.email);
  const poketBooks = await listPocketBooks();
  return (
    <PageShell title="Pustaka Saya" intro={`Untuk ${lib.email}`}>
      <section className="ph-card mx-auto mb-8 grid max-w-reading gap-3 p-4" aria-labelledby="pustaka-bacaan">
        <h2 id="pustaka-bacaan" className="font-display text-2xl">Bacaan saya</h2>
        <p>Tips Psikologi Suami Isteri{bookmark ? ` · Halaman ${bookmark}` : ""}</p>
        <div className="flex flex-wrap gap-3">
          <a className="ph-cta min-h-tap" href={bookmark ? `${TIPS_PATH}?halaman=${bookmark}` : TIPS_PATH}>{bookmark ? "Sambung membaca" : "Mula membaca"}</a>
          {bookmark && <form method="post" action="/api/pustaka/bookmark">
            <input type="hidden" name="action" value="reset" />
            <button className="btn-ghost min-h-tap">Buang penanda buku</button>
          </form>}
        </div>
      </section>
      <section className="mx-auto mb-8 max-w-reading" aria-labelledby="pustaka-poket">
        <h2 id="pustaka-poket" className="mb-3 font-display text-2xl">Koleksi Poket percuma</h2>
        <ul className="grid gap-2">
          {poketBooks.map((book) => (
            <li key={book.slug} className="ph-card flex flex-wrap items-center justify-between gap-2 p-3">
              <span>{book.title}</span>
              {book.available ? (
                <a href={`/api/pustaka/poket/${book.slug}`} className="btn-ghost min-h-tap">Muat turun PDF</a>
              ) : (
                <span className="text-sm text-fg-muted">Segera hadir</span>
              )}
            </li>
          ))}
        </ul>
      </section>
      <h2 className="mx-auto mb-3 max-w-reading font-display text-2xl">Pembelian</h2>
      {lib.items.length === 0 ? (
        <p className="text-center">Belum ada pembelian.</p>
      ) : (
        <ul className="mx-auto flex max-w-reading flex-col gap-3">
          {lib.items.map((i) => (
            <li key={i.name} className="ph-card flex flex-wrap items-center justify-between gap-3 p-4">
              <span className="font-display text-xl text-fg">{i.name}</span>
              <a href={i.url} className="ph-cta min-h-tap">Muat turun PDF</a>
            </li>
          ))}
        </ul>
      )}
      <p className="mx-auto mt-6 max-w-reading text-center text-sm text-fg-muted">Setiap salinan yang dibeli ditandakan dengan nama pembeli. Mohon jangan kongsi.</p>
      <form action="/api/pustaka/session" method="post" className="mx-auto mt-5 max-w-reading"><button className="btn-ghost min-h-tap">Log keluar</button></form>
    </PageShell>
  );
}
