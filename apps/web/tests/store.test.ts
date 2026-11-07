import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { openStore, type Store } from "@/src/server/store";

let dir: string;
let store: Store;
beforeEach(() => {
  dir = mkdtempSync(path.join(tmpdir(), "ph-store-"));
  store = openStore(path.join(dir, "subscribers.db"));
});
afterEach(() => {
  store.close();
  rmSync(dir, { recursive: true, force: true });
});

describe("store", () => {
  it("saves a new subscriber", () => {
    expect(store.add({ email: "a@b.co", phone: null })).toEqual({ created: true });
    expect(store.count()).toBe(1);
  });
  it("treats a duplicate email as not created, no error", () => {
    store.add({ email: "a@b.co", phone: null });
    expect(store.add({ email: "a@b.co", phone: null })).toEqual({ created: false });
    expect(store.count()).toBe(1);
  });
  it("treats a duplicate phone as not created", () => {
    store.add({ email: null, phone: "+60123456789" });
    expect(store.add({ email: null, phone: "+60123456789" })).toEqual({ created: false });
  });
  it("stores injection-looking input as plain data", () => {
    store.add({ email: "x'); DROP TABLE subscribers;--@b.co", phone: null });
    expect(store.count()).toBe(1);
  });
  it("creates the parent directory if missing", () => {
    const nested = openStore(path.join(dir, "deep", "er", "s.db"));
    expect(nested.count()).toBe(0);
    nested.close();
  });
});

describe("store.list", () => {
  it("returns every subscriber, newest first", async () => {
    const { openStore } = await import("@/src/server/store");
    const s = openStore(":memory:");
    s.add({ email: "a@x.com", phone: null });
    s.add({ email: null, phone: "+60123456789" });
    const rows = s.list();
    expect(rows).toHaveLength(2);
    expect(rows.map((r) => r.email ?? r.phone).sort()).toEqual(["+60123456789", "a@x.com"]);
    expect(rows[0]).toHaveProperty("created_at");
    s.close();
  });
});
