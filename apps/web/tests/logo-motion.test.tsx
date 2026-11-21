import { readFileSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { BrandMark } from "@/components/BrandMark";
import { EbookDeck } from "@/components/EbookDeck";
import { Hero } from "@/components/Hero";
import { HeroBook } from "@/components/HeroBook";
import { HeroGlyphs } from "@/components/HeroGlyphs";
import { ProductCover } from "@/components/ProductCover";
import { StatsStrip } from "@/components/StatsStrip";
import { StickyCta } from "@/components/StickyCta";
import { Ticker } from "@/components/Ticker";
import Home from "@/app/page";

const animated = (f: string) => readFileSync(path.join(__dirname, "../public/brand/animated", f), "utf8");
const LOGOS = ["emblem-book-heart.svg", "lockup-hero.svg", "seal-edisi-poket.svg", "seal-edisi-membangun.svg", "seal-teman-hidup.svg"];

describe("animated logo files (build-animated-logos.py)", () => {
  it.each(LOGOS)("%s draws the heart on, traces the ruby line and honours reduced motion", (f) => {
    const svg = animated(f);
    expect(svg.match(/class="phx-draw"/g)).toHaveLength(8);
    expect(svg.match(/class="phx-trace"/g)).toHaveLength(1);
    expect(svg).toContain('pathLength="1"');
    expect(svg).toContain("prefers-reduced-motion: reduce");
    expect(svg).toContain("backwards"); // ends on the original artwork
  });
  it("lockup lifts the HATI face out of its extrusion and sweeps one sheen", () => {
    const svg = animated("lockup-hero.svg");
    expect(svg).toContain('class="phx-lift"');
    expect(svg).toContain('class="phx-depth"');
    expect(svg).toContain('class="phx-sheen"');
    expect(svg).not.toMatch(/phx-sheen[^}]*infinite/); // brand rule: sheen never loops
  });
  it("seals turn their gilt ring", () => {
    for (const f of LOGOS.filter((n) => n.startsWith("seal-"))) expect(animated(f)).toContain('class="phx-turn"');
  });
});

describe("animated logos on the site", () => {
  it("sets the compact headline on the daylight stage", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain("ph-day-stage");
    expect(html).toContain("Bacaan kecil.");
    expect(html).not.toContain("ph-logo-lockup");
  });
  it("the header animates the emblem and the 3D book uses the exported cover", () => {
    expect(renderToStaticMarkup(<BrandMark />)).toContain("/brand/animated/emblem-book-heart.svg");
    expect(renderToStaticMarkup(<HeroBook />)).toContain("/ebooks/cover-poket.png");
  });
  it("seals are animated, 3D coins, and at least the 96px brand minimum", () => {
    const cover = renderToStaticMarkup(<ProductCover name="Teman Hidup" src={null} seal="/brand/animated/seal-teman-hidup.svg" />);
    expect(cover).toContain("ph-coin");
    expect(cover).toContain("h-24 w-24");
  });
});

describe("website_sam ports", () => {
  it("coverflow covers get a gilt spine, side blur and the gold border beam on the active one", () => {
    const html = renderToStaticMarkup(<EbookDeck />);
    expect(html.match(/ph-spine/g)?.length).toBe(3);
    expect(html).toContain("ph-beam");
    expect(html).toContain("blur(");
    expect(html).toContain("/ebooks/cover-membangun.png");
  });
  it("stats strip counts up to real numbers from the editions, rendered final for no-JS", () => {
    const html = renderToStaticMarkup(<StatsStrip />);
    for (const n of [">7<", ">30<", ">60<", ">12<"]) expect(html).toContain(n);
    expect(html).toContain("ph-stats");
  });
  it("ticker loops its items with the duplicate hidden from screen readers", () => {
    const html = renderToStaticMarkup(<Ticker />);
    expect(html).toContain("ph-ticker");
    expect(html).toContain('aria-hidden="true"');
    expect(html).toContain("Kad Refleksi");
  });
  it("sticky CTA is marked to step aside while the opt-in form is on screen", () => {
    expect(renderToStaticMarkup(<StickyCta />)).toContain("data-sticky-cta");
  });
  it("glyphs carry a parallax depth each", () => {
    expect(renderToStaticMarkup(<HeroGlyphs />).match(/--depth:/g)?.length).toBeGreaterThanOrEqual(6);
  });
  it("homepage wires stats, ticker, cursor spotlight cards, ink-in titles and page-in chapters", () => {
    const html = renderToStaticMarkup(<Home />);
    expect(html).toContain("ph-stats");
    expect(html).toContain("ph-ticker");
    expect(html).toContain("ph-lux");
    expect(html).toContain("ph-ink-in");
    expect(html).toContain("ph-page-in");
  });
  it("hero carries the Sam-style motion set: glyphs, ring, CTA sheen and 3D page turn", () => {
    const html = renderToStaticMarkup(<Home />);
    expect(html).toContain("ph-glyphs");
    const heroCss = readFileSync(path.join(__dirname, "../components/HeroAtmosphere.module.css"), "utf8");
    expect(heroCss).toContain("@keyframes spin-ring");
    const tokens = readFileSync(path.join(__dirname, "../styles/design-tokens.css"), "utf8");
    expect(tokens).toContain("@keyframes ph-cta-sheen");
    const flipCss = readFileSync(path.join(__dirname, "../components/TipsFlipbook.module.css"), "utf8");
    expect(flipCss).toContain("rotateX(6deg)");
  });
});
