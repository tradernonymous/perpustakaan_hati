import { handlePaid } from "@/src/server/checkout";
import { getOrders } from "@/src/server/instance";
import { onPaid } from "@/src/server/paid";
import { verifyStripeSignature } from "@/src/server/stripe";

export const runtime = "nodejs";

type Session = { id: string; client_reference_id?: string; payment_status?: string; amount_total?: number };

export async function POST(req: Request) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secret) return new Response("not configured", { status: 503 });

  const raw = await req.text();
  if (!verifyStripeSignature(raw, req.headers.get("stripe-signature"), secret)) return new Response("bad signature", { status: 401 });

  const event = JSON.parse(raw) as { type: string; data: { object: Session } };
  const s = event.data.object;
  if (event.type !== "checkout.session.completed" || s.payment_status !== "paid" || !s.client_reference_id) {
    return new Response("ignored", { status: 200 });
  }
  const outcome = await handlePaid(getOrders(), s.client_reference_id, s.id, s.amount_total ?? -1, onPaid);
  return new Response(outcome, { status: 200 });
}
