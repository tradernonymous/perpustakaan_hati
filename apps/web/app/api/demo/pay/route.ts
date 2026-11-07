import { demoMode } from "@/src/server/demo";
import { handlePaid } from "@/src/server/checkout";
import { getOrders } from "@/src/server/instance";
import { onPaid } from "@/src/server/paid";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Fake pay button for demo orders. It 404s unless demo mode is on and the
 * order was created as a demo order, so it can never touch a real payment.
 * It reuses the same handlePaid and onPaid path as the real webhooks, so the
 * delivery and library behaviour is the real one.
 */
export async function POST(req: Request) {
  if (!demoMode()) return new Response("not found", { status: 404 });

  let orderId = "";
  try {
    const body = (await req.json()) as { order?: unknown };
    if (typeof body.order === "string") orderId = body.order;
  } catch {
    return new Response("not found", { status: 404 });
  }
  if (!/^[0-9a-f-]{36}$/.test(orderId)) return new Response("not found", { status: 404 });

  const orders = getOrders();
  const order = orders.get(orderId);
  if (!order || order.provider !== "demo") return new Response("not found", { status: 404 });

  const outcome = await handlePaid(orders, order.id, `demo-${order.id.slice(0, 8)}`, order.amountSen, onPaid);
  return Response.json({ outcome });
}
