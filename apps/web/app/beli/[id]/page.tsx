import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { CheckoutForm } from "@/components/CheckoutForm";
import { PageShell } from "@/components/PageShell";
import { ProductCover } from "@/components/ProductCover";
import { bumpPriceSen, isProductId, PRODUCTS, priceSen } from "@/src/catalog";
import { TIERS } from "@/src/content";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Beli | Perpustakaan Hati", robots: { index: false } };

export default async function Beli({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!isProductId(id)) notFound();
  const p = PRODUCTS[id];
  const tier = TIERS.find((t) => t.id === id)!;
  const teman = TIERS.find((t) => t.id === "teman-hidup")!;
  return (
    <PageShell title={`Beli ${p.name}`} intro={tier.subcopy}>
      <div className="mx-auto mb-8 max-w-reading">
        <ProductCover name={tier.name} src={tier.cover} className="mx-auto max-w-[220px]" />
      </div>
      <CheckoutForm
        product={id}
        name={p.name}
        priceLabel={tier.price}
        priceSen={priceSen(id)}
        bump={id === "membangun" ? { priceSen: bumpPriceSen(), label: teman.includes.slice(1).join(", ") } : null}
      />
    </PageShell>
  );
}
