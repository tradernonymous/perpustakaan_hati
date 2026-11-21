import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { ChapterPreview } from "@/components/ChapterPreview";
import { EbookDeck } from "@/components/EbookDeck";
import { Hero } from "@/components/Hero";

const root = join(__dirname, "..");
const css = readFileSync(join(root, "styles/design-tokens.css"), "utf8");
const layout = readFileSync(join(root, "app/layout.tsx"), "utf8");

/** The CSS text of one top-level @keyframes block. */
function keyframes(name: string): string {
  const i = css.indexOf(`@keyframes ${name}`);
  expect(i, name).toBeGreaterThan(-1);
  let depth = 0;
  for (let j = css.indexOf("{", i); j < css.length; j++) {
    if (css[j] === "{") depth++;
    if (css[j] === "}" && --depth === 0) return css.slice(i, j + 1);
  }
  return "";
}

describe("3.8 void ground", () => {
  it("puts the void layer on the body next to nightlight, with a black themeColor", () => {
    expect(layout).toContain('className="ph-nightlight ph-void ph-storefront"');
    expect(layout).toContain('themeColor: "#030604"');
  });
  it("defines a near-black scope that re-points the surface roles", () => {
    expect(css).toContain("--ph-void: #030604");
    expect(css).toMatch(/\.ph-void\s*\{[\s\S]*?--surface-base:\s*var\(--ph-void\)/);
    expect(css).toMatch(/\.ph-void\s*\{[\s\S]*?--surface-raised:\s*var\(--ph-void-raised\)/);
  });
  it("makes the section grounds follow the active theme instead of a fixed green", () => {
    expect(css).toMatch(/\.ph-dark-section\s*\{\s*background-color:\s*var\(--surface-base\)/);
    expect(css).toMatch(/\.ph-dark-section-raised\s*\{\s*background-color:\s*var\(--surface-raised\)/);
  });
  it("draws a glowing hairline at the top of each dark section", () => {
    expect(css).not.toContain("content: none !important");
    expect(css).toMatch(/\.ph-dark-section::before[\s\S]*?background:\s*var\(--ph-hairline-dark\)/);
  });
  it("keeps the phone header opaque inside the void scope", () => {
    expect(css).toMatch(/@media \(max-width: 767px\)\s*\{[\s\S]*?\.ph-void \.ph-header\s*\{[^}]*background:\s*var\(--surface-base\)/);
  });
});

describe("minimal hero motion", () => {
  it("keeps the beam and spotlight out of the new hero", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).not.toContain("ph-hero-fx");
    expect(html).not.toContain("ph-hero-beam");
    expect(html).not.toContain("ph-hero-spot");
    expect(html).not.toContain("ph-glyphs");
  });
  it("renders the compact headline immediately", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain("Bacaan kecil.");
    expect(html).toContain("Ruang untuk pulih.");
    expect(html).not.toContain("hero-rise");
  });
  it("links the secondary action to the editions", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain('href="#edisi"');
    expect(html).toContain("Lihat koleksi");
  });
  it("animates only opacity and transform", () => {
    const body = keyframes("ph-rise");
    expect(body).not.toMatch(/filter|margin|width|height|top:|left:|letter-spacing|background/);
  });
  it("removes the beam CSS entirely", () => {
    expect(css).not.toContain(".ph-hero-fx");
    expect(css).not.toContain("@keyframes ph-beam-in");
    expect(css).not.toContain("@keyframes ph-beam-breathe");
    expect(css).not.toContain(".ph-hero-beam");
    expect(css).not.toContain(".ph-hero-spot");
  });
  it("keeps keyboard focus clear of the sticky header and the mobile action", () => {
    expect(css).toMatch(/:focus-visible\s*\{[\s\S]*?scroll-margin-top:\s*5rem/);
    expect(css).toMatch(/:focus-visible\s*\{[\s\S]*?scroll-margin-bottom:\s*5rem/);
  });
});

describe("3.8 Raycast-style details", () => {
  it("fades section headings from white to muted on the void ground, with a forced-colors fallback", () => {
    expect(css).toMatch(/\.ph-void :is\(\.ph-title\)[^{]*\{[\s\S]*?-webkit-text-fill-color:\s*transparent/);
    expect(css).toMatch(/@media \(forced-colors: active\)[\s\S]*?\.ph-void :is\(\.ph-title\)[\s\S]*?-webkit-text-fill-color:\s*currentColor/);
  });
  it("adds a cursor-lit border ring to spotlight cards, except the opt-in beam card", () => {
    expect(css).toMatch(/\.ph-void \.ph-lux:not\(\.ph-beam\)::before/);
    expect(css).toMatch(/\.ph-void \.ph-lux:not\(\.ph-beam\):hover::before\s*\{\s*opacity:\s*1/);
  });
  it("gives chapter cards and the edition card the cursor spotlight", () => {
    expect(renderToStaticMarkup(<ChapterPreview />)).toMatch(/class="[^"]*ph-chapter-card[^"]*ph-lux|class="[^"]*ph-lux[^"]*ph-chapter-card/);
    expect(renderToStaticMarkup(<EbookDeck />)).toMatch(/class="[^"]*ph-tier-card[^"]*ph-lux|class="[^"]*ph-lux[^"]*ph-tier-card/);
  });
});

describe("3.8 review fixes: css", () => {
  it("scopes the kbd style to the palette and the header hint", () => {
    expect(css).not.toMatch(/^kbd\s*\{/m);
    expect(css).toMatch(/\.ph-palette kbd,\s*\.ph-kbd-hint kbd\s*\{/);
  });
  it("uses the real tap-size token", () => {
    expect(css).not.toContain("var(--tap,");
    expect(css).toContain("var(--tap-min");
  });
  it("prints headings in a solid colour (background clipping is dropped in print)", () => {
    expect(css).toMatch(/@media print\s*\{[\s\S]*?\.ph-void :is\(\.ph-title\)[\s\S]*?-webkit-text-fill-color:\s*currentColor/);
  });
});
