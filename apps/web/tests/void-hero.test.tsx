// @vitest-environment jsdom
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { cleanup, render } from "@testing-library/react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it } from "vitest";
import { ChapterPreview } from "@/components/ChapterPreview";
import { EbookDeck } from "@/components/EbookDeck";
import { Hero } from "@/components/Hero";
import { HeroBeam } from "@/components/HeroBeam";

const root = join(__dirname, "..");
const css = readFileSync(join(root, "styles/design-tokens.css"), "utf8");
const layout = readFileSync(join(root, "app/layout.tsx"), "utf8");
afterEach(cleanup);

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

describe("3.8 hero motion: minimal, compositor-only", () => {

  it("animates only opacity and transform", () => {
    for (const k of ["ph-beam-in", "ph-beam-breathe", "ph-rise"]) {
      const body = keyframes(k);
      expect(body, k).not.toMatch(/filter|margin|width|height|top:|left:|letter-spacing|background/);
    }
  });
  it("stops the breathing loop on phones and shows the spotlight only with a real pointer", () => {
    expect(css).toMatch(/@media \(max-width: 767px\)\s*\{[\s\S]*?\.ph-hero-beam\s*\{[^}]*animation:\s*ph-beam-in[^;]*forwards;/);
    expect(css).toMatch(/\.ph-hero-spot\s*\{[^}]*display:\s*none/);
    expect(css).toMatch(/@media \(hover: hover\)[^{]*\{\s*\.ph-hero-spot\s*\{\s*display:\s*block/);
  });
  it("writes the pointer position onto the fx layer and ignores touch", async () => {
    const ptr = (init: MouseEventInit & { pointerType: string }) => {
      const e = new MouseEvent("pointermove", init);
      Object.defineProperty(e, "pointerType", { value: init.pointerType });
      return e;
    };
    const { container } = render(<HeroBeam />);
    const fx = container.querySelector<HTMLElement>(".ph-hero-fx")!;
    window.dispatchEvent(ptr({ clientX: 10, clientY: 10, pointerType: "touch" }));
    await new Promise((r) => setTimeout(r, 40));
    expect(fx.style.getPropertyValue("--hx")).toBe("");
    window.dispatchEvent(ptr({ clientX: 20, clientY: 30, pointerType: "mouse" }));
    await new Promise((r) => setTimeout(r, 40));
    expect(fx.style.getPropertyValue("--hx")).toMatch(/px$/);
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
  it("hides the spotlight until the pointer has moved once", async () => {
    expect(css).toMatch(/\.ph-hero-spot\s*\{[^}]*opacity:\s*0/);
    expect(css).toMatch(/\.ph-hero-fx\[data-live\] \.ph-hero-spot\s*\{\s*opacity:\s*1/);
    const { container } = render(<HeroBeam />);
    const fx = container.querySelector<HTMLElement>(".ph-hero-fx")!;
    expect(fx.hasAttribute("data-live")).toBe(false);
    const e = new MouseEvent("pointermove", { clientX: 5, clientY: 5 });
    Object.defineProperty(e, "pointerType", { value: "mouse" });
    window.dispatchEvent(e);
    await new Promise((r) => setTimeout(r, 40));
    expect(fx.hasAttribute("data-live")).toBe(true);
  });
});
