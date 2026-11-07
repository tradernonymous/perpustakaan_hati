import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { ChapterPreview } from "@/components/ChapterPreview";
import { ProductCover } from "@/components/ProductCover";
import { TierCompare } from "@/components/TierCompare";
import { openOrders } from "@/src/server/orders";
import { startCheckout, validateCheckout } from "@/src/server/checkout";

describe("cover slots", () => {
  it("shows a labelled placeholder when no cover image is set", () => {
    const html = renderToStaticMarkup(<ProductCover name="Edisi Membangun" src={null} />);
    expect(html).toContain("Kulit buku akan datang");
    expect(html).not.toContain("<img");
  });
  it("shows the image when a cover is set", () => {
    const html = renderToStaticMarkup(<ProductCover name="X" src="/products/x.png" />);
    expect(html).toContain('src="/products/x.png"');
  });
  it("every tier card has a cover slot", () => {
    expect(renderToStaticMarkup(<TierCompare />).match(/data-cover-slot/g)).toHaveLength(3);
  });
});

describe("held-back chapters", () => {
  it("shows Bab 4 and 5 as pending without leaking the unconfirmed titles", () => {
    const html = renderToStaticMarkup(<ChapterPreview />);
    expect(html).toContain("Bab 4");
    expect(html).toContain("Bab 5");
    expect(html).toContain("Tajuk akan diumumkan");
    expect(html).not.toContain("Bicornak");
  });
});

describe("demo checkout", () => {
  const v = validateCheckout({ product: "membangun", bump: false, email: "a@x.com", phone: "", method: "fpx", consent: true });
  if (!v.ok) throw new Error("fixture");
  it("is refused without DEMO_MODE", async () => {
    const orders = openOrders(":memory:");
    expect(await startCheckout(v.value, { orders, env: {}, baseUrl: "https://s" })).toMatchObject({ ok: false, status: 503 });
    orders.close();
  });
  it("routes to the demo pay page when DEMO_MODE=1 and no provider keys exist", async () => {
    const orders = openOrders(":memory:");
    const r = await startCheckout(v.value, { orders, env: { DEMO_MODE: "1" }, baseUrl: "https://s" });
    expect(r).toMatchObject({ ok: true, url: expect.stringMatching(/^https:\/\/s\/demo-bayar\?order=/) });
    if (r.ok) expect(orders.get(r.orderId)).toMatchObject({ provider: "demo", status: "pending" });
    orders.close();
  });
});

describe("demo pay route + placeholder PDF", () => {
  let dir: string;
  beforeAll(() => { dir = mkdtempSync(path.join(tmpdir(), "ph-demo-")); Object.assign(process.env, { DATA_DIR: dir, DOWNLOAD_SECRET: "d".repeat(32) }); });
  afterAll(() => { rmSync(dir, { recursive: true, force: true }); delete process.env.DEMO_MODE; });

  it("404s when demo mode is off", async () => {
    delete process.env.DEMO_MODE;
    const { POST } = await import("@/app/api/demo/pay/route");
    expect((await POST(new Request("http://x", { method: "POST", body: JSON.stringify({ order: "x" }) }))).status).toBe(404);
  });
  it("pays a demo order and serves a stamped placeholder PDF when the real file is missing", async () => {
    process.env.DEMO_MODE = "1";
    const { getOrders } = await import("@/src/server/instance");
    const o = getOrders().create({ items: ["membangun"], amountSen: 2900, email: "a@x.com", phone: null, provider: "demo" });
    const { POST } = await import("@/app/api/demo/pay/route");
    const res = await POST(new Request("http://x", { method: "POST", body: JSON.stringify({ order: o.id }) }));
    expect(res.status).toBe(200);
    expect(getOrders().get(o.id)?.status).toBe("paid");
    const { signToken } = await import("@/src/server/tokens");
    const { GET } = await import("@/app/muat-turun/[token]/route");
    const token = signToken({ k: "dl", o: o.id, p: "membangun" }, process.env.DOWNLOAD_SECRET!, 600);
    const dl = await GET(new Request("http://x"), { params: Promise.resolve({ token }) });
    expect(dl.status).toBe(200);
    expect(dl.headers.get("content-type")).toBe("application/pdf");
  });
  it("does not pay a non-demo order through the demo route", async () => {
    process.env.DEMO_MODE = "1";
    const { getOrders } = await import("@/src/server/instance");
    const o = getOrders().create({ items: ["membangun"], amountSen: 2900, email: "b@x.com", phone: null, provider: "billplz" });
    const { POST } = await import("@/app/api/demo/pay/route");
    expect((await POST(new Request("http://x", { method: "POST", body: JSON.stringify({ order: o.id }) }))).status).toBe(404);
    expect(getOrders().get(o.id)?.status).toBe("pending");
  });
});
