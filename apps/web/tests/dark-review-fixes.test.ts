import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const root = join(__dirname, "..");
const css = readFileSync(join(root, "styles/design-tokens.css"), "utf8");
const tw = readFileSync(join(root, "tailwind.config.js"), "utf8");
const src = (p: string) => readFileSync(join(root, p), "utf8");
function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((n) => {
    const p = join(dir, n);
    return statSync(p).isDirectory() ? walk(p) : p.endsWith(".tsx") ? [p] : [];
  });
}
const files = [...walk(join(root, "app")), ...walk(join(root, "components"))];

describe("review fixes: error text on dark", () => {
  it("never uses the dark burgundy as text; errors use the fg-danger role", () => {
    const offenders = files.filter((f) => /\btext-burgundy(?!-)\b/.test(readFileSync(f, "utf8")));
    expect(offenders).toEqual([]);
    expect(tw).toContain("danger: 'var(--text-danger)'");
  });
  it("defines --text-danger in both theme scopes at readable values", () => {
    expect(css).toMatch(/\.ph-nightlight,\s*\[data-theme="nightlight"\]\s*\{[\s\S]*?--text-danger:\s*var\(--burgundy-text-dark\)/);
    expect(css).toMatch(/\.ph-daylight\s*\{[\s\S]*?--text-danger:\s*var\(--burgundy-text-light\)/);
  });
});

describe("review fixes: dark scope must not leak into the ivory admin", () => {
  it("excludes .ph-daylight descendants from the nightlight form and heading rules", () => {
    for (const sel of [".ph-nightlight :is(input, textarea, select)", ".ph-nightlight :not(.ph-daylight *)::placeholder", ".ph-nightlight :is(.ph-title, .ph-hero)", ".ph-nightlight [data-tier]"]) {
      const line = css.split("\n").find((l) => l.startsWith(sel));
      expect(line, sel).toBeDefined();
      expect(line).toContain(":not(.ph-daylight *)");
    }
  });
});

describe("review fixes: phone header and sticky bar", () => {
  it("makes the header opaque on phones even inside the nightlight scope", () => {
    expect(css).toMatch(/@media \(max-width: 767px\)\s*\{[\s\S]*?\.ph-nightlight \.ph-header\s*\{[^}]*background:\s*var\(--surface-base\)/);
  });
  it("drops the backdrop blur from the sticky CTA bar", () => {
    expect(src("components/StickyCta.tsx")).not.toContain("backdrop-blur");
  });
});

describe("review fixes: progress fills", () => {
  it("use a light green that clears 3:1 on the dark track", () => {
    expect(src("components/CerminPasangan.tsx")).not.toMatch(/bg-green-700/);
    expect(src("components/OrderStatus.tsx")).not.toMatch(/bg-green-700/);
  });
});
