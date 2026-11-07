import { describe, expect, it, vi } from "vitest";
import { libraryFor, requestLoginLink } from "@/src/server/library";
import { openOrders } from "@/src/server/orders";

const secret = "s".repeat(32);
const env = { DOWNLOAD_SECRET: secret, SITE_URL: "https://s.test", RESEND_API_KEY: "re", EMAIL_FROM: "Hati <hi@s.test>" };

function setup() {
  const orders = openOrders(":memory:");
  const paid = orders.create({ items: ["membangun"], amountSen: 2900, email: "a@x.com", phone: null, provider: "billplz" });
  orders.markPaid(paid.id, "r");
  orders.create({ items: ["teman-hidup"], amountSen: 7900, email: "a@x.com", phone: null, provider: "stripe" });
  return { orders, paid };
}

describe("library login", () => {
  it("emails a link only when the address has a paid order", async () => {
    const { orders } = setup();
    const fetchFn = vi.fn(async () => new Response("{}", { status: 200 }));
    expect(await requestLoginLink("A@x.com", { orders, env, fetchFn: fetchFn as unknown as typeof fetch })).toBe(true);
    expect(await requestLoginLink("nobody@x.com", { orders, env, fetchFn: fetchFn as unknown as typeof fetch })).toBe(false);
    expect(fetchFn).toHaveBeenCalledTimes(1);
    const body = JSON.parse((fetchFn.mock.calls[0] as unknown as [string, RequestInit])[1].body as string);
    expect(body.to).toEqual(["a@x.com"]);
    expect(body.text).toContain("https://s.test/pustaka?t=");
  });
  it("opens the library with a valid link and lists only paid items with fresh links", async () => {
    const { orders } = setup();
    const fetchFn = vi.fn(async () => new Response("{}", { status: 200 }));
    await requestLoginLink("a@x.com", { orders, env, fetchFn: fetchFn as unknown as typeof fetch });
    const text = JSON.parse((fetchFn.mock.calls[0] as unknown as [string, RequestInit])[1].body as string).text as string;
    const token = text.match(/\?t=([\w.-]+)/)![1];
    const lib = libraryFor(token, { orders, env });
    expect(lib).not.toBeNull();
    expect(lib!.email).toBe("a@x.com");
    expect(lib!.items.map((i) => i.name)).toEqual(["Edisi Membangun"]);
    expect(lib!.items[0].url).toContain("https://s.test/muat-turun/");
  });
  it("rejects a download token used as a library token", () => {
    const { orders } = setup();
    expect(libraryFor("junk.token", { orders, env })).toBeNull();
  });
});
