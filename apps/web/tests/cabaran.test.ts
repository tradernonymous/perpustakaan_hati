import { describe, expect, it } from "vitest";
import { CABARAN_DAYS, cabaranPrompt, CABARAN_TITLE } from "@/src/games/cabaran";

describe("7 Hari Cabaran Pulih Hati", () => {
  it("has 7 days", () => {
    expect(CABARAN_DAYS).toHaveLength(7);
  });
  it("title is exact", () => {
    expect(CABARAN_TITLE).toBe("7 Hari Cabaran Pulih Hati");
  });
  it("each day has a prompt", () => {
    for (const d of CABARAN_DAYS) {
      expect(d.prompt.length).toBeGreaterThan(0);
      expect(d.day).toBeGreaterThanOrEqual(1);
    }
  });
  it("cabaranPrompt returns correct day", () => {
    expect(cabaranPrompt(1).day).toBe(1);
    expect(cabaranPrompt(7).day).toBe(7);
  });
  it("cabaranPrompt clamps", () => {
    expect(cabaranPrompt(0).day).toBe(1);
    expect(cabaranPrompt(99).day).toBe(7);
  });
});
