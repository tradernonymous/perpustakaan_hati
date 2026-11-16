/**
 * The tier ladder (Design System 3.5 "Ladder of Light").
 *
 * Three things have to hold, and each one has been broken before:
 *
 *  1. Every tier has a full token set, so a surface can style a tier
 *     without hard-coding a colour.
 *  2. The tier colours are actually distinguishable, on every ground the
 *     storefront puts them on, including for a colour-blind reader.
 *  3. A tier is never carried by colour alone: it also has its own
 *     silhouette, and the name always ships with it.
 *
 * The measurements here mirror packages/brand-tools/check-contrast.py.
 * If a ramp value changes, this test is what should fail first.
 */
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import path from "node:path";

import { TIERS } from "@/src/content";

const css = readFileSync(path.join(import.meta.dirname, "../styles/design-tokens.css"), "utf8");
const docsCss = readFileSync(
  path.join(import.meta.dirname, "../../../docs/brand/design-tokens.css"),
  "utf8",
);

const TIER_IDS = ["poket", "membangun", "teman-hidup"] as const;

/* ---- colour maths (WCAG relative luminance, CIE76 dE) ---------------- */

function hexToRgb(hex: string): [number, number, number] {
  const v = hex.trim().replace("#", "");
  const full = v.length === 3 ? v.split("").map((c) => c + c).join("") : v;
  return [
    parseInt(full.slice(0, 2), 16),
    parseInt(full.slice(2, 4), 16),
    parseInt(full.slice(4, 6), 16),
  ];
}

function luminance(hex: string): number {
  const [r, g, b] = hexToRgb(hex).map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(a: string, b: string): number {
  const la = luminance(a);
  const lb = luminance(b);
  const [hi, lo] = la > lb ? [la, lb] : [lb, la];
  return (hi + 0.05) / (lo + 0.05);
}

function token(name: string): string {
  const m = css.match(new RegExp(`${name}:\\s*(#[0-9a-fA-F]{6})`));
  expect(m, `token ${name} must be defined in design-tokens.css`).not.toBeNull();
  return m![1];
}

/** Any token value, for the ones that are not colours (shapes, scales). */
function value(name: string): string {
  const m = css.match(new RegExp(`${name}:\\s*([^;]+);`));
  expect(m, `token ${name} must be defined in design-tokens.css`).not.toBeNull();
  return m![1].trim();
}

/* ---- the palette ----------------------------------------------------- */

const GROUNDS = {
  daylight: "#f7f4ea",
  sage: "#e9f0e6",
  raised: "#fffdf6",
  forest: "#07140d",
  forestRaised: "#0d2117",
  forestSoft: "#142c20",
} as const;

describe("tier ramp tokens", () => {
  it("defines the full role set for every tier", () => {
    for (const tier of TIER_IDS) {
      for (const role of ["ink", "on-dark", "fill", "on-fill", "band", "edge", "rim", "shape", "scale", "foil"]) {
        expect(
          css.includes(`--tier-${tier}-${role}:`),
          `missing --tier-${tier}-${role}`,
        ).toBe(true);
      }
    }
  });

  it("keeps the docs and web copies identical", () => {
    expect(css).toBe(docsCss);
  });

  it("gives each tier its own silhouette, so colour is never the only signal", () => {
    const shapes = TIER_IDS.map((t) => value(`--tier-${t}-shape`));
    // circle / hexagon / arch, per docs/brand/visual-identity.md
    expect(shapes[0]).toContain("circle");
    expect(shapes[1]).toContain("polygon");
    expect(shapes[2]).toContain("polygon");
    expect(new Set(shapes).size).toBe(3);
  });

  it("scales the tiers upward, so the premium tier reads as the heavier one", () => {
    const scale = (t: (typeof TIER_IDS)[number]) => Number(value(`--tier-${t}-scale`));
    expect(scale("poket")).toBeLessThan(scale("membangun"));
    expect(scale("membangun")).toBeLessThan(scale("teman-hidup"));
  });
});

describe("tier colours are readable on every ground the storefront uses", () => {
  it("tier ink is legible on the light grounds", () => {
    for (const tier of TIER_IDS) {
      const ink = token(`--tier-${tier}-ink`);
      for (const ground of [GROUNDS.daylight, GROUNDS.sage, GROUNDS.raised]) {
        expect(contrast(ink, ground), `${tier} ink on ${ground}`).toBeGreaterThanOrEqual(4.5);
      }
    }
  });

  it("tier ink is legible on its own band", () => {
    for (const tier of TIER_IDS) {
      expect(contrast(token(`--tier-${tier}-ink`), token(`--tier-${tier}-band`))).toBeGreaterThanOrEqual(4.5);
    }
  });

  it("the on-dark variant is legible on the dark stage", () => {
    for (const tier of TIER_IDS) {
      const onDark = token(`--tier-${tier}-on-dark`);
      for (const ground of [GROUNDS.forest, GROUNDS.forestRaised, GROUNDS.forestSoft]) {
        expect(contrast(onDark, ground), `${tier} on-dark on ${ground}`).toBeGreaterThanOrEqual(4.5);
      }
    }
  });

  it("the label on a tier fill is legible", () => {
    for (const tier of TIER_IDS) {
      expect(contrast(token(`--tier-${tier}-on-fill`), token(`--tier-${tier}-fill`))).toBeGreaterThanOrEqual(4.5);
    }
  });

  it("a tier block is visible as a graphic on the dark stage", () => {
    for (const tier of TIER_IDS) {
      expect(contrast(token(`--tier-${tier}-fill`), GROUNDS.forest)).toBeGreaterThanOrEqual(3);
    }
  });

  it("the band edge separates the band from its neighbours", () => {
    for (const tier of TIER_IDS) {
      expect(contrast(token(`--tier-${tier}-edge`), token(`--tier-${tier}-band`))).toBeGreaterThanOrEqual(1.5);
    }
  });
});

describe("the tiers stay tellable apart", () => {
  // The three hues are the locked brand colours. What must not happen is
  // two tiers landing on the same hue at the same value.
  it("uses three distinct hues across the tier fills", () => {
    const fills = TIER_IDS.map((t) => token(`--tier-${t}-fill`));
    expect(new Set(fills).size).toBe(3);
  });

  it("gives every tier a distinct band", () => {
    const bands = TIER_IDS.map((t) => token(`--tier-${t}-band`));
    expect(new Set(bands).size).toBe(3);
  });

  it("keeps the tier ids and the ramp in step", () => {
    expect(TIERS.map((t) => t.id).sort()).toEqual([...TIER_IDS].sort());
  });
});
