import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

/*
 * Daylight is the only ground the site renders, so every semantic pair the
 * components use must clear WCAG AA there: 4.5:1 for body text, 3:1 for
 * borders that carry meaning. These are measured, not asserted by vibes.
 */
// Resolve relative to this file: vitest may run from the repo root, not apps/web.
const css = readFileSync(path.join(import.meta.dirname, "../styles/design-tokens.css"), "utf8");

/** Resolve `--name: value` pairs, following one level of var() indirection. */
function tokens(): Record<string, string> {
  const raw: Record<string, string> = {};
  for (const m of css.matchAll(/(--[a-z0-9-]+)\s*:\s*([^;]+);/gi)) raw[m[1]] = m[2].trim();
  const resolved: Record<string, string> = {};
  for (const [k, v] of Object.entries(raw)) {
    const ref = v.match(/^var\((--[a-z0-9-]+)\)$/i);
    resolved[k] = ref ? (raw[ref[1]] ?? v) : v;
  }
  return resolved;
}

function luminance(hex: string): number {
  const h = hex.replace("#", "");
  const full = h.length === 3 ? h.split("").map((c) => c + c).join("") : h;
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(full.slice(i, i + 2), 16) / 255);
  const lin = (c: number) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

function contrast(a: string, b: string): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

describe("daylight contrast", () => {
  const t = tokens();
  const ground = t["--daylight"];
  const raised = t["--daylight-raised"];
  const pairs: Array<[string, string, string, number]> = [
    ["primary text", t["--ink-grove"], ground, 4.5],
    ["primary text on cards", t["--ink-grove"], raised, 4.5],
    ["muted text", t["--muted-grove"], ground, 4.5],
    ["gold label", t["--gold-ink"], ground, 4.5],
    ["green heading", t["--green-700"], ground, 4.5],
    ["green heading on cards", t["--green-900"], raised, 4.5],
    ["error text", t["--burgundy"], ground, 4.5],
    ["hairline vs ground", t["--daylight-edge"], ground, 1.2],
  ];

  for (const [name, fg, bg, min] of pairs) {
    it(`${name} ≥ ${min}:1`, () => {
      expect(fg, `${name} must resolve to a hex`).toMatch(/^#[0-9a-f]{3,8}$/i);
      expect(contrast(fg, bg)).toBeGreaterThanOrEqual(min);
    });
  }
});

describe("theme scope", () => {
  it("keeps a daylight semantic layer for every surface the components use", () => {
    const scope = css.slice(css.indexOf(".ph-daylight {"));
    for (const name of ["--surface-base", "--surface-raised", "--text-primary", "--border-default", "--focus-ring"]) {
      expect(scope).toContain(`${name}:`);
    }
  });

  it("does not rename the AJE branch's tokens while adding daylight", () => {
    expect(css).toContain("--aje-gold:");
    expect(css).toContain("--aje-black:");
  });
});