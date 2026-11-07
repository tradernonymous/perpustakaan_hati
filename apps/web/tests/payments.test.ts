import { createHmac } from "node:crypto";
import { describe, expect, it, vi } from "vitest";
import { createBill, verifyBillplzCallback } from "@/src/server/billplz";
import { createCheckoutSession, verifyStripeSignature } from "@/src/server/stripe";

const hmac = (key: string, s: string) => createHmac("sha256", key).update(s).digest("hex");

describe("billplz", () => {
  const cfg = { apiKey: "key", collectionId: "col", xSignatureKey: "sigkey", baseUrl: "https://www.billplz-sandbox.com" };

  it("creates a bill with basic auth and returns the hosted url", async () => {
    const fetchFn = vi.fn(async () => new Response(JSON.stringify({ id: "b1", url: "https://pay/b1" }), { status: 200 }));
    const r = await createBill(cfg, { orderId: "o1", amountSen: 2900, email: "a@x.com", phone: "+60123456789", description: "Edisi Membangun", callbackUrl: "https://s/cb", redirectUrl: "https://s/ok" }, fetchFn as unknown as typeof fetch);
    expect(r).toEqual({ ref: "b1", url: "https://pay/b1" });
    const [url, init] = fetchFn.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("https://www.billplz-sandbox.com/api/v3/bills");
    expect((init.headers as Record<string, string>).authorization).toBe("Basic " + Buffer.from("key:").toString("base64"));
    const body = new URLSearchParams(init.body as string);
    expect(body.get("amount")).toBe("2900");
    expect(body.get("collection_id")).toBe("col");
    expect(body.get("reference_1")).toBe("o1");
    expect(body.get("mobile")).toBe("+60123456789");
  });
  it("throws on a failed bill", async () => {
    const fetchFn = vi.fn(async () => new Response("{}", { status: 422 }));
    await expect(createBill(cfg, { orderId: "o", amountSen: 100, email: "a@x.com", phone: null, description: "d", callbackUrl: "c", redirectUrl: "r" }, fetchFn as unknown as typeof fetch)).rejects.toThrow(/Billplz/);
  });
  it("verifies callback signatures (sorted key+value joined by |)", () => {
    const params = { id: "b1", paid: "true", state: "paid", amount: "2900", reference_1: "o1" };
    const source = Object.entries(params).map(([k, v]) => k + v).sort().join("|");
    const good = { ...params, x_signature: hmac("sigkey", source) };
    expect(verifyBillplzCallback(good, "sigkey")).toBe(true);
    expect(verifyBillplzCallback({ ...good, amount: "1" }, "sigkey")).toBe(false);
    expect(verifyBillplzCallback({ ...params }, "sigkey")).toBe(false);
    expect(verifyBillplzCallback(good, "")).toBe(false);
  });
});

describe("stripe", () => {
  it("creates a MYR card checkout session", async () => {
    const fetchFn = vi.fn(async () => new Response(JSON.stringify({ id: "cs_1", url: "https://checkout.stripe.com/c/cs_1" }), { status: 200 }));
    const r = await createCheckoutSession({ secretKey: "sk_test" }, { orderId: "o1", amountSen: 2900, email: "a@x.com", description: "Edisi Membangun", successUrl: "https://s/ok", cancelUrl: "https://s/no" }, fetchFn as unknown as typeof fetch);
    expect(r).toEqual({ ref: "cs_1", url: "https://checkout.stripe.com/c/cs_1" });
    const [, init] = fetchFn.mock.calls[0] as unknown as [string, RequestInit];
    const b = new URLSearchParams(init.body as string);
    expect(b.get("mode")).toBe("payment");
    expect(b.get("client_reference_id")).toBe("o1");
    expect(b.get("line_items[0][price_data][currency]")).toBe("myr");
    expect(b.get("line_items[0][price_data][unit_amount]")).toBe("2900");
    expect(b.get("payment_method_types[0]")).toBe("card");
    expect((init.headers as Record<string, string>).authorization).toBe("Bearer sk_test");
  });
  it("verifies webhook signatures and rejects stale or forged ones", () => {
    const body = '{"type":"checkout.session.completed"}';
    const t = 1_700_000_000;
    const sig = hmac("whsec", `${t}.${body}`);
    expect(verifyStripeSignature(body, `t=${t},v1=${sig}`, "whsec", t + 10)).toBe(true);
    expect(verifyStripeSignature(body, `t=${t},v1=${sig}`, "whsec", t + 10_000)).toBe(false);
    expect(verifyStripeSignature(body + " ", `t=${t},v1=${sig}`, "whsec", t + 10)).toBe(false);
    expect(verifyStripeSignature(body, `t=${t},v1=deadbeef`, "whsec", t + 10)).toBe(false);
    expect(verifyStripeSignature(body, null, "whsec", t)).toBe(false);
    expect(verifyStripeSignature(body, `t=${t},v1=${sig}`, "", t)).toBe(false);
  });
});
