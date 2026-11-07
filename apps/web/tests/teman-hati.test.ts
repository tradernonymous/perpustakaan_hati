import { describe, expect, it } from "vitest";
import { guardrails, isCrisis, needsCounsellor } from "@/src/games/teman-hati";

describe("Teman Hati companion", () => {
  it("isCrisis detects HEAL keyword", () => {
    expect(isCrisis("aku mahu bunuh diri")).toBe(true);
  });
  it("isCrisis false for normal", () => {
    expect(isCrisis("aku rasa sedih hari ini")).toBe(false);
  });
  it("needsCounsellor flags severe distress", () => {
    expect(needsCounsellor("aku tak boleh berfungsi, dah 3 bulan")).toBe(true);
  });
  it("guardrails lists helplines", () => {
    expect(guardrails).toContain("Talian HEAL 15555");
    expect(guardrails).toContain("Befrienders");
  });
});
