import type { Metadata } from "next";
import { LibraryLogin } from "@/components/LibraryLogin";
import { PageShell } from "@/components/PageShell";
import { getOrders } from "@/src/server/instance";
import { libraryFor } from "@/src/server/library";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Pustaka Saya | Perpustakaan Hati", robots: { index: false }, referrer: "no-referrer" };

export default async function Pustaka({ searchParams }: { searchParams: Promise<{ t?: string }> }) {
  const { t } = await searchParams;
  const lib = t ? libraryFor(t, { orders: getOrders(), env: process.env }) : null;

  if (!lib) {
    return (
      <PageShell title="Pustaka Saya" intro="Muat turun semula buku yang sudah kamu beli. Kami hantar pautan selamat ke e-mel kamu.">
        {t && <p className="mb-6 text-center text-burgundy-light">Pautan sudah tamat atau tidak sah. Minta yang baharu di bawah.</p>}
        <LibraryLogin />
      </PageShell>
    );
  }
  return (
    <PageShell title="Pustaka Saya" intro={`Untuk ${lib.email}`}>
      {lib.items.length === 0 ? (
        <p className="text-center">Belum ada buku dalam pustaka kamu.</p>
      ) : (
        <ul className="mx-auto flex max-w-reading flex-col gap-3">
          {lib.items.map((i) => (
            <li key={i.name} className="ph-card flex flex-wrap items-center justify-between gap-3 p-4">
              <span className="font-display text-xl text-gold-light">{i.name}</span>
              <a href={i.url} className="ph-cta min-h-tap">Muat turun PDF</a>
            </li>
          ))}
        </ul>
      )}
      <p className="mx-auto mt-6 max-w-reading text-center text-sm text-on-dark-muted">Setiap salinan ditandakan dengan nama pembeli. Mohon jangan kongsi.</p>
    </PageShell>
  );
}
