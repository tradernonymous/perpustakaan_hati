import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { DemoPayButton } from "@/components/DemoPayButton";
import { PageShell } from "@/components/PageShell";
import { demoMode } from "@/src/server/demo";
import { getOrders } from "@/src/server/instance";
import { formatRM, PRODUCTS } from "@/src/catalog";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Mod demo | Perpustakaan Hati", robots: { index: false } };

export default async function DemoBayar({ searchParams }: { searchParams: Promise<{ order?: string }> }) {
  if (!demoMode()) notFound();
  const { order: orderId } = await searchParams;
  const order = orderId && /^[0-9a-f-]{36}$/.test(orderId) ? getOrders().get(orderId) : null;
  if (!order || order.provider !== "demo") notFound();

  return (
    <PageShell title="Mod demo" intro="Tiada wang sebenar akan diambil.">
      <div className="mx-auto flex max-w-reading flex-col gap-5">
        <div className="rounded border border-gold-deep bg-forest-raised p-4 text-center" role="status">
          <p className="font-display text-xl text-gold-light">Mod demo, tiada wang sebenar</p>
          <p className="mt-1 text-sm text-on-dark-muted">
            Halaman ini hanya untuk menguji aliran beli, hantar dan muat turun. Tiada kad, FPX atau DuitNow akan digunakan.
          </p>
        </div>

        <div className="ph-card flex flex-col gap-3 p-6">
          <h2 className="font-display text-2xl text-gold-light">Pesanan {order.id.slice(0, 8)}</h2>
          <ul className="flex flex-col gap-1 text-sm text-on-dark">
            {order.items.map((p) => (
              <li key={p}>{PRODUCTS[p].name}</li>
            ))}
          </ul>
          <p className="font-display text-3xl text-cream">{formatRM(order.amountSen)}</p>
          <DemoPayButton orderId={order.id} />
          <p className="text-xs text-on-dark-muted">Pautan muat turun akan dihantar ke e-mel {order.email} (dan WhatsApp jika diisi), seperti dalam aliran sebenar.</p>
        </div>
      </div>
    </PageShell>
  );
}
