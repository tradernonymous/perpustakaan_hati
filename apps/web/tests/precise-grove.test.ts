/**
 * Design System 3.9 "Void Grove" (refinement layer).
 *
 * 3.6 changes no colour, font or asset. What it locks is the machinery:
 * focus, selection, wrapping, numerals, motion roles, elevation and the
 * contrast escape hatches. Each rule below was added because a surface
 * was otherwise free to invent its own value.
 *
 * The measurements mirror packages/brand-tools/check-contrast.py. If a
 * 3.6 value changes, this test should fail first.
 */
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import path from "node:path";

const css = readFileSync(path.join(import.meta.dirname, "../styles/design-tokens.css"), "utf8");
const docsCss = readFileSync(
  path.join(import.meta.dirname, "../../../docs/brand/design-tokens.css"),
  "utf8",
);
const guideline = readFileSync(
  path.join(import.meta.dirname, "../../../docs/brand/doop-guideline.md"),
  "utf8",
);
const webTailwind = readFileSync(path.join(import.meta.dirname, "../tailwind.config.js"), "utf8");
const uiTailwind = readFileSync(
  path.join(import.meta.dirname, "../../../packages/ui/tailwind.config.js"),
  "utf8",
);

function declared(name: string): string | null {
  const m = css.match(new RegExp(`${name}\\s*:\\s*([^;]+);`));
  return m ? m[1].trim() : null;
}

describe("3.6 focus recipe", () => {
  it("uses a 2px ring at a 3:1-safe colour on both grounds", () => {
    expect(declared("--focus-width")).toBe("2px");
    expect(declared("--focus-offset")).toBe("2px");
    expect(declared("--focus-color")).toBe("var(--green-300)");
    expect(declared("--focus-color-light")).toBe("var(--green-800)");
  });

  it("draws the ring with outline so it never overwrites a box-shadow", () => {
    expect(css).toMatch(/:focus-visible\s*\{[\s\S]*?outline:\s*var\(--focus-width\) solid var\(--focus-color\)/);
    expect(css).toMatch(/\.ph-cta:focus-visible\s*\{[\s\S]*?outline-offset:\s*var\(--focus-offset-wide\)/);
  });

  it("points the daylight scope at the light-ground ring colour", () => {
    expect(css).toMatch(/\.ph-daylight\s*\{[\s\S]*?--focus-color:\s*var\(--focus-color-light\)/);
  });
});

describe("3.6 selection, caret and native controls", () => {
  it("replaces the browser blue with the brand green", () => {
    expect(css).toMatch(/::selection\s*\{\s*background:\s*var\(--selection-bg\)/);
    expect(declared("--selection-bg")).toBe("var(--green-800)");
    expect(declared("--selection-fg")).toBe("var(--cream)");
  });

  it("tints the caret and native controls", () => {
    expect(css).toMatch(/body\s*\{[\s\S]*?caret-color:\s*var\(--caret-color\)/);
    expect(css).toMatch(/body\s*\{[\s\S]*?accent-color:\s*var\(--accent-color\)/);
  });
});

describe("3.6 typography and numerals", () => {
  it("balances headings and pretty-wraps paragraphs", () => {
    expect(css).toMatch(/h1,\s*h2,\s*h3,\s*\.ph-title\s*\{\s*text-wrap:\s*balance/);
    expect(css).toMatch(/p,\s*li,[^{]*\{\s*text-wrap:\s*pretty/);
  });

  it("gives stats tabular numerals", () => {
    expect(css).toMatch(/\.ph-stat-num\s*\{[^}]*font-variant-numeric:\s*tabular-nums/);
    expect(css).toMatch(/\.ph-nums\s*\{\s*font-variant-numeric:\s*tabular-nums/);
  });
});

describe("3.6 motion roles", () => {
  it("defines one ease per role", () => {
    expect(declared("--ease-standard")).toBe("cubic-bezier(0.2, 0, 0, 1)");
    expect(declared("--ease-decelerate")).toBe("cubic-bezier(0.05, 0.7, 0.1, 1)");
    expect(declared("--ease-accelerate")).toBe("cubic-bezier(0.3, 0, 0.8, 0.15)");
  });

  it("uses them where the role is clear", () => {
    expect(css).toMatch(/\.ph-card\s*\{[^}]*var\(--ease-standard\)/);
    expect(css).toMatch(/\.ph-sticky-cta\s*\{[^}]*var\(--ease-decelerate\)/);
    expect(css).toMatch(/\.ph-sticky-cta\[data-hidden="true"\][\s\S]{0,220}?--ease-accelerate/);
  });
});

describe("3.6 elevation ladder", () => {
  it("has four steps backed by a shadow tint", () => {
    const shapes = ["1px 2px", "4px 10px -2px", "12px 28px -6px", "28px 60px -12px"];
    for (const n of [1, 2, 3, 4]) {
      expect(declared(`--elevation-${n}`)).toBe(`0 ${shapes[n - 1]} var(--shadow-tint-${n})`);
    }
    expect(declared("--shadow-tint-1")).toBe("rgb(0 0 0 / 0.22)");
  });

  it("lets the daylight scope swap the material, not the shape", () => {
    expect(css).toMatch(/\.ph-daylight\s*\{[\s\S]*?--shadow-tint-1:\s*rgb\(60 45 20 \/ 0\.08\)/);
    expect(css).toMatch(/\.ph-elev-1\s*\{\s*box-shadow:\s*var\(--elevation-1\)/);
  });

  it("mirrors the ladder into both Tailwind configs", () => {
    for (const config of [webTailwind, uiTailwind]) {
      expect(config).toContain("'elev-1': 'var(--elevation-1)'");
      expect(config).toContain("'elev-4': 'var(--elevation-4)'");
      expect(config).toContain("standard: 'cubic-bezier(0.2, 0, 0, 1)'");
      expect(config).toContain("decelerate: 'cubic-bezier(0.05, 0.7, 0.1, 1)'");
      expect(config).toContain("accelerate: 'cubic-bezier(0.3, 0, 0.8, 0.15)'");
    }
  });
});

describe("3.6 escape hatches", () => {
  it("raises contrast through the semantic layer, not the primitives", () => {
    const block = css.match(/@media \(prefers-contrast: more\)\s*\{([\s\S]*?)\n\}/);
    expect(block, "prefers-contrast: more block").toBeTruthy();
    expect(block![1]).toContain("--text-muted:");
    expect(block![1]).not.toContain("--muted-grove:");
    expect(block![1]).not.toContain("--text-muted-on-dark:");
  });

  it("keeps the focus ring visible in forced-colors mode", () => {
    expect(css).toMatch(/@media \(forced-colors: active\)\s*\{[\s\S]*?:focus-visible\s*\{\s*outline:\s*2px solid Highlight/);
  });
});

describe("Design system release bookkeeping", () => {
  it("is the current version in both copies", () => {
    expect(css).toContain("--ph-system-version: '3.9.0'");
    expect(css).toBe(docsCss);
  });

  it("is described in the docs and the Doop guideline", () => {
    const design = readFileSync(path.join(import.meta.dirname, "../../../docs/brand/DESIGN-SYSTEM.md"), "utf8");
    expect(design).toContain('Design System 3.9 "Void Grove"');
    expect(design).toContain('Precise Grove');
    expect(design).toContain("--ph-system-version: '3.9.0'");
    expect(guideline).toContain('Design System 3.9 "Void Grove"');
    expect(guideline).toContain("--focus-color:var(--green-300)");
  });
});