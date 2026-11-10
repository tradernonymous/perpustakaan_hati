import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

/*
 * The nightlight scope is opt-in: it may only be reached through an explicit
 * attribute, never through prefers-color-scheme alone, and it may only reuse
 * primitives that already exist. Both are structural, so they are asserted
 * against the stylesheet rather than a rendered page.
 */
const css = readFileSync(path.join(import.meta.dirname, "../styles/design-tokens.css"), "utf8");

function scope(selector: string): string {
  const at = css.indexOf(selector);
  if (at < 0) return "";
  const open = css.indexOf("{", at);
  let depth = 0;
  for (let i = open; i < css.length; i += 1) {
    if (css[i] === "{") depth += 1;
    else if (css[i] === "}") {
      depth -= 1;
      if (depth === 0) return css.slice(open + 1, i);
    }
  }
  return "";
}

describe("nightlight scope", () => {
  const body = scope('.ph-nightlight,\n[data-theme="nightlight"]');

  it("exists and maps the semantic layer", () => {
    expect(body).not.toBe("");
    for (const name of ["--surface-base", "--text-primary", "--border-default", "--focus-ring"]) {
      expect(body).toContain(`${name}:`);
    }
  });

  it("flips the ground to the dark primitive", () => {
    expect(body).toMatch(/--surface-base:\s*var\(--forest-night\)/);
    expect(body).toMatch(/--text-primary:\s*var\(--text-on-dark\)/);
  });

  it("is never triggered by prefers-color-scheme on its own", () => {
    // A media query that applies nightlight without an attribute would flip the
    // storefront for every dark-OS visitor; that stays a brand decision.
    const mediaBlock = css.slice(css.indexOf("@media (prefers-color-scheme"));
    if (css.includes("@media (prefers-color-scheme")) {
      expect(mediaBlock.slice(0, 400)).not.toContain("ph-nightlight");
    }
  });

  it("introduces no new hex inside the scope", () => {
    expect(body).not.toMatch(/#[0-9a-f]{3,8}\b/i);
  });
});

describe("system version", () => {
  it("is bumped to 3.3.0 with the new scope", () => {
    expect(css).toContain("--ph-system-version: '3.3.0'");
  });
});