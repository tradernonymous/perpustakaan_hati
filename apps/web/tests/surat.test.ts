import { describe, expect, it } from "vitest";
import { anonymize, acceptsSurat } from "@/src/games/surat";

describe("Surat Hati", () => {
  it("anonymize strips names", () => {
    expect(anonymize("Aina", "ada luahan")).not.toContain("Aina");
  });
  it("anonymize keeps dilemma", () => {
    expect(anonymize("Aina", "dia tak balas mesej")).toContain("tak balas");
  });
  it("acceptsSurat requires dilemma", () => {
    expect(acceptsSurat({ dilemma: "ada" })).toBe(true);
    expect(acceptsSurat({ dilemma: "" })).toBe(false);
  });
});
