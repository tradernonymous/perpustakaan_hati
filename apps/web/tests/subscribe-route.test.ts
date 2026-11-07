import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

let dir: string;
beforeEach(() => {
  dir = mkdtempSync(path.join(tmpdir(), "ph-route-"));
  process.env.DATA_DIR = dir;
  vi.resetModules();
});
afterEach(() => rmSync(dir, { recursive: true, force: true }));

const post = (body: unknown, ip = "1.2.3.4") =>
  new Request("http://localhost/api/subscribe", {
    method: "POST",
    headers: { "content-type": "application/json", "x-forwarded-for": ip },
    body: typeof body === "string" ? body : JSON.stringify(body),
  });

describe("POST /api/subscribe", () => {
  it("201 on a new valid signup", async () => {
    const { POST } = await import("@/app/api/subscribe/route");
    const res = await POST(post({ email: "a@b.co", consent: true }));
    expect(res.status).toBe(201);
  });
  it("201 with the same body on a duplicate (no leak)", async () => {
    const { POST } = await import("@/app/api/subscribe/route");
    await POST(post({ email: "a@b.co", consent: true }));
    const res = await POST(post({ email: "a@b.co", consent: true }));
    expect(res.status).toBe(201);
    expect(await res.json()).toEqual({ ok: true });
  });
  it("400 with a BM message on invalid input", async () => {
    const { POST } = await import("@/app/api/subscribe/route");
    const res = await POST(post({ email: "nope", consent: true }));
    expect(res.status).toBe(400);
    expect((await res.json()).error).toBeTypeOf("string");
  });
  it("400 on malformed JSON", async () => {
    const { POST } = await import("@/app/api/subscribe/route");
    expect((await POST(post("{not json"))).status).toBe(400);
  });
  it("pretends success for bots but stores nothing", async () => {
    const { POST } = await import("@/app/api/subscribe/route");
    const res = await POST(post({ email: "bot@b.co", consent: true, website: "x" }));
    expect(res.status).toBe(201);
    const { openStore } = await import("@/src/server/store");
    const s = openStore(path.join(dir, "subscribers.db"));
    expect(s.count()).toBe(0);
    s.close();
  });
  it("429 after too many requests from one IP", async () => {
    const { POST } = await import("@/app/api/subscribe/route");
    let last = 0;
    for (let i = 0; i < 12; i++) last = (await POST(post({ email: `u${i}@b.co`, consent: true }, "9.9.9.9"))).status;
    expect(last).toBe(429);
  });
});
