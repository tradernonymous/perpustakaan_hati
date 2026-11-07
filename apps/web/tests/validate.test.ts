import { describe, expect, it } from "vitest";
import { validateSubscribe } from "@/src/server/validate";

const ok = { email: "aina@example.com", consent: true };

describe("validateSubscribe", () => {
  it("accepts a valid email with consent", () => {
    const r = validateSubscribe(ok);
    expect(r).toEqual({ ok: true, bot: false, value: { email: "aina@example.com", phone: null } });
  });
  it("lowercases and trims email", () => {
    const r = validateSubscribe({ ...ok, email: "  Aina@Example.COM " });
    expect(r.ok && r.value.email).toBe("aina@example.com");
  });
  it("rejects invalid email", () => {
    expect(validateSubscribe({ ...ok, email: "not-an-email" }).ok).toBe(false);
  });
  it("requires email or phone", () => {
    expect(validateSubscribe({ consent: true }).ok).toBe(false);
  });
  it("requires consent", () => {
    expect(validateSubscribe({ email: "a@b.co", consent: false }).ok).toBe(false);
    expect(validateSubscribe({ email: "a@b.co" }).ok).toBe(false);
  });
  it.each(["012-3456789", "0123456789", "+60123456789", "60123456789", "011-23456789"])(
    "normalises Malaysian mobile %s to E.164",
    (phone) => {
      const r = validateSubscribe({ phone, consent: true });
      expect(r.ok && r.value.phone).toMatch(/^\+601\d{8,9}$/);
    },
  );
  it.each(["12345", "0212345678", "+65 9123 4567", "abc"])("rejects non-MY-mobile %s", (phone) => {
    expect(validateSubscribe({ phone, consent: true }).ok).toBe(false);
  });
  it("flags honeypot submissions as bots without erroring", () => {
    const r = validateSubscribe({ ...ok, website: "http://spam.example" });
    expect(r).toMatchObject({ ok: true, bot: true });
  });
  it("rejects non-object input", () => {
    expect(validateSubscribe(null).ok).toBe(false);
    expect(validateSubscribe("x").ok).toBe(false);
  });
});
