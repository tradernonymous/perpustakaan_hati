import type { Env } from "../env";
import { createHmac, timingSafeEqual } from "node:crypto";

export type StripeConfig = { secretKey: string };

export function stripeConfig(env: Env = process.env): StripeConfig | null {
  return env.STRIPE_SECRET_KEY ? { secretKey: env.STRIPE_SECRET_KEY } : null;
}

export type SessionInput = { orderId: string; amountSen: number; email: string; description: string; successUrl: string; cancelUrl: string };

type Fetch = typeof fetch;

/** Card payments through Stripe Checkout (REST, no SDK needed). Amount is MYR sen. */
export async function createCheckoutSession(cfg: StripeConfig, i: SessionInput, fetchFn: Fetch = fetch): Promise<{ ref: string; url: string }> {
  const body = new URLSearchParams({
    mode: "payment",
    "payment_method_types[0]": "card",
    client_reference_id: i.orderId,
    customer_email: i.email,
    success_url: i.successUrl,
    cancel_url: i.cancelUrl,
    "line_items[0][quantity]": "1",
    "line_items[0][price_data][currency]": "myr",
    "line_items[0][price_data][unit_amount]": String(i.amountSen),
    "line_items[0][price_data][product_data][name]": i.description,
  });
  const res = await fetchFn("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: { authorization: `Bearer ${cfg.secretKey}`, "content-type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  if (!res.ok) throw new Error(`Stripe session failed (${res.status})`);
  const data = (await res.json()) as { id?: string; url?: string };
  if (!data.id || !data.url) throw new Error("Stripe session response missing id/url");
  return { ref: data.id, url: data.url };
}

const TOLERANCE_SECONDS = 300;

/** Verifies the `Stripe-Signature` header (t=...,v1=...) against the raw request body. */
export function verifyStripeSignature(rawBody: string, header: string | null, secret: string, nowSeconds = Math.floor(Date.now() / 1000)): boolean {
  if (!header || !secret) return false;
  const parts = Object.fromEntries(header.split(",").map((p) => p.split("=") as [string, string]));
  const t = Number(parts.t);
  const v1 = parts.v1;
  if (!Number.isFinite(t) || !v1 || Math.abs(nowSeconds - t) > TOLERANCE_SECONDS) return false;
  const expected = createHmac("sha256", secret).update(`${t}.${rawBody}`).digest();
  const given = Buffer.from(v1, "hex");
  return given.length === expected.length && timingSafeEqual(given, expected);
}
