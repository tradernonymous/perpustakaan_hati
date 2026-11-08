import { readFileSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { BrandMark } from "@/components/BrandMark";
import { EbookDeck } from "@/components/EbookDeck";
import { Hero } from "@/components/Hero";
import { HeroBook } from "@/components/HeroBook";
import { ProductCover } from "@/components/ProductCover";
import { SafetyFooter } from "@/components/SafetyFooter";
import { SectionOrnament } from "@/components/SectionOrnament";
import { SiteHeader } from "@/components/SiteHeader";
import Home from "@/app/page";

const publicBrand = (f: string) => readFileSync(path.join(__dirname, "../public/brand", f), "utf8");

describe("3.2 Daylight Grove hero", () => {
  it("typesets the wordmark as live text so it holds on the ivory ground", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toMatch(/<h1[^>]*>[\s\S]*Perpustakaan[\s\S]*HATI[\s\S]*<\/h1>/);
    expect(html).not.toContain("lockup-hero.svg");
  });
  it("keeps the byline and tagline as real text below the mark", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain("ph-kicker");
    expect(html).toContain("oleh @rahimam");
    expect(html).toContain("Karya untuk jiwa yang pernah terluka");
  });
  it("the cinematic lockup stays in the system for covers and posters", () => {
    const svg = publicBrand("lockup-hero.svg");
    expect(svg).not.toContain('fill="#07140d"');
    expect(svg).toContain('viewBox="300 80 1000 780"');
    expect(svg).toContain('aria-label="Perpustakaan Hati"');
    expect(svg).toContain("phl-bevel"); // lit 3D bevel survives
  });
});

describe("original book-heart emblem", () => {
  it("BrandMark wraps the real emblem in the animated glow, orbit and twinkle", () => {
    const html = renderToStaticMarkup(<BrandMark size={48} />);
    expect(html).toContain("/brand/animated/emblem-book-heart.svg");
    expect(html).toContain("ph-mark-glow");
    expect(html).toContain("ph-mark-orbit");
  });
  it("header shows the emblem at 48px, the brand minimum for its detail", () => {
    const html = renderToStaticMarkup(<SiteHeader />);
    expect(html).toContain("/brand/animated/emblem-book-heart.svg");
    expect(html).toContain('width="48"');
  });
  it("the 3D book cover carries the emblem and the Edisi Poket seal", () => {
    const html = renderToStaticMarkup(<HeroBook name="Edisi Poket" />);
    expect(html).toContain("/brand/animated/emblem-book-heart.svg");
    expect(html).toContain("/brand/animated/seal-edisi-poket.svg");
  });
  it("footer signs off with the emblem", () => {
    expect(renderToStaticMarkup(<SafetyFooter />)).toContain("/brand/emblem-book-heart.svg");
  });
});

describe("design-system cover, seals and ribbon on the editions", () => {
  it("placeholder cover is a gilt-framed brand cover, still clearly a placeholder", () => {
    const html = renderToStaticMarkup(<ProductCover name="Edisi Membangun" src={null} seal="/brand/seal-edisi-membangun.svg" />);
    expect(html).toContain("ph-cover-frame");
    expect(html).toContain("/brand/emblem-book-heart.svg");
    expect(html).toContain("/brand/seal-edisi-membangun.svg");
    expect(html).toContain("Kulit buku akan datang");
    expect(html).not.toContain("<img");
  });
  it("every deck slide shows its tier seal and a ribbon with the edition name", () => {
    const html = renderToStaticMarkup(<EbookDeck />);
    for (const f of ["seal-edisi-poket.svg", "seal-edisi-membangun.svg", "seal-teman-hidup.svg"]) {
      expect(html).toContain(`/brand/animated/${f}`);
    }
    expect(html.match(/ph-ribbon/g)?.length).toBeGreaterThanOrEqual(3);
  });
});

describe("gilt section ornaments", () => {
  it("renders the lockup's flanked diamond rule as decoration only", () => {
    const html = renderToStaticMarkup(<SectionOrnament />);
    expect(html).toContain("ph-ornament");
    expect(html).toContain('aria-hidden="true"');
  });
  it("every homepage section title carries the ornament", () => {
    const html = renderToStaticMarkup(<Home />);
    expect(html.match(/ph-ornament/g)?.length).toBeGreaterThanOrEqual(6);
  });
});

describe("design tokens stay in sync and valid", () => {
  const web = readFileSync(path.join(__dirname, "../styles/design-tokens.css"), "utf8");
  const docs = readFileSync(path.join(__dirname, "../../../docs/brand/design-tokens.css"), "utf8");
  it("the web copy is an exact copy of docs/brand/design-tokens.css", () => {
    expect(web).toBe(docs);
  });
  it("ember variables live inside :root, not stranded after the last rule", () => {
    const tail = web.slice(web.lastIndexOf("}") + 1);
    expect(tail).not.toMatch(/--[a-z-]+\s*:/);
    const root = web.slice(web.indexOf(":root {"), web.indexOf("\n}", web.indexOf(":root {")));
    expect(root).toContain("--dur-ember:");
  });
});
