import { describe, expect, it } from "vitest";
import { toCsv } from "@/src/server/csv";

describe("toCsv", () => {
  it("writes a header and rows", () => {
    expect(toCsv(["a", "b"], [["1", "2"]])).toBe("a,b\r\n1,2\r\n");
  });
  it("quotes commas, quotes and newlines", () => {
    expect(toCsv(["a"], [['x,"y"\nz']])).toBe('a\r\n"x,""y""\nz"\r\n');
  });
  it("renders null as empty", () => {
    expect(toCsv(["a", "b"], [[null, "q"]])).toBe("a,b\r\n,q\r\n");
  });
  it("neutralises spreadsheet formulas", () => {
    expect(toCsv(["a"], [["=SUM(A1)"], ["+60123"], ["@x"], ["-1"]])).toBe("a\r\n'=SUM(A1)\r\n'+60123\r\n'@x\r\n'-1\r\n");
  });
});
