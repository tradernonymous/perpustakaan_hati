import { describe, expect, it } from "vitest";
import { generateWorkbook, type WorkbookInput } from "@/src/games/workbook";

describe("Bespoke workbook generator", () => {
  it("generates supplement for dating + anxious", () => {
    const w = generateWorkbook({ status: "dating", style: "anxious" });
    expect(w.title).toContain("Dating");
    expect(w.sections.length).toBeGreaterThan(0);
    expect(w.sections[0].body.length).toBeGreaterThan(0);
  });
  it("generates for married + avoidant", () => {
    const w = generateWorkbook({ status: "married", style: "avoidant" });
    expect(w.title).toContain("Kahwin");
  });
  it("generates for recovering + secure", () => {
    const w = generateWorkbook({ status: "recovering", style: "secure" });
    expect(w.title).toContain("Pulih");
  });
  it("engaged variant works", () => {
    const w = generateWorkbook({ status: "engaged", style: "anxious" });
    expect(w.title).toContain("Bertunang");
  });
});
