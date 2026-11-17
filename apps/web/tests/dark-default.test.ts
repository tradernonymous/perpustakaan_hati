import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const root = join(__dirname, "..");
const layout = readFileSync(join(root, "app/layout.tsx"), "utf8");
const css = readFileSync(join(root, "styles/design-tokens.css"), "utf8");
const brandCss = readFileSync(join(root, "../../docs/brand/design-tokens.css"), "utf8");

describe("Design System 3.7 dark default", () => {
  it("puts the nightlight scope on the body", () => {
    expect(layout).toContain('className="ph-nightlight"');
  });
  it("uses the forest-night ground as themeColor", () => {
    expect(layout).toContain('themeColor: "#07140d"');
  });
  it("bumps the system version to 3.7.0", () => {
    expect(css).toContain("--ph-system-version: '3.7.0'");
    expect(brandCss).toContain("--ph-system-version: '3.7.0'");
  });
  it("defines the dark page tokens and section classes", () => {
    for (const t of ["--ph-glow-green", "--ph-glow-gold", "--ph-hairline-dark", ".ph-dark-section", ".ph-dark-section-raised"]) {
      expect(css).toContain(t);
    }
  });
});
