import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const root = join(__dirname, "..");
function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((n) => {
    const p = join(dir, n);
    return statSync(p).isDirectory() ? walk(p) : p.endsWith(".tsx") ? [p] : [];
  });
}
const files = [...walk(join(root, "app")), ...walk(join(root, "components"))].filter((f) => !f.includes("astryx-scratch"));

describe("dark pages and components", () => {
  it("use theme-role classes, never ivory-only ones", () => {
    const bad = /\b(bg-daylight[\w-]*|bg-sage|text-green-900|text-ink-grove|text-muted-grove|border-daylight-edge)\b/;
    const offenders = files.filter((f) => bad.test(readFileSync(f, "utf8")));
    expect(offenders).toEqual([]);
  });
  it("keep the nightlight scope on the body", () => {
    expect(readFileSync(join(root, "app/layout.tsx"), "utf8")).toContain("ph-nightlight");
  });
});
