import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { openOrders, type Orders } from "@/src/server/orders";

let o: Orders;
beforeEach(() => { o = openOrders(":memory:"); });
afterEach(() => o.close());

const base = { items: ["membangun"] as const, amountSen: 2900, email: "a@x.com", phone: null, provider: "billplz" as const };

describe("orders", () => {
  it("creates a pending order with an unguessable id", () => {
    const a = o.create({ ...base, items: ["membangun"] });
    const b = o.create({ ...base, items: ["membangun"] });
    expect(a.id).toMatch(/^[0-9a-f-]{36}$/);
    expect(a.id).not.toBe(b.id);
    expect(o.get(a.id)).toMatchObject({ status: "pending", amountSen: 2900, items: ["membangun"], email: "a@x.com" });
  });
  it("marks paid once and reports whether it changed", () => {
    const a = o.create({ ...base, items: ["membangun"] });
    expect(o.markPaid(a.id, "ref-1")).toEqual({ changed: true });
    expect(o.markPaid(a.id, "ref-1")).toEqual({ changed: false });
    expect(o.get(a.id)).toMatchObject({ status: "paid", providerRef: "ref-1" });
  });
  it("returns false for unknown orders", () => {
    expect(o.markPaid("00000000-0000-0000-0000-000000000000", "x")).toEqual({ changed: false });
    expect(o.get("nope")).toBeNull();
  });
  it("sets the provider ref after checkout creation", () => {
    const a = o.create({ ...base, items: ["membangun"] });
    o.setProviderRef(a.id, "bill-9");
    expect(o.get(a.id)?.providerRef).toBe("bill-9");
    expect(o.findByProviderRef("billplz", "bill-9")?.id).toBe(a.id);
  });
  it("lists only paid orders for an email, case-insensitive", () => {
    const a = o.create({ ...base, items: ["membangun"] });
    o.create({ ...base, items: ["teman-hidup"] });
    o.markPaid(a.id, "r");
    expect(o.listPaidByEmail("A@X.com").map((x) => x.id)).toEqual([a.id]);
    expect(o.listPaidByEmail("other@x.com")).toEqual([]);
  });
});
