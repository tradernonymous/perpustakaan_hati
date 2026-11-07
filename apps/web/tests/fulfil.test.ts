import { PDFDocument } from "pdf-lib";
import { describe, expect, it, vi } from "vitest";
import { signToken, verifyToken } from "@/src/server/tokens";
import { watermarkPdf } from "@/src/server/watermark";
import { deliverOrder } from "@/src/server/fulfil";
import { openOrders } from "@/src/server/orders";

const secret = "s".repeat(32);

describe("tokens", () => {
  it("round-trips a payload before expiry", () => {
    const t = signToken({ k: "dl", o: "order1", p: "membangun" }, secret, 1000, 100);
    expect(verifyToken(t, secret, 500)).toMatchObject({ k: "dl", o: "order1", p: "membangun" });
  });
  it("rejects expired, tampered, wrong-secret and malformed tokens", () => {
    const t = signToken({ k: "dl" }, secret, 1000, 100);
    expect(verifyToken(t, secret, 1101)).toBeNull();
    const [body, sig] = t.split(".");
    const forged = Buffer.from(JSON.stringify({ k: "admin", exp: 9999 })).toString("base64url");
    expect(verifyToken(`${forged}.${sig}`, secret, 500)).toBeNull();
    expect(verifyToken(`${body}.AAAA`, secret, 500)).toBeNull();
    expect(verifyToken(t, "x".repeat(32), 500)).toBeNull();
    expect(verifyToken("garbage", secret, 500)).toBeNull();
    expect(verifyToken(t, "", 500)).toBeNull();
  });
});

describe("watermarkPdf", () => {
  it("keeps the page count and stamps the buyer on every page", async () => {
    const src = await PDFDocument.create();
    src.addPage(); src.addPage();
    const out = await watermarkPdf(await src.save(), "Dilesenkan kepada a@x.com");
    const doc = await PDFDocument.load(out);
    expect(doc.getPageCount()).toBe(2);
    expect(Buffer.from(out).length).toBeGreaterThan((await src.save()).length);
  });
  it("tolerates non-latin characters in the stamp", async () => {
    const src = await PDFDocument.create();
    src.addPage();
    await expect(watermarkPdf(await src.save(), "Dilesenkan kepada ünï@x.com — 日本")).resolves.toBeInstanceOf(Uint8Array);
  });
});

describe("deliverOrder", () => {
  const mk = () => {
    const orders = openOrders(":memory:");
    const o = orders.create({ items: ["membangun", "teman-hidup"], amountSen: 7900, email: "a@x.com", phone: "+60123456789", provider: "billplz" });
    return { orders, o };
  };
  const env = { DOWNLOAD_SECRET: secret, SITE_URL: "https://s.test", RESEND_API_KEY: "re", EMAIL_FROM: "Hati <hi@s.test>", WHATSAPP_TOKEN: "wa", WHATSAPP_PHONE_ID: "123" };

  it("sends email and WhatsApp with signed links and records both", async () => {
    const { orders, o } = mk();
    const fetchFn = vi.fn(async () => new Response("{}", { status: 200 }));
    const r = await deliverOrder(o, { orders, env, fetchFn: fetchFn as unknown as typeof fetch, now: () => 1_000 });
    expect(r).toEqual({ email: "ok", whatsapp: "ok" });
    const urls = fetchFn.mock.calls.map((c) => (c as unknown as [string])[0]);
    expect(urls[0]).toBe("https://api.resend.com/emails");
    expect(urls[1]).toBe("https://graph.facebook.com/v21.0/123/messages");
    const mail = JSON.parse((fetchFn.mock.calls[0] as unknown as [string, RequestInit])[1].body as string);
    expect(mail.to).toEqual(["a@x.com"]);
    expect(mail.text).toContain("https://s.test/muat-turun/");
    expect(mail.text.match(/muat-turun\//g)).toHaveLength(2);
    expect(orders.deliveries(o.id).map((d) => `${d.channel}:${d.status}`).sort()).toEqual(["email:ok", "whatsapp:ok"]);
  });
  it("still sends email when WhatsApp fails, and records the error", async () => {
    const { orders, o } = mk();
    const fetchFn = vi.fn(async (u: string) => new Response("{}", { status: u.includes("facebook") ? 400 : 200 }));
    const r = await deliverOrder(o, { orders, env, fetchFn: fetchFn as unknown as typeof fetch });
    expect(r).toEqual({ email: "ok", whatsapp: "error" });
  });
  it("skips channels that are not configured or have no phone", async () => {
    const { orders, o } = mk();
    const fetchFn = vi.fn(async () => new Response("{}", { status: 200 }));
    const r = await deliverOrder(o, { orders, env: { DOWNLOAD_SECRET: secret, SITE_URL: "https://s.test" }, fetchFn: fetchFn as unknown as typeof fetch });
    expect(r).toEqual({ email: "skipped", whatsapp: "skipped" });
    expect(fetchFn).not.toHaveBeenCalled();
  });
  it("gives up on a hung provider within the time limit instead of blocking", async () => {
    const { orders, o } = mk();
    const hang = vi.fn((_u: string, init?: RequestInit) => new Promise<Response>((_, rej) => init?.signal?.addEventListener("abort", () => rej(new Error("aborted")))));
    const t0 = Date.now();
    const r = await deliverOrder(o, { orders, env, fetchFn: hang as unknown as typeof fetch, timeoutMs: 50 });
    expect(Date.now() - t0).toBeLessThan(1000);
    expect(r).toEqual({ email: "error", whatsapp: "error" });
  });
  it("refuses to run without a download secret", async () => {
    const { orders, o } = mk();
    await expect(deliverOrder(o, { orders, env: {}, fetchFn: vi.fn() as unknown as typeof fetch })).rejects.toThrow(/DOWNLOAD_SECRET/);
  });
});
