import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

/*
 * The brand bridge must stay a pointer layer: every Astryx theme variable we
 * set resolves to a brand token, never to a hand-picked hex. These tests read
 * the two stylesheets as text so a stray hex or a renamed token fails here
 * instead of silently drifting the palette.
 */
const root = process.cwd();
const bridge = readFileSync(path.join(root, "src/astryx/astryx-brand.css"), "utf8");
const tokens = readFileSync(path.join(root, "styles/design-tokens.css"), "utf8");

/** Decode the bridge's `var(--name)` references, ignoring fallbacks. */
function bridgeRefs(): string[] {
  return [...bridge.matchAll(/var\((--[a-z0-9-]+)/gi)].map((m) => m[1]);
}

describe("astryx brand bridge", () => {
  it("is scoped to the stone theme attribute", () => {
    expect(bridge).toContain('[data-astryx-theme="stone"]');
  });

  it("every referenced brand token exists in design-tokens.css", () => {
    const defined = new Set([...tokens.matchAll(/(--[a-z0-9-]+)\s*:/gi)].map((m) => m[1]));
    const missing = [...new Set(bridgeRefs())].filter((name) => !defined.has(name));
    expect(missing).toEqual([]);
  });

  it("introduces no colour of its own", () => {
    // Strip comments, then assert no hex colour literal survives.
    const code = bridge.replace(/\/\*[\s\S]*?\*\//g, "");
    expect(code).not.toMatch(/#[0-9a-f]{3,8}\b/i);
  });

  it("points the accent at green, not the gold ornament colour", () => {
    expect(bridge).toMatch(/--color-accent:\s*var\(--green-600\)/);
    expect(bridge).toMatch(/--color-success:\s*var\(--green-700\)/);
  });

  it("keeps the brand type faces", () => {
    expect(bridge).toMatch(/--font-family-heading:\s*"Fraunces",\s*Georgia,\s*serif/);
    expect(bridge).toMatch(/--font-family-body:\s*"Inter",\s*system-ui,\s*sans-serif/);
  });

  it("keeps status errors on the burgundy already in the system", () => {
    expect(bridge).toMatch(/--color-error:\s*var\(--burgundy\)/);
  });
});