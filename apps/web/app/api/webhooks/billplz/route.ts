import { verifyBillplzCallback, billplzConfig } from "@/src/server/billplz";
import { handlePaid } from "@/src/server/checkout";
import { getOrders } from "@/src/server/instance";
import { onPaid } from "@/src/server/paid";

export const runtime = "nodejs";

/** Billplz posts form-encoded bill updates here. Only a correctly signed, paid callback counts. */
export async function POST(req: Request) {
  const cfg = billplzConfig();
  if (!cfg) return new Response("not configured", { status: 503 });

  const params = Object.fromEntries(new URLSearchParams(await req.text()));
  if (!verifyBillplzCallback(params, cfg.xSignatureKey)) return new Response("bad signature", { status: 401 });
  if (params.paid !== "true") return new Response("ok", { status: 200 });

  const orders = getOrders();
  const order = orders.findByProviderRef("billplz", params.id ?? "");
  if (!order) return new Response("unknown bill", { status: 200 });

  const outcome = await handlePaid(orders, order.id, params.id!, Number(params.paid_amount ?? params.amount), onPaid);
  return new Response(outcome, { status: 200 });
}
