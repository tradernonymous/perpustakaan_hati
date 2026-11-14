import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

let dir: string;
beforeEach(() => {
  dir = mkdtempSync(path.join(tmpdir(), "ph-routes-"));
  process.env.DATA_DIR = dir;
  vi.resetModules();
});
afterEach(() => rmSync(dir, { recursive: true, force: true }));

const postJson = (url: string, body: unknown, ip = "10.0.0.1") =>
  new Request(url, {
    method: "POST",
    headers: { "content-type": "application/json", "x-forwarded-for": ip },
    body: JSON.stringify(body),
  });

describe("POST /api/surat", () => {
  it("stores anonymized dilemma and strips the alias from text", async () => {
    const { POST } = await import("@/app/api/surat/route");
    const res = await POST(
      postJson("http://localhost/api/surat", {
        name: "Aina",
        dilemma: "Saya Aina rasa penat memujuk pasangan setiap minggu.",
        consentPublish: true,
      }),
    );
    expect(res.status).toBe(201);
    const { openSuratStore } = await import("@/src/server/surat-store");
    const store = openSuratStore(path.join(dir, "surat.db"));
    expect(store.count()).toBe(1);
    const row = store.list()[0];
    expect(row.anonymized_dilemma).not.toContain("Aina");
    expect(row.anonymized_dilemma).toContain("[nama disembunyikan]");
    store.close();
  });

  it("rejects empty dilemma with 400", async () => {
    const { POST } = await import("@/app/api/surat/route");
    const res = await POST(postJson("http://localhost/api/surat", { name: "Aina", dilemma: "hi" }));
    expect(res.status).toBe(400);
  });
});

describe("POST /api/booking", () => {
  it("persists a valid booking request with calculated quoteSen", async () => {
    const { POST } = await import("@/app/api/booking/route");
    const res = await POST(
      postJson("http://localhost/api/booking", {
        name: "Amirul",
        email: "amirul@contoh.my",
        phone: "012-345 6789",
        sessionType: "couples",
        notes: "Malam hari bekerja",
        consent: true,
      }),
    );
    expect(res.status).toBe(201);
    const body = (await res.json()) as { ok: boolean; quoteSen: number };
    expect(body.ok).toBe(true);
    expect(body.quoteSen).toBe(35000);

    const { openBookingStore } = await import("@/src/server/booking-store");
    const store = openBookingStore(path.join(dir, "booking.db"));
    expect(store.count()).toBe(1);
    expect(store.list()[0].phone).toBe("+60123456789");
    store.close();
  });

  it("rejects missing PDPA consent or invalid Malaysian phone", async () => {
    const { POST } = await import("@/app/api/booking/route");
    const badPhone = await POST(
      postJson("http://localhost/api/booking", {
        name: "Amirul",
        email: "amirul@contoh.my",
        phone: "999",
        sessionType: "clarity",
        consent: true,
      }),
    );
    expect(badPhone.status).toBe(400);

    const noConsent = await POST(
      postJson("http://localhost/api/booking", {
        name: "Amirul",
        email: "amirul@contoh.my",
        phone: "0123456789",
        sessionType: "clarity",
        consent: false,
      }),
    );
    expect(noConsent.status).toBe(400);
  });
});
