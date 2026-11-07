import type { Env } from "../env";
import { cartItems, cartTotalSen, isProductId, PRODUCTS, type Cart } from "../catalog";
import { billplzConfig, createBill } from "./billplz";
import type { Orders } from "./orders";
import { createCheckoutSession, stripeConfig } from "./stripe";
import { EMAIL, MY_MOBILE } from "./validate";

export type Method = "fpx" | "card";
export type CheckoutValue = { cart: Cart; email: string; phone: string | null; method: Method };
export type CheckoutValidation = { ok: true; value: CheckoutValue } | { ok: false; error: string };

const fail = (error: string): CheckoutValidation => ({ ok: false, error });

export function validateCheckout(input: unknown): CheckoutValidation {
  if (typeof input !== "object" || input === null) return fail("Permintaan tidak sah.");
  const b = input as Record<string, unknown>;
  if (!isProductId(b.product)) return fail("Produk tidak dijumpai.");
  const email = typeof b.email === "string" ? b.email.trim().toLowerCase() : "";
  if (!email || email.length > 254 || !EMAIL.test(email)) return fail("Sila isi alamat e-mel yang sah. Kami hantar buku ke sini.");
  const rawPhone = typeof b.phone === "string" ? b.phone.replace(/[\s-]/g, "") : "";
  let phone: string | null = null;
  if (rawPhone) {
    const m = MY_MOBILE.exec(rawPhone);
    if (!m) return fail("Nombor WhatsApp mesti nombor mudah alih Malaysia, contoh 012-345 6789.");
    phone = `+60${m[1]}`;
  }
  if (b.method !== "fpx" && b.method !== "card") return fail("Sila pilih kaedah bayaran.");
  if (b.consent !== true) return fail("Sila setuju dengan notis privasi (PDPA) untuk teruskan.");
  return { ok: true, value: { cart: { product: b.product, bump: b.bump === true }, email, phone, method: b.method } };
}

export type CheckoutDeps = { orders: Orders; env: Env; baseUrl: string; fetchFn?: typeof fetch };
export type CheckoutResult = { ok: true; url: string; orderId: string } | { ok: false; status: 503 | 502; error: string };

export async function startCheckout(v: CheckoutValue, d: CheckoutDeps): Promise<CheckoutResult> {
  const bill = v.method === "fpx" ? billplzConfig(d.env) : null;
  const stripe = v.method === "card" ? stripeConfig(d.env) : null;
  if (!bill && !stripe) return { ok: false, status: 503, error: "Kaedah bayaran ini belum tersedia. Cuba kaedah lain atau datang semula nanti." };

  const items = cartItems(v.cart);
  const amountSen = cartTotalSen(v.cart, d.env);
  const description = items.map((i) => PRODUCTS[i].name).join(" + ");
  const order = d.orders.create({ items, amountSen, email: v.email, phone: v.phone, provider: bill ? "billplz" : "stripe" });
  const returnUrl = `${d.baseUrl}/terima-kasih?order=${order.id}`;

  try {
    const r = bill
      ? await createBill(bill, { orderId: order.id, amountSen, email: v.email, phone: v.phone, description, callbackUrl: `${d.baseUrl}/api/webhooks/billplz`, redirectUrl: returnUrl }, d.fetchFn)
      : await createCheckoutSession(stripe!, { orderId: order.id, amountSen, email: v.email, description, successUrl: returnUrl, cancelUrl: `${d.baseUrl}/beli/${v.cart.product}` }, d.fetchFn);
    d.orders.setProviderRef(order.id, r.ref);
    return { ok: true, url: r.url, orderId: order.id };
  } catch {
    return { ok: false, status: 502, error: "Tidak dapat memulakan pembayaran sekarang. Cuba lagi sebentar." };
  }
}

export type PaidOutcome = "paid" | "duplicate" | "unknown-order" | "amount-mismatch";

/**
 * Called by a verified webhook. Checks the amount the provider says was paid against
 * the order, flips it to paid exactly once, and only then triggers delivery.
 */
export async function handlePaid(
  orders: Orders,
  orderId: string,
  providerRef: string,
  paidAmountSen: number,
  onPaid: (orderId: string) => Promise<void>,
): Promise<PaidOutcome> {
  const order = orders.get(orderId);
  if (!order) return "unknown-order";
  if (order.amountSen !== paidAmountSen) return "amount-mismatch";
  if (!orders.markPaid(orderId, providerRef).changed) return "duplicate";
  await onPaid(orderId);
  return "paid";
}
