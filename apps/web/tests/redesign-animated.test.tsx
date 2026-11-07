import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { BrandMark } from "@/components/BrandMark";
import { EbookDeck } from "@/components/EbookDeck";
import { Reveal } from "@/components/Reveal";
import { Hero } from "@/components/Hero";
import { SiteHeader } from "@/components/SiteHeader";

describe("BrandMark (animated logo)", () => {
  it("renders the brand mark as an svg", () => {
    const html = renderToStaticMarkup(<BrandMark />);
    expect(html).toContain("<svg");
    expect(html).toContain('role="img"');
  });

  it("uses the animated mark treatment for the header", () => {
    const html = renderToStaticMarkup(<BrandMark />);
    expect(html).toContain("ph-mark-glow");
    expect(html).toContain("ph-mark-orbit");
    expect(html).toContain("ph-mark-twinkle");
  });

  it("exposes a size prop that scales the mark", () => {
    const small = renderToStaticMarkup(<BrandMark size={28} />);
    expect(small).toContain('width="28"');
    expect(small).toContain('height="28"');
  });
});

describe("SiteHeader logo", () => {
  it("uses the animated Perpustakaan Hati mark on top left instead of the monogram", () => {
    const html = renderToStaticMarkup(<SiteHeader />);
    expect(html).toContain("ph-mark-glow");
    expect(html).not.toContain("monogram-stamp");
  });
});

describe("Hero motion", () => {
  it("has an animated ember backdrop and a staggered reveal", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain("ph-ember");
    expect(html).toContain("animate-fade-up");
  });
});

describe("Reveal", () => {
  it("wraps children and starts hidden until scrolled into view", () => {
    const html = renderToStaticMarkup(
      <Reveal>
        <p>Kandungan</p>
      </Reveal>
    );
    expect(html).toContain("Kandungan");
    expect(html).toContain("data-revealed");
  });
});

describe("EbookDeck (free ebook preview)", () => {
  it("renders every tier as a slide of the carousel", () => {
    const html = renderToStaticMarkup(<EbookDeck />);
    expect(html).toContain('aria-roledescription="carousel"');
    expect(html).toContain("Edisi Poket");
    expect(html).toContain("Edisi Membangun");
    expect(html).toContain("Teman Hidup");
  });

  it("gives the free tier the opt-in CTA and paid tiers the checkout CTA", () => {
    const html = renderToStaticMarkup(<EbookDeck />);
    expect(html).toContain('href="#percuma"');
    expect(html).toContain('href="/beli/membangun"');
    expect(html).toContain('href="/beli/teman-hidup"');
  });

  it("exposes prev/next navigation and dots", () => {
    const html = renderToStaticMarkup(<EbookDeck />);
    expect(html).toContain("aria-label");
  });
});
