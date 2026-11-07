import { createHmac } from "node:crypto";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

let dir: string;
beforeAll(() => {
  dir = mkdtempSync(path.join(tmpdir(), "ph-wh-"));
  Object.assign(process.env, {
    DATA_DIR: dir, BILLPLZ_API_KEY: "k", BILLPLZ_COLLECTION_ID: "c", BILLPLZ_X_SIGNATURE: "sigkey",
    STRIPE_WEBHOOK_SECRET: "whsec", DOWNLOAD_SECRET: "d".repeat(32), SITE_URL: "https://s.test",
  });
  delete process.env.RESEND_API_KEY;
});
afterAll(() => rmSync(dir, { recursive: true, force: true }));

const sign = (params: Record<string, string>) =>
  createHmac("sha256", "sigkey").update(Object.entries(params).map(([k, v]) => k + v).sort().join("|")).digest("hex");
const form = (params: Record<string, string>) => new URLSearchParams({ ...params, x_signature: sign(params) }).toString();

async function seed(provider: "billplz" | "stripe", ref: string) {
  const { getOrders } = await import("@/src/server/instance");
  const o = getOrders().create({ items: ["membangun"], amountSen: 2900, email: "a@x.com", phone: null, provider });
  getOrders().setProviderRef(o.id, ref);
  return { o, orders: getOrders() };
}

describe("billplz webhook", () => {
  it("rejects a forged callback and leaves the order pending", async () => {
    const { POST } = await import("@/app/api/webhooks/billplz/route");
    const { o, orders } = await seed("billplz", "bill-forged");
    const res = await POST(new Request("http://x", { method: "POST", body: new URLSearchParams({ id: "bill-forged", paid: "true", paid_amount: "2900", x_signature: "00" }).toString() }));
    expect(res.status).toBe(401);
    expect(orders.get(o.id)?.status).toBe("pending");
  });
  it("marks a signed paid callback as paid exactly once and attempts delivery", async () => {
    const { POST } = await import("@/app/api/webhooks/billplz/route");
    const { o, orders } = await seed("billplz", "bill-1");
    const body = form({ id: "bill-1", paid: "true", paid_amount: "2900", amount: "2900", state: "paid" });
    const first = await POST(new Request("http://x", { method: "POST", body }));
    expect(await first.text()).toBe("paid");
    expect(orders.get(o.id)?.status).toBe("paid");
    const second = await POST(new Request("http://x", { method: "POST", body }));
    expect(await second.text()).toBe("duplicate");
    expect(orders.deliveries(o.id).length).toBe(0); // no mail/WhatsApp keys set: both skipped, nothing recorded
  });
  it("ignores an unpaid callback and a wrong amount", async () => {
    const { POST } = await import("@/app/api/webhooks/billplz/route");
    const { o, orders } = await seed("billplz", "bill-2");
    const unpaid = await POST(new Request("http://x", { method: "POST", body: form({ id: "bill-2", paid: "false", paid_amount: "0" }) }));
    expect(unpaid.status).toBe(200);
    const wrong = await POST(new Request("http://x", { method: "POST", body: form({ id: "bill-2", paid: "true", paid_amount: "100" }) }));
    expect(await wrong.text()).toBe("amount-mismatch");
    expect(orders.get(o.id)?.status).toBe("pending");
  });
});

describe("stripe webhook", () => {
  const signed = (raw: string) => {
    const t = Math.floor(Date.now() / 1000);
    return `t=${t},v1=${createHmac("sha256", "whsec").update(`${t}.${raw}`).digest("hex")}`;
  };
  it("pays the order named in client_reference_id", async () => {
    const { POST } = await import("@/app/api/webhooks/stripe/route");
    const { o, orders } = await seed("stripe", "cs_1");
    const raw = JSON.stringify({ type: "checkout.session.completed", data: { object: { id: "cs_1", client_reference_id: o.id, payment_status: "paid", amount_total: 2900 } } });
    const res = await POST(new Request("http://x", { method: "POST", body: raw, headers: { "stripe-signature": signed(raw) } }));
    expect(await res.text()).toBe("paid");
    expect(orders.get(o.id)?.status).toBe("paid");
  });
  it("rejects a bad signature", async () => {
    const { POST } = await import("@/app/api/webhooks/stripe/route");
    const res = await POST(new Request("http://x", { method: "POST", body: "{}", headers: { "stripe-signature": "t=1,v1=00" } }));
    expect(res.status).toBe(401);
  });
});

describe("download route", () => {
  it("serves a stamped PDF for a valid token and refuses bad or unpaid ones", async () => {
    const { PDFDocument } = await import("pdf-lib");
    const { mkdirSync, writeFileSync } = await import("node:fs");
    mkdirSync(path.join(dir, "assets"), { recursive: true });
    const src = await PDFDocument.create(); src.addPage();
    writeFileSync(path.join(dir, "assets", "edisi-membangun.pdf"), await src.save());

    const { GET } = await import("@/app/muat-turun/[token]/route");
    const { signToken } = await import("@/src/server/tokens");
    const { o, orders } = await seed("billplz", "bill-dl");
    const token = signToken({ k: "dl", o: o.id, p: "membangun" }, process.env.DOWNLOAD_SECRET!, 600);

    expect((await GET(new Request("http://x"), { params: Promise.resolve({ token }) })).status).toBe(404); // not paid yet
    orders.markPaid(o.id, "bill-dl");
    const ok = await GET(new Request("http://x"), { params: Promise.resolve({ token }) });
    expect(ok.status).toBe(200);
    expect(ok.headers.get("content-type")).toBe("application/pdf");
    expect((await ok.arrayBuffer()).byteLength).toBeGreaterThan(500);

    const bad = await GET(new Request("http://x"), { params: Promise.resolve({ token: token + "x" }) });
    expect(bad.status).toBe(410);
    const other = signToken({ k: "dl", o: o.id, p: "teman-hidup" }, process.env.DOWNLOAD_SECRET!, 600);
    expect((await GET(new Request("http://x"), { params: Promise.resolve({ token: other }) })).status).toBe(404);
  });
});
