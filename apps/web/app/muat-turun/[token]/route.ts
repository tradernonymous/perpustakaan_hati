import { readFile } from "node:fs/promises";
import path from "node:path";
import { isProductId, PRODUCTS } from "@/src/catalog";
import { demoMode } from "@/src/server/demo";
import { getOrders } from "@/src/server/instance";
import { verifyToken } from "@/src/server/tokens";
import { placeholderPdf, watermarkPdf } from "@/src/server/watermark";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const text = (body: string, status: number) => new Response(body, { status, headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store" } });

/** Signed link -> PDF stamped with the buyer's name. Product PDFs live in ASSETS_DIR, outside the public folder. */
export async function GET(_req: Request, ctx: { params: Promise<{ token: string }> }) {
  const { token } = await ctx.params;
  const t = verifyToken(token, process.env.DOWNLOAD_SECRET ?? "");
  if (!t || t.k !== "dl" || typeof t.o !== "string" || !isProductId(t.p)) return text("Pautan tidak sah atau sudah tamat. Buka Pustaka Saya untuk pautan baharu.", 410);

  const order = getOrders().get(t.o);
  if (!order || order.status !== "paid" || !order.items.includes(t.p)) return text("Pesanan tidak dijumpai.", 404);

  const assets = process.env.ASSETS_DIR ?? path.join(process.env.DATA_DIR ?? "./data", "assets");
  let source: Buffer;
  try {
    source = await readFile(path.join(assets, PRODUCTS[t.p].file));
  } catch {
    // No real file yet. In demo mode we serve a marked placeholder so the
    // whole flow can be tested; in production the buyer is told to wait.
    if (!demoMode()) return text("Fail ini belum sedia. Kami akan hubungi kamu.", 503);
    const ph = await placeholderPdf(PRODUCTS[t.p].name);
    const stampedPh = await watermarkPdf(ph, `Dilesenkan kepada ${order.email} | Pesanan ${order.id.slice(0, 8)}`);
    return new Response(Buffer.from(stampedPh), {
      headers: {
        "content-type": "application/pdf",
        "content-disposition": `attachment; filename="placeholder-${PRODUCTS[t.p].file}"`,
        "cache-control": "no-store",
      },
    });
  }

  const stamped = await watermarkPdf(source, `Dilesenkan kepada ${order.email} | Pesanan ${order.id.slice(0, 8)}`);
  return new Response(Buffer.from(stamped), {
    headers: {
      "content-type": "application/pdf",
      "content-disposition": `attachment; filename="${PRODUCTS[t.p].file}"`,
      "cache-control": "no-store",
    },
  });
}
