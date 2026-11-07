import { describe, expect, it } from "vitest";
import { NURTURE_DAYS, nurtureMessage } from "@/src/games/nurture";

describe("Nurture sequence", () => {
  it("has 7 days", () => {
    expect(NURTURE_DAYS).toHaveLength(7);
  });
  it("each day has subject and body in BM", () => {
    for (const d of NURTURE_DAYS) {
      expect(d.subject.length).toBeGreaterThan(0);
      expect(d.body.length).toBeGreaterThan(0);
    }
  });
  it("nurtureMessage returns correct day", () => {
    const m = nurtureMessage(1);
    expect(m.subject).toBe(NURTURE_DAYS[0].subject);
  });
  it("nurtureMessage clamps out of range", () => {
    expect(nurtureMessage(99).subject).toBe(NURTURE_DAYS[6].subject);
    expect(nurtureMessage(0).subject).toBe(NURTURE_DAYS[0].subject);
  });
  it("no message contains a real link", () => {
    for (const d of NURTURE_DAYS) {
      expect(d.body).not.toMatch(/https?:\/\/(?!example\.com)/);
    }
  });
});
