import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const root = join(__dirname, "..");
const layout = readFileSync(join(root, "app/layout.tsx"), "utf8");
const css = readFileSync(join(root, "styles/design-tokens.css"), "utf8");
const brandCss = readFileSync(join(root, "../../docs/brand/design-tokens.css"), "utf8");

describe("Design System 3.7 dark default", () => {
  it("puts the nightlight scope on the body", () => {
    expect(layout).toMatch(/className="ph-nightlight[ "]/);
  });
  it("uses a dark ground as themeColor", () => {
    expect(layout).toMatch(/themeColor: "#0[0-9a-f]{5}"/);
  });
  it("bumps the system version to 3.7.0", () => {
    expect(css).toContain("--ph-system-version: '4.1.0'");
    expect(brandCss).toContain("--ph-system-version: '4.1.0'");
  });
  it("defines the dark page tokens and section classes", () => {
    for (const t of ["--ph-glow-green", "--ph-glow-gold", "--ph-hairline-dark", ".ph-dark-section", ".ph-dark-section-raised"]) {
      expect(css).toContain(t);
    }
  });
});

describe("tiers on the dark stage", () => {
  it("re-points the tier ink at the on-dark value inside the nightlight scope", () => {
    expect(css).toMatch(/\.ph-nightlight \[data-tier\][\s\S]*?--tier-ink:\s*var\(--tier-on-dark\)/);
  });
  it("gives the featured compare column a dark tint, not the ivory wash", () => {
    expect(css).toContain("--ph-featured-col: rgb(201 168 106 / 0.10)");
  });
});
