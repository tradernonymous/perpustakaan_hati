import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { openOrders, type Orders } from "@/src/server/orders";
import { handlePaid, startCheckout, validateCheckout } from "@/src/server/checkout";

const ok = { product: "membangun", bump: false, email: "A@X.com", phone: "012-345 6789", method: "fpx", consent: true };

describe("validateCheckout", () => {
  it("normalises a good request", () => {
    expect(validateCheckout(ok)).toEqual({ ok: true, value: { cart: { product: "membangun", bump: false }, email: "a@x.com", phone: "+60123456789", method: "fpx" } });
  });
  it.each([
    [{ ...ok, product: "poket" }, /produk/i],
    [{ ...ok, product: "__proto__" }, /produk/i],
    [{ ...ok, email: "" }, /e-mel/i],
    [{ ...ok, email: "nope" }, /e-mel/i],
    [{ ...ok, phone: "123" }, /whatsapp/i],
    [{ ...ok, method: "paypal" }, /kaedah/i],
    [{ ...ok, consent: false }, /pdpa/i],
    [null, /tidak sah/i],
  ])("rejects %j", (input, msg) => {
    const r = validateCheckout(input);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error).toMatch(msg);
  });
  it("allows an empty phone", () => {
    const r = validateCheckout({ ...ok, phone: "" });
    expect(r).toMatchObject({ ok: true, value: { phone: null } });
  });
});

describe("startCheckout", () => {
  let orders: Orders;
  beforeEach(() => { orders = openOrders(":memory:"); });
  afterEach(() => orders.close());
  const env = { BILLPLZ_API_KEY: "k", BILLPLZ_COLLECTION_ID: "c", BILLPLZ_X_SIGNATURE: "s", STRIPE_SECRET_KEY: "sk" };
  const valid = validateCheckout(ok);
  if (!valid.ok) throw new Error("fixture");

  it("fpx goes through billplz and stores the bill id", async () => {
    const fetchFn = vi.fn(async () => new Response(JSON.stringify({ id: "b1", url: "https://pay/b1" }), { status: 200 }));
    const r = await startCheckout(valid.value, { orders, env, baseUrl: "https://s.test", fetchFn: fetchFn as unknown as typeof fetch });
    expect(r).toEqual({ ok: true, url: "https://pay/b1", orderId: expect.any(String) });
    if (r.ok) expect(orders.get(r.orderId)).toMatchObject({ provider: "billplz", providerRef: "b1", amountSen: 2900, status: "pending" });
    const body = new URLSearchParams((fetchFn.mock.calls[0] as unknown as [string, RequestInit])[1].body as string);
    expect(body.get("callback_url")).toBe("https://s.test/api/webhooks/billplz");
    expect(body.get("redirect_url")).toMatch(/^https:\/\/s\.test\/terima-kasih\?order=/);
  });
  it("card goes through stripe, with the bump priced in", async () => {
    const fetchFn = vi.fn(async () => new Response(JSON.stringify({ id: "cs_1", url: "https://stripe/cs_1" }), { status: 200 }));
    const r = await startCheckout({ ...valid.value, method: "card", cart: { product: "membangun", bump: true } }, { orders, env, baseUrl: "https://s.test", fetchFn: fetchFn as unknown as typeof fetch });
    expect(r.ok).toBe(true);
    if (r.ok) expect(orders.get(r.orderId)).toMatchObject({ provider: "stripe", items: ["membangun", "teman-hidup"], amountSen: 7900 });
  });
  it("reports an unconfigured provider without creating an order", async () => {
    const r = await startCheckout(valid.value, { orders, env: {}, baseUrl: "https://s.test", fetchFn: vi.fn() as unknown as typeof fetch });
    expect(r).toEqual({ ok: false, status: 503, error: expect.stringMatching(/belum tersedia/i) });
    expect(orders.listPaidByEmail("a@x.com")).toEqual([]);
  });
  it("reports a provider failure as 502", async () => {
    const fetchFn = vi.fn(async () => new Response("{}", { status: 500 }));
    const r = await startCheckout(valid.value, { orders, env, baseUrl: "https://s.test", fetchFn: fetchFn as unknown as typeof fetch });
    expect(r).toMatchObject({ ok: false, status: 502 });
  });
});

describe("handlePaid", () => {
  it("runs the delivery hook only on the first paid notification", async () => {
    const orders = openOrders(":memory:");
    const o = orders.create({ items: ["membangun"], amountSen: 2900, email: "a@x.com", phone: null, provider: "billplz" });
    const onPaid = vi.fn(async () => {});
    expect(await handlePaid(orders, o.id, "b1", 2900, onPaid)).toBe("paid");
    expect(await handlePaid(orders, o.id, "b1", 2900, onPaid)).toBe("duplicate");
    expect(onPaid).toHaveBeenCalledTimes(1);
    orders.close();
  });
  it("rejects an amount that does not match the order", async () => {
    const orders = openOrders(":memory:");
    const o = orders.create({ items: ["membangun"], amountSen: 2900, email: "a@x.com", phone: null, provider: "billplz" });
    const onPaid = vi.fn(async () => {});
    expect(await handlePaid(orders, o.id, "b1", 100, onPaid)).toBe("amount-mismatch");
    expect(orders.get(o.id)?.status).toBe("pending");
    expect(onPaid).not.toHaveBeenCalled();
    expect(await handlePaid(orders, "unknown", "b", 1, onPaid)).toBe("unknown-order");
    orders.close();
  });
});
