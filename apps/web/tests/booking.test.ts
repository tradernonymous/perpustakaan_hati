import { describe, expect, it } from "vitest";
import { createBrief, quoteForType, TIERS } from "@/src/games/booking";

describe("Counselling booking", () => {
  it("quoteForType returns RM150-350 range", () => {
    const q = quoteForType("clarity");
    expect(q).toBeGreaterThanOrEqual(15000);
    expect(q).toBeLessThanOrEqual(35000);
  });
  it("createBrief compiles summary", () => {
    const b = createBrief({ name: "Aina", quiz: "anxious", books: ["membangun"], intake: "tak boleh tidur" });
    expect(b.summary).toContain("Aina");
    expect(b.summary).toContain("anxious");
    expect(b.summary).toContain("membangun");
  });
  it("TIERS includes clarity and couples", () => {
    expect(TIERS).toContain("clarity");
    expect(TIERS).toContain("couples");
  });
});
