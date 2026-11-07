import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

let dir: string;
beforeAll(() => {
  dir = mkdtempSync(path.join(tmpdir(), "ph-admin-"));
  process.env.DATA_DIR = dir;
  process.env.ADMIN_TOKEN = "tok-123456789";
});
afterAll(() => rmSync(dir, { recursive: true, force: true }));

describe("GET /admin/subscribers", () => {
  it("asks for a login without credentials", async () => {
    const { GET } = await import("@/app/admin/subscribers/route");
    const res = GET(new Request("http://x/admin/subscribers"));
    expect(res.status).toBe(401);
    expect(res.headers.get("www-authenticate")).toContain("Basic");
  });
  it("returns a CSV with the token", async () => {
    const { getStore } = await import("@/src/server/instance");
    getStore().add({ email: "a@x.com", phone: null });
    const { GET } = await import("@/app/admin/subscribers/route");
    const res = GET(new Request("http://x/admin/subscribers", { headers: { authorization: "Bearer tok-123456789" } }));
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toContain("text/csv");
    expect(await res.text()).toContain("a@x.com");
  });
});
