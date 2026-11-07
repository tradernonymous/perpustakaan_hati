import { getOrders } from "@/src/server/instance";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** The order id is a random UUID, so it works as the capability. Only the status is exposed. */
export async function GET(_req: Request, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  const order = getOrders().get(id);
  if (!order) return Response.json({ error: "not found" }, { status: 404 });
  return Response.json({ status: order.status }, { headers: { "Cache-Control": "no-store" } });
}
