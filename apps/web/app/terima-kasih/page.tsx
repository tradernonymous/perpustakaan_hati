import type { Metadata } from "next";
import { OrderStatus } from "@/components/OrderStatus";
import { PageShell } from "@/components/PageShell";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Terima kasih | Perpustakaan Hati", robots: { index: false } };

export default async function ThankYou({ searchParams }: { searchParams: Promise<{ order?: string }> }) {
  const { order } = await searchParams;
  return (
    <PageShell title="Terima kasih">
      {order && /^[0-9a-f-]{36}$/.test(order) ? <OrderStatus orderId={order} /> : <p className="text-center">Pautan tidak lengkap. Semak e-mel kamu untuk pautan muat turun.</p>}
    </PageShell>
  );
}
